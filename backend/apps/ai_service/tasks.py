"""
异步任务 - AI生成测试用例
- ai_generate_func_case_task: 生成功能测试用例(FuncCase)
- ai_generate_api_case_task:   生成接口自动化用例(Case+CaseSteps+Step)
使用django-q2异步执行，完成后发送站内信
"""
import logging
from django.conf import settings
from django.utils import timezone
from apps.ai_service.graph import run_generation as run_func_case_generation
from apps.ai_service.api_case_graph import run_generation as run_api_case_generation
from apps.ai_service.api_case_saver import save_generated_api_cases
from apps.ai_service.scenario_case_graph import run_generation as run_scenario_case_generation
from apps.ai_service.scenario_case_saver import save_generated_scenario_cases
from apps.ai_service.vectorstore import add_case_to_vectorstore
from apps.tests.models import FuncCase, Tag
from apps.envs.models import Module
from apps.projects.models import Project
from apps.users.models import User
from apps.messages.models import Message
from apps.tests.serializers import FuncCaseSerializer

logger = logging.getLogger('ai_service')


def ai_generate_func_case_task(task_id: str, requirement: str, project_id: int,
                               ai_config_id: int, user_id: int,
                               module_id: int = None, tag_ids: list = None,
                               generate_count: int = 3, include_boundary: bool = True,
                               include_exception: bool = True, include_performance: bool = False,
                               message_id: int = None):
    """
    异步任务: AI生成功能测试用例
    1. 调用LangGraph工作流生成用例
    2. 将有效用例写入数据库
    3. 添加到向量库
    4. 更新站内信状态为已完成
    """
    from django.core.cache import cache

    logger.info(f"[AI任务 {task_id}] 开始执行 - 项目{project_id}, 用户{user_id}, 消息ID={message_id}")

    # 更新任务状态
    cache.set(f'ai_task_{task_id}', {
        'status': 'running',
        'progress': '正在分析需求...',
    }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

    try:
        # 执行生成
        cache.set(f'ai_task_{task_id}', {
            'status': 'running',
            'progress': '正在生成用例...',
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        result = run_func_case_generation(
            requirement=requirement,
            project_id=project_id,
            ai_config_id=ai_config_id,
            module_id=module_id,
            tag_ids=tag_ids or [],
            generate_count=generate_count,
            include_boundary=include_boundary,
            include_exception=include_exception,
            include_performance=include_performance,
        ) or {}

        if not result.get('success'):
            cache.set(f'ai_task_{task_id}', {
                'status': 'failed',
                'progress': '生成失败',
                'error': result.get('error', '未知错误'),
            }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
            _update_message(message_id, user_id, project_id, 0, 0, [], result.get('error', ''), task_id)
            return

        cache.set(f'ai_task_{task_id}', {
            'status': 'running',
            'progress': '正在保存用例...',
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        # 写入数据库
        user = User.objects.get(id=user_id)
        project = Project.objects.get(id=project_id)
        saved_cases = []
        failed_count = 0

        # 【健壮性修复】模块解析改为"一次解析 + 显式报错"。
        # 原实现把 _get_default_module() 放在循环内，若项目下无任何模块会抛
        # ValueError 并被 except 吞掉，表现为"生成成功但 0 条落库"，
        # 用户无从得知原因。现改为：模块无效时直接回写失败原因到站内信。
        resolved_module_id = module_id
        if not resolved_module_id:
            try:
                resolved_module_id = _get_default_module(project_id)
            except ValueError as e:
                error_msg = (
                    f"无法保存用例：{e}。请先在该项目下创建「模块管理」中的模块，"
                    f"再重新执行 AI 生成。"
                )
                logger.error(f"[AI任务 {task_id}] {error_msg}")
                cache.set(f'ai_task_{task_id}', {
                    'status': 'failed',
                    'progress': '保存失败：项目下无可用模块',
                    'error': error_msg,
                }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
                _update_message(message_id, user_id, project_id, 0, 0, [], error_msg, task_id)
                return

        for case_data in result.get('cases', []):
            try:
                func_case = FuncCase(
                    name=case_data['name'],
                    project=project,
                    owner=user,
                    module_id=resolved_module_id,
                    setup_condition=case_data.get('setup_condition', ''),
                    case_mark=case_data.get('case_mark', 'AI生成，待人工审核'),
                    step_type=2,
                    step_table=case_data.get('step_table', []),
                    can_autoed=3,
                    auto_status=4,
                    case_status=FuncCase.CaseStatus.DESIGNING,
                    create_by=user,
                    update_by=user,
                )
                func_case.save()

                # 关联标签
                if tag_ids:
                    for tag_id in tag_ids:
                        try:
                            tag = Tag.objects.get(id=tag_id)
                            func_case.tag.add(tag)
                        except Tag.DoesNotExist:
                            pass

                saved_cases.append({
                    'id': func_case.id,
                    'name': func_case.name,
                })

                # 添加到向量库
                add_case_to_vectorstore(
                    project_id=project_id,
                    case_id=func_case.id,
                    case_name=func_case.name,
                    step_text='',
                    step_table=func_case.step_table or [],
                    module_id=resolved_module_id,
                    create_time=str(func_case.create_time) if func_case.create_time else None,
                    create_by_name=func_case.create_by.username if func_case.create_by else None,
                    update_time=str(func_case.update_time) if func_case.update_time else None,
                    update_by_name=func_case.update_by.username if func_case.update_by else None,
                )
            except Exception as e:
                logger.error(f"[AI任务 {task_id}] 保存用例失败: {case_data.get('name', '未知')} - {e}")
                failed_count += 1

        # 更新站内信状态为已完成
        _update_message(
            message_id=message_id,
            user_id=user_id,
            project_id=project_id,
            success_count=len(saved_cases),
            failed_count=failed_count,
            case_names=[c['name'] for c in saved_cases],
            error='',
            task_id=task_id,
            duration=result.get('duration', 0),
        )

        cache.set(f'ai_task_{task_id}', {
            'status': 'success',
            'progress': '生成完成',
            'cases': saved_cases,
            'failed_count': failed_count,
            'duration': result.get('duration', 0),
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        logger.info(f"[AI任务 {task_id}] 完成 - 成功{len(saved_cases)}条, 失败{failed_count}条")

    except Exception as e:
        logger.error(f"[AI任务 {task_id}] 执行异常: {e}", exc_info=True)
        cache.set(f'ai_task_{task_id}', {
            'status': 'failed',
            'progress': '执行异常',
            'error': str(e),
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
        _update_message(message_id, user_id, project_id, 0, 0, [], str(e), task_id)


def _get_default_module(project_id: int) -> int:
    """获取项目默认模块"""
    module = Module.objects.filter(project_id=project_id, is_delete=False).first()
    if module:
        return module.id
    raise ValueError("项目下无可用模块")


def _update_message(message_id: int, user_id: int, project_id: int, success_count: int, failed_count: int,
                    case_names: list, error: str, task_id: str, duration: float = 0):
    """更新站内信状态为已完成/失败"""
    try:
        user = User.objects.get(id=user_id)
        project = Project.objects.get(id=project_id)

        total_count = success_count + failed_count
        if error:
            title = f"AI用例生成失败"
            content = f"项目: {project.name}\n任务ID: {task_id}\n失败原因: {error}"
            task_status = Message.TaskStatus.FAILED
        else:
            title = f"AI用例生成完成"
            case_list_text = "\n".join([f"  {i+1}. {name}" for i, name in enumerate(case_names)])
            content = (
                f"项目: {project.name}\n"
                f"生成成功: {success_count} 条\n"
                f"生成失败: {failed_count} 条\n"
                f"耗时: {duration} 秒\n"
                f"用例列表:\n{case_list_text}"
            )
            task_status = Message.TaskStatus.SUCCESS

        if message_id:
            updated = Message.objects.filter(id=message_id).update(
                title=title,
                content=content,
                task_status=task_status,
                total_count=total_count,
                success_count=success_count,
                failed_count=failed_count,
                fail_reason=error or '',
                # 【AI 用例可见性】带 filter=ai，前端据此清空模块记忆筛选，
                # 直接定位到本次生成的用例，避免用户"看不到已生成用例"。
                related_url='/resource/funcCase?filter=ai',
                is_read=False,
                read_time=None,
                duration=duration,
                update_by=user,
                update_time=timezone.now(),
            )
            if updated:
                logger.info(f"[AI任务 {task_id}] 站内信 {message_id} 已更新为 {title}, task_status={task_status}")
                _push_message(message_id)
            else:
                logger.warning(f"[AI任务 {task_id}] 站内信 {message_id} 未找到，未更新")
        else:
            Message.objects.create(
                user=user,
                project=project,
                title=title,
                content=content,
                message_type=Message.MessageType.TASK,
                task_status=task_status,
                is_read=False,
                related_url='/resource/funcCase?filter=ai',
                total_count=total_count,
                success_count=success_count,
                failed_count=failed_count,
                fail_reason=error or '',
                duration=duration,
                create_by=user,
                update_by=user,
            )
            logger.info(f"[AI任务 {task_id}] 站内信已发送给用户 {user.username}")
    except Exception as e:
        logger.error(f"[AI任务 {task_id}] 更新站内信失败: {e}")


# ===== 接口自动化用例生成任务 =====
def ai_generate_api_case_task(task_id: str, api_id: int, project_id: int,
                              ai_config_id: int, user_id: int,
                              module_id: int, tag_ids: list = None,
                              generate_count: int = 3, include_boundary: bool = True,
                              include_missing_required: bool = True, include_type_error: bool = False,
                              include_exception_status: bool = True,
                              include_security: bool = False,
                              extra_requirement: str = "", message_id: int = None):
    """
    异步任务: AI生成接口自动化用例
    1. 调用LangGraph工作流生成用例(场景+override+状态码断言)
    2. 调用saver落库(数据驱动模式 or 独立用例模式)
    3. 更新站内信状态为已完成

    与 ai_generate_func_case_task 的差异:
    - 输入是 api_id 而非 requirement
    - 产物是 Case+CaseSteps+Step(结构化接口请求) 而非 FuncCase(文本步骤)
    - 跳过向量库(MVP阶段无接口用例RAG)
    - related_url 指向 /resource/scriptCase 而非 /resource/funcCase
    """
    from django.core.cache import cache

    logger.info(
        f"[AI-API任务 {task_id}] 开始执行 - api={api_id}, 项目{project_id}, "
        f"用户{user_id}, 模块{module_id}, 消息ID={message_id}"
    )

    cache.set(f'ai_task_{task_id}', {
        'status': 'running',
        'progress': '正在加载接口文档...',
    }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

    try:
        # 校验模块存在
        module = Module.objects.get(id=module_id, is_delete=False)

        cache.set(f'ai_task_{task_id}', {
            'status': 'running',
            'progress': '正在生成接口用例...',
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        result = run_api_case_generation(
            api_id=api_id,
            project_id=project_id,
            ai_config_id=ai_config_id,
            module_id=module_id,
            tag_ids=tag_ids or [],
            generate_count=generate_count,
            include_boundary=include_boundary,
            include_missing_required=include_missing_required,
            include_type_error=include_type_error,
            include_exception_status=include_exception_status,
            include_security=include_security,
            extra_requirement=extra_requirement,
        )

        if not result.get('success'):
            cache.set(f'ai_task_{task_id}', {
                'status': 'failed',
                'progress': '生成失败',
                'error': result.get('error', '未知错误'),
            }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
            _update_api_case_message(
                message_id, user_id, project_id, 0, 0, [], result.get('error', ''), task_id, api_id=api_id
            )
            return

        cache.set(f'ai_task_{task_id}', {
            'status': 'running',
            'progress': '正在保存用例...',
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        # 落库
        saved_cases = save_generated_api_cases(
            api_id=api_id,
            generated_cases=result.get('cases', []),
            user_id=user_id,
            project_id=project_id,
            module_id=module_id,
            tag_ids=tag_ids or [],
        )
        failed_count = 0

        _update_api_case_message(
            message_id=message_id,
            user_id=user_id,
            project_id=project_id,
            success_count=len(saved_cases),
            failed_count=failed_count,
            case_names=[c['name'] for c in saved_cases],
            error='',
            task_id=task_id,
            duration=result.get('duration', 0),
            api_id=api_id,
        )

        cache.set(f'ai_task_{task_id}', {
            'status': 'success',
            'progress': '生成完成',
            'cases': saved_cases,
            'failed_count': failed_count,
            'duration': result.get('duration', 0),
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        logger.info(f"[AI-API任务 {task_id}] 完成 - 成功{len(saved_cases)}条")

    except Module.DoesNotExist:
        err = f"模块不存在: module_id={module_id}"
        logger.error(f"[AI-API任务 {task_id}] {err}")
        cache.set(f'ai_task_{task_id}', {
            'status': 'failed', 'progress': '模块不存在', 'error': err,
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
        _update_api_case_message(message_id, user_id, project_id, 0, 0, [], err, task_id, api_id=api_id)
    except Exception as e:
        logger.error(f"[AI-API任务 {task_id}] 执行异常: {e}", exc_info=True)
        cache.set(f'ai_task_{task_id}', {
            'status': 'failed', 'progress': '执行异常', 'error': str(e),
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
        _update_api_case_message(message_id, user_id, project_id, 0, 0, [], str(e), task_id, api_id=api_id)


def _update_api_case_message(message_id: int, user_id: int, project_id: int,
                             success_count: int, failed_count: int,
                             case_names: list, error: str, task_id: str,
                             duration: float = 0, api_id: int = None):
    """更新接口用例生成的站内信

    与 _update_message 的差异:
    - related_url 指向 /resource/apiEdit?id={api_id}&mode=edit (接口编辑详情)
    - 标题和文案区分接口用例
    """
    try:
        user = User.objects.get(id=user_id)
        project = Project.objects.get(id=project_id)

        total_count = success_count + failed_count
        if error:
            title = "AI接口用例生成失败"
            content = (
                f"项目: {project.name}\n"
                f"任务ID: {task_id}\n"
                f"生成成功: {success_count} 条\n"
                f"生成失败: {failed_count} 条\n"
                f"失败原因: {error}"
            )
            task_status = Message.TaskStatus.FAILED
        else:
            title = "AI接口用例生成完成"
            case_list_text = "\n".join(
                [f"  {i+1}. {name}" for i, name in enumerate(case_names)]
            )
            content = (
                f"项目: {project.name}\n"
                f"生成成功: {success_count} 条\n"
                f"生成失败: {failed_count} 条\n"
                f"耗时: {duration} 秒\n"
                f"用例列表:\n{case_list_text}"
            )
            task_status = Message.TaskStatus.SUCCESS

        related_url = f'/resource/apiEdit?id={api_id}&mode=edit&tab=case' if api_id else '/resource/scriptCase'

        if message_id:
            updated = Message.objects.filter(id=message_id).update(
                title=title,
                content=content,
                task_status=task_status,
                total_count=total_count,
                success_count=success_count,
                failed_count=failed_count,
                fail_reason=error or '',
                related_url=related_url,
                is_read=False,
                read_time=None,
                duration=duration,
                update_by=user,
                update_time=timezone.now(),
            )
            if updated:
                logger.info(f"[AI-API任务 {task_id}] 站内信 {message_id} 已更新为 {title}")
                _push_message(message_id)
            else:
                logger.warning(f"[AI-API任务 {task_id}] 站内信 {message_id} 未找到，未更新")
        else:
            Message.objects.create(
                user=user,
                project=project,
                title=title,
                content=content,
                message_type=Message.MessageType.TASK,
                task_status=task_status,
                is_read=False,
                related_url=related_url,
                total_count=total_count,
                success_count=success_count,
                failed_count=failed_count,
                fail_reason=error or '',
                duration=duration,
                create_by=user,
                update_by=user,
            )
            logger.info(f"[AI-API任务 {task_id}] 站内信已发送给用户 {user.username}")
    except Exception as e:
        logger.error(f"[AI-API任务 {task_id}] 更新站内信失败: {e}")


def ai_generate_scenario_case_task(task_id: str, func_case_id: int, project_id: int,
                                   ai_config_id: int, user_id: int, module_id: int,
                                   mode: str, tag_ids: list = None,
                                   generate_count: int = 3,
                                   extra_requirement: str = "",
                                   message_id: int = None):
    """
    异步任务: AI从功能用例生成场景脚本用例

    1. 调用LangGraph工作流生成步骤树(api/web/control节点)
    2. 调用saver递归落库(Case + CaseSteps + Step, 变量引用回填)
    3. 更新站内信状态为已完成

    与 ai_generate_api_case_task 的差异:
    - 输入是 func_case_id(功能用例) 而非 api_id(接口文档)
    - 支持 mode: api(接口自动化) / web_ui(WebUI自动化)
    - 产物是步骤树(含逻辑控制器) + 前置接口造数据
    """
    from django.core.cache import cache

    logger.info(
        f"[AI-SCENE任务 {task_id}] 开始执行 - 功能用例{func_case_id}, 模式{mode}, "
        f"项目{project_id}, 用户{user_id}, 模块{module_id}, 消息ID={message_id}"
    )

    cache.set(f'ai_task_{task_id}', {
        'status': 'running',
        'progress': '正在加载功能用例...',
    }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

    try:
        # 校验模块存在
        module = Module.objects.get(id=module_id, is_delete=False)

        cache.set(f'ai_task_{task_id}', {
            'status': 'running',
            'progress': '正在生成场景脚本...',
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        result = run_scenario_case_generation(
            func_case_id=func_case_id,
            project_id=project_id,
            ai_config_id=ai_config_id,
            module_id=module_id,
            mode=mode,
            tag_ids=tag_ids or [],
            generate_count=generate_count,
            extra_requirement=extra_requirement,
        )

        if not result.get('success'):
            cache.set(f'ai_task_{task_id}', {
                'status': 'failed',
                'progress': '生成失败',
                'error': result.get('error', '未知错误'),
            }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
            _update_scene_case_message(
                message_id, user_id, project_id, 0, 0, [],
                result.get('error', ''), task_id, mode=mode,
            )
            return

        cache.set(f'ai_task_{task_id}', {
            'status': 'running',
            'progress': '正在保存用例...',
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        # 落库
        saved_cases = save_generated_scenario_cases(
            func_case_id=func_case_id,
            generated_cases=result.get('cases', []),
            mode=mode,
            user_id=user_id,
            project_id=project_id,
            module_id=module_id,
            tag_ids=tag_ids or [],
        )
        failed_count = 0

        _update_scene_case_message(
            message_id=message_id,
            user_id=user_id,
            project_id=project_id,
            success_count=len(saved_cases),
            failed_count=failed_count,
            case_names=[c['name'] for c in saved_cases],
            error='',
            task_id=task_id,
            duration=result.get('duration', 0),
            mode=mode,
        )

        cache.set(f'ai_task_{task_id}', {
            'status': 'success',
            'progress': '生成完成',
            'cases': saved_cases,
            'failed_count': failed_count,
            'duration': result.get('duration', 0),
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)

        logger.info(f"[AI-SCENE任务 {task_id}] 完成 - 模式{mode}, 成功{len(saved_cases)}条")

    except Module.DoesNotExist:
        err = f"模块不存在: module_id={module_id}"
        logger.error(f"[AI-SCENE任务 {task_id}] {err}")
        cache.set(f'ai_task_{task_id}', {
            'status': 'failed', 'progress': '模块不存在', 'error': err,
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
        _update_scene_case_message(message_id, user_id, project_id, 0, 0, [], err, task_id, mode=mode)
    except Exception as e:
        logger.error(f"[AI-SCENE任务 {task_id}] 执行异常: {e}", exc_info=True)
        cache.set(f'ai_task_{task_id}', {
            'status': 'failed', 'progress': '执行异常', 'error': str(e),
        }, timeout=settings.AI_TASK_CACHE_TIMEOUT)
        _update_scene_case_message(message_id, user_id, project_id, 0, 0, [], str(e), task_id, mode=mode)


def _update_scene_case_message(message_id: int, user_id: int, project_id: int,
                               success_count: int, failed_count: int,
                               case_names: list, error: str, task_id: str,
                               duration: float = 0, mode: str = 'api'):
    """更新场景脚本生成的站内信"""
    try:
        user = User.objects.get(id=user_id)
        project = Project.objects.get(id=project_id)

        mode_label = '接口' if mode == 'api' else 'WebUI'
        total_count = success_count + failed_count
        if error:
            title = f"AI{mode_label}脚本生成失败"
            content = (
                f"项目: {project.name}\n"
                f"任务ID: {task_id}\n"
                f"生成成功: {success_count} 条\n"
                f"生成失败: {failed_count} 条\n"
                f"失败原因: {error}"
            )
            task_status = Message.TaskStatus.FAILED
        else:
            title = f"AI{mode_label}脚本生成完成"
            case_list_text = "\n".join(
                [f"  {i+1}. {name}" for i, name in enumerate(case_names)]
            )
            content = (
                f"项目: {project.name}\n"
                f"生成成功: {success_count} 条\n"
                f"生成失败: {failed_count} 条\n"
                f"耗时: {duration} 秒\n"
                f"用例列表:\n{case_list_text}"
            )
            task_status = Message.TaskStatus.SUCCESS

        related_url = '/resource/scriptCase'

        if message_id:
            updated = Message.objects.filter(id=message_id).update(
                title=title,
                content=content,
                task_status=task_status,
                total_count=total_count,
                success_count=success_count,
                failed_count=failed_count,
                fail_reason=error or '',
                related_url=related_url,
                is_read=False,
                read_time=None,
                duration=duration,
                update_by=user,
                update_time=timezone.now(),
            )
            if updated:
                logger.info(f"[AI-SCENE任务 {task_id}] 站内信 {message_id} 已更新为 {title}")
                _push_message(message_id)
            else:
                logger.warning(f"[AI-SCENE任务 {task_id}] 站内信 {message_id} 未找到，未更新")
        else:
            Message.objects.create(
                user=user,
                project=project,
                title=title,
                content=content,
                message_type=Message.MessageType.TASK,
                task_status=task_status,
                is_read=False,
                related_url=related_url,
                total_count=total_count,
                success_count=success_count,
                failed_count=failed_count,
                fail_reason=error or '',
                duration=duration,
                create_by=user,
                update_by=user,
            )
            logger.info(f"[AI-SCENE任务 {task_id}] 站内信已发送给用户 {user.username}")
    except Exception as e:
        logger.error(f"[AI-SCENE任务 {task_id}] 更新站内信失败: {e}")


def _push_message(message_id):
    """推送更新后的消息到前端"""
    if not message_id:
        return
    try:
        from apps.messages.models import Message
        from apps.messages.push import push_message_to_user, build_message_payload
        msg = Message.objects.filter(id=message_id).first()
        if msg:
            logger.info(f"[AI任务] 推送站内信 message_id={message_id} user_id={msg.user_id}")
            push_message_to_user(msg.user_id, build_message_payload(msg))
            logger.info(f"[AI任务] 推送站内信完成 message_id={message_id}")
    except Exception as e:
        logger.error(f"[AI任务] 推送站内信失败: {e}", exc_info=True)
