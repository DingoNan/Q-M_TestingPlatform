import json
import re
import uuid
import logging
from django.http import StreamingHttpResponse, JsonResponse
from django_q.tasks import async_task
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils.base import BasePageNumberPagination
from utils.base_view import BaseModelViewSet
from apps.ai_service.models import AiConversation, AiMessage
from apps.ai_service.serializers import AiConversationSerializer, AiMessageSerializer, AiConversationCreateSerializer
from apps.ai_service.filters import AiConversationFilter
from apps.tests.models import FuncCase, Tag
from apps.projects.models import Project

logger = logging.getLogger('ai_service')


def _parse_bool(val):
    """安全解析布尔值，处理 true/false 字符串和 None"""
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() == 'true'
    return bool(val)


class AiConversationViewSet(BaseModelViewSet):
    serializer_class = AiConversationSerializer
    queryset = AiConversation.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = AiConversationFilter
    ordering_fields = ['create_time', 'update_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user).order_by('-update_time')

    def get_serializer_class(self):
        if self.action == 'create':
            return AiConversationCreateSerializer
        return AiConversationSerializer

    def create(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            project_id=int(project_id),
            create_by=request.user,
            update_by=request.user,
        )
        return Response(serializer.data, status=201)

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.update_by = self.request.user
        instance.save()
        instance.messages.filter(is_delete=False).update(is_delete=True)

    @action(detail=True, methods=['patch'])
    def rename(self, request, *args, **kwargs):
        """重命名会话"""
        conv = self.get_object()
        title = request.data.get('title', '').strip()
        if not title:
            return Response({'detail': '标题不能为空'}, status=400)
        conv.title = title[:200]
        conv.update_by = request.user
        conv.save()
        return Response({'id': conv.id, 'title': conv.title})

    @action(detail=True, methods=['get'])
    def messages(self, request, *args, **kwargs):
        """获取会话消息列表"""
        conv = self.get_object()
        msgs = conv.messages.filter(is_delete=False).order_by('create_time')
        serializer = AiMessageSerializer(msgs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def chat_stream(self, request, *args, **kwargs):
        """
        SSE流式对话接口
        POST请求体(JSON):
            message: 用户消息文本
            images: 图片base64列表(可选)
            ai_config_id: AI模型配置ID
        """
        from apps.ai_service.llm import LLMClient
        from apps.ai_service.prompts import (
            CHAT_SYSTEM, CHAT_SYSTEM_WITH_CONTEXT,
            ASSISTANT_SYSTEM, ASSISTANT_SYSTEM_WITH_CONTEXT,
            ASSISTANT_AGENT_SYSTEM,
        )

        conv = self.get_object()
        message = request.data.get('message', '').strip()
        images = request.data.get('images', [])
        ai_config_id = request.data.get('ai_config_id')
        mode = request.data.get('mode', 'generate')  # 'generate' | 'assistant'

        if not message and not images:
            return JsonResponse({'detail': '消息不能为空'}, status=400)
        if not ai_config_id:
            return JsonResponse({'detail': '请选择AI模型'}, status=400)

        # 保存用户消息（文本+图片占位）
        display_content = message
        if images:
            display_content = message + f'\n[图片x{len(images)}]' if message else f'[图片x{len(images)}]'
        AiMessage.objects.create(
            conversation=conv,
            role=AiMessage.Role.USER,
            content=display_content,
            create_by=request.user,
            update_by=request.user,
        )

        # 构建消息列表 - 根据mode选择不同的系统提示词
        module_info = ''
        if conv.module:
            module_info = f"模块: {conv.module.name}"
        if mode == 'assistant':
            # Agent模式使用带工具调用的系统提示词
            system_prompt = ASSISTANT_AGENT_SYSTEM
        else:
            system_prompt = CHAT_SYSTEM_WITH_CONTEXT.format(module_info=module_info) if module_info else CHAT_SYSTEM

        # 获取历史消息（最近20条），历史消息只用文本
        history_msgs = list(conv.messages.filter(is_delete=False).order_by('-create_time')[:20])
        history_msgs.reverse()
        messages = [{"role": "system", "content": system_prompt}]
        for i, msg in enumerate(history_msgs):
            if msg.role not in ['user', 'assistant']:
                continue
            # 最后一条用户消息支持多模态（含图片）
            if i == len(history_msgs) - 1 and msg.role == 'user' and images:
                content_parts = []
                if message:
                    content_parts.append({"type": "text", "text": message})
                for img_data in images:
                    content_parts.append({"type": "image_url", "image_url": {"url": img_data}})
                messages.append({"role": "user", "content": content_parts})
            else:
                messages.append({"role": msg.role, "content": msg.content})

        # 如果会话标题是默认的，用第一条消息更新
        if conv.title == '新对话':
            conv.title = message[:50]
            conv.save()

        def event_stream():
            try:
                if mode == 'assistant':
                    # ===== Agent模式：走LangGraph ReAct流程（带工具调用） =====
                    from apps.ai_service.agent_graph import run_agent_stream

                    full_text = ''
                    has_error = False
                    for sse_event in run_agent_stream(messages, conv.project_id, ai_config_id):
                        yield sse_event
                        # 从SSE事件中提取content用于保存
                        if sse_event.startswith('data: '):
                            try:
                                data = json.loads(sse_event[6:].strip())
                                if 'content' in data:
                                    full_text += data['content']
                                elif 'error' in data:
                                    has_error = True
                            except (json.JSONDecodeError, ValueError):
                                pass

                    if not has_error and full_text:
                        ai_msg = AiMessage.objects.create(
                            conversation=conv,
                            role=AiMessage.Role.ASSISTANT,
                            content=full_text,
                            cases_data=[],
                            create_by=request.user,
                            update_by=request.user,
                        )
                        yield f"data: {json.dumps({'done': True, 'cases': [], 'message_id': ai_msg.id}, ensure_ascii=False)}\n\n"
                    elif not has_error:
                        yield f"data: {json.dumps({'done': True, 'cases': [], 'message_id': None}, ensure_ascii=False)}\n\n"

                else:
                    # ===== 生成用例模式：原有流式对话 =====
                    full_response = []
                    llm = LLMClient(ai_config_id=ai_config_id)
                    for chunk in llm.chat_stream(messages):
                        full_response.append(chunk)
                        yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

                    full_text = ''.join(full_response)
                    cases_data = _parse_cases_from_response(full_text)

                    ai_msg = AiMessage.objects.create(
                        conversation=conv,
                        role=AiMessage.Role.ASSISTANT,
                        content=full_text,
                        cases_data=cases_data,
                        create_by=request.user,
                        update_by=request.user,
                    )
                    yield f"data: {json.dumps({'done': True, 'cases': cases_data, 'message_id': ai_msg.id}, ensure_ascii=False)}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    @action(detail=False, methods=['post'])
    def save_chat_cases(self, request, *args, **kwargs):
        """
        从对话中保存用例到数据库
        请求参数:
            message_id: AI消息ID
            cases: 要保存的用例列表（可选，不传则保存消息中所有用例）
            module_id: 模块ID
            tag_ids: 标签ID列表
        """
        from apps.ai_service.vectorstore import add_case_to_vectorstore

        message_id = request.data.get('message_id')
        if not message_id:
            return Response({'detail': 'message_id不能为空'}, status=400)

        try:
            ai_msg = AiMessage.objects.get(id=message_id, is_delete=False)
        except AiMessage.DoesNotExist:
            return Response({'detail': '消息不存在'}, status=404)

        cases = request.data.get('cases', ai_msg.cases_data)
        if not cases:
            return Response({'detail': '没有可保存的用例'}, status=400)

        project_id = request.query_params.get('project') or request.data.get('project_id')
        module_id = request.data.get('module_id') or ai_msg.conversation.module_id
        tag_ids = request.data.get('tag_ids', [])

        user = request.user
        project = Project.objects.get(id=project_id)
        saved_cases = []
        failed_count = 0

        for case_data in cases:
            try:
                func_case = FuncCase(
                    name=case_data['name'],
                    project=project,
                    owner=user,
                    module_id=module_id,
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

                if tag_ids:
                    for tag_id in tag_ids:
                        try:
                            tag = Tag.objects.get(id=tag_id)
                            func_case.tag.add(tag)
                        except Tag.DoesNotExist:
                            pass

                saved_cases.append({'id': func_case.id, 'name': func_case.name})

                # 同步到向量库（供RAG检索使用）
                add_case_to_vectorstore(
                    project_id=int(project_id),
                    case_id=func_case.id,
                    case_name=func_case.name,
                    step_text='',
                    step_table=func_case.step_table or [],
                    module_id=module_id,
                )
            except Exception as e:
                logger.error(f"保存用例失败: {case_data.get('name', '未知')} - {e}")
                failed_count += 1

        return Response({
            'saved_count': len(saved_cases),
            'failed_count': failed_count,
            'cases': saved_cases,
        })

    @action(detail=False, methods=['post'])
    def generate_func_case(self, request, *args, **kwargs):
        """
        AI生成功能测试用例 - 异步任务
        请求参数:
            requirement: 需求描述 (可选，若有图片则可空)
            ai_config_id: AI模型配置ID (必填)
            module_id: 模块ID (可选)
            tag_ids: 标签ID列表 (可选)
            generate_count: 生成条数 (默认3)
            include_boundary: 包含边界场景 (默认true)
            include_exception: 包含异常场景 (默认true)
            include_performance: 包含性能安全场景 (默认false)
            images: 图片列表 (可选) [{base64: '...', type: 'image/png'}, ...]
        """
        from apps.ai_service.tasks import ai_generate_func_case_task
        from apps.ai_service.file_processor import process_images, process_documents, build_requirement_with_images, build_requirement_with_documents
        from apps.messages.models import Message
        from apps.projects.models import Project

        requirement = request.data.get('requirement', '').strip()
        ai_config_id = request.data.get('ai_config_id')
        images = request.data.get('images', [])
        documents = request.data.get('documents', [])

        logger.info(f"[generate_func_case] 接收到参数: requirement={len(requirement)}字, images={len(images)}张, documents={len(documents)}个")
        if documents:
            for d in documents:
                logger.info(f"[generate_func_case] 文档: name={d.get('name')}, ext={d.get('ext')}, size={d.get('size')}, base64长度={len(d.get('base64', ''))}")

        # requirement、images、documents至少有一个
        if not requirement and not images and not documents:
            return Response({'detail': '需求描述不能为空，请输入文字或粘贴图片/文档'}, status=400)
        if not ai_config_id:
            return Response({'detail': '请选择AI模型'}, status=400)

        project_id = request.query_params.get('project') or request.data.get('project_id')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        # ===== 处理文档 =====
        doc_text = ''
        if documents:
            doc_results = process_documents(documents)
            doc_text = build_requirement_with_documents('', doc_results)
            logger.info(f"文档处理完成，{len(doc_results)}个文档，文本长度{len(doc_text)}")
            
            # 检查是否有文档解析成功（至少50字）
            docs_with_text = [r for r in doc_results if len(r.get('text', '')) >= 50]
            if not docs_with_text and not requirement and not images:
                # 只有文档且全部解析失败
                failed_names = [r.get('name', '未知') for r in doc_results if not r.get('text')]
                return Response({
                    'detail': f'文档解析失败: {", ".join(failed_names)}。请确保文件格式正确，或直接在对话框粘贴文字内容'
                }, status=400)

        # ===== 处理图片OCR =====
        image_text = ''
        if images:
            ocr_results = process_images(images)
            
            # 检查OCR质量：有差的图片则尝试LLM视觉兜底
            needs_vision = any(r['quality'] != 'good' for r in ocr_results)
            
            if needs_vision:
                try:
                    from apps.ai_service.llm import LLMClient
                    llm = LLMClient(int(ai_config_id))
                    vision_result = llm.chat_vision_json(
                        system_prompt="你是一位测试需求分析专家。请分析以下图片内容，提取所有文字信息，并补充描述图片中的主要内容、界面元素、流程关系等关键信息。输出JSON格式：{\"text\": \"提取的文字\", \"description\": \"图片内容描述\"}",
                        text="请识别图片中的所有文字内容，并描述图片的主要内容。",
                        image_base64_list=images,
                        temperature=0.3,
                    )
                    vision_text = vision_result.get('text', '') + '\n' + vision_result.get('description', '')
                    if vision_text.strip():
                        # 用LLM视觉结果覆盖OCR结果
                        image_text = f"--- 图片AI识别结果 ---\n{vision_text.strip()}"
                    else:
                        # LLM也没识别到，用OCR结果
                        image_text = build_requirement_with_images('', ocr_results)
                except Exception as e:
                    logger.warning(f"LLM视觉兜底失败，使用OCR结果: {e}")
                    image_text = build_requirement_with_images('', ocr_results)
            else:
                image_text = build_requirement_with_images('', ocr_results)

        # 拼接最终requirement
        final_requirement = requirement
        if doc_text:
            final_requirement = f"{final_requirement}\n\n{doc_text}" if final_requirement else doc_text
        if image_text:
            final_requirement = f"{final_requirement}\n\n{image_text}" if final_requirement else image_text

        logger.info(f"[generate_func_case] 最终requirement: 总长{len(final_requirement)}字, 前200字: {final_requirement[:200]}")

        # 如果最终requirement仍为空，返回友好提示
        if not final_requirement or not final_requirement.strip():
            return Response({'detail': '未识别到有效内容，请尝试输入文字或使用更清晰的图片/文档'}, status=400)

        task_id = str(uuid.uuid4())[:8]

        # 创建站内信，状态为"进行中"
        project = Project.objects.filter(id=project_id).first()
        message = Message.objects.create(
            user=request.user,
            project=project,
            title=f"AI用例生成中",
            content=f"需求: {final_requirement[:100]}",
            message_type=Message.MessageType.TASK,
            task_status=Message.TaskStatus.RUNNING,
            total_count=0,
            success_count=0,
            failed_count=0,
            create_by=request.user,
            update_by=request.user,
        )

        async_task(
            'apps.ai_service.tasks.ai_generate_func_case_task',
            task_id=task_id,
            requirement=final_requirement,
            project_id=int(project_id),
            ai_config_id=int(ai_config_id),
            user_id=request.user.id,
            module_id=request.data.get('module_id'),
            tag_ids=request.data.get('tag_ids', []),
            generate_count=int(request.data.get('generate_count', 3)),
            include_boundary=request.data.get('include_boundary', True),
            include_exception=request.data.get('include_exception', True),
            include_performance=request.data.get('include_performance', False),
            message_id=message.id,
        )

        return Response({'task_id': task_id, 'message': 'AI生成任务已提交'})

    @action(detail=False, methods=['post'])
    def generate_api_case(self, request, *args, **kwargs):
        """
        AI生成接口自动化用例 - 异步任务
        请求参数:
            api_id: 接口文档ID (必填)
            ai_config_id: AI模型配置ID (必填)
            module_id: 用例模块ID (必填, 决定Step.plant)
            tag_ids: 标签ID列表 (可选)
            generate_count: 生成条数 (默认3)
            include_boundary: 包含边界场景 (默认false)
            include_missing_required: 包含缺必填字段场景 (默认false)
            include_type_error: 包含类型错误场景 (默认false)
            include_exception_status: 包含异常状态码场景 (默认false)
            include_security: 包含安全性场景 (默认false)
            extra_requirement: 补充需求文本 (可选)
        """
        from apps.ai_service.tasks import ai_generate_api_case_task
        from apps.messages.models import Message
        from apps.projects.models import Project
        from apps.interfaces.models import Api

        api_id = request.data.get('api_id')
        ai_config_id = request.data.get('ai_config_id')
        module_id = request.data.get('module_id')

        if not api_id:
            return Response({'detail': '接口ID不能为空'}, status=400)
        if not ai_config_id:
            return Response({'detail': '请选择AI模型'}, status=400)
        if not module_id:
            return Response({'detail': '请选择用例模块'}, status=400)

        project_id = request.query_params.get('project') or request.data.get('project_id')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        # 校验接口存在
        api = Api.objects.filter(id=api_id, is_delete=False).first()
        if not api:
            return Response({'detail': '接口不存在'}, status=404)

        task_id = str(uuid.uuid4())[:8]

        # 创建站内信，状态为"进行中"
        project = Project.objects.filter(id=project_id).first()
        message = Message.objects.create(
            user=request.user,
            project=project,
            title="AI接口用例生成中",
            content=f"接口: {api.method} {api.url}",
            message_type=Message.MessageType.TASK,
            task_status=Message.TaskStatus.RUNNING,
            total_count=0,
            success_count=0,
            failed_count=0,
            create_by=request.user,
            update_by=request.user,
        )

        async_task(
            'apps.ai_service.tasks.ai_generate_api_case_task',
            task_id=task_id,
            api_id=int(api_id),
            project_id=int(project_id),
            ai_config_id=int(ai_config_id),
            user_id=request.user.id,
            module_id=int(module_id),
            tag_ids=request.data.get('tag_ids', []),
            generate_count=int(request.data.get('generate_count', 3)),
            include_boundary=_parse_bool(request.data.get('include_boundary')),
            include_missing_required=_parse_bool(request.data.get('include_missing_required')),
            include_type_error=_parse_bool(request.data.get('include_type_error')),
            include_exception_status=_parse_bool(request.data.get('include_exception_status')),
            include_security=_parse_bool(request.data.get('include_security')),
            extra_requirement=request.data.get('extra_requirement', ''),
            message_id=message.id,
        )

        return Response({'task_id': task_id, 'message': 'AI接口用例生成任务已提交'})

    @action(detail=False, methods=['post'])
    def generate_scenario_case(self, request, *args, **kwargs):
        """
        AI从功能用例生成场景脚本用例 - 异步任务
        请求参数:
            func_case_id: 功能用例ID (必填)
            ai_config_id: AI模型配置ID (必填)
            module_id: 用例模块ID (必填, 决定Step.plant)
            mode: 生成模式，'api'/'web_ui' 或数组/逗号分隔，支持多选
            tag_ids: 标签ID列表 (可选)
            generate_count: 生成条数 (默认3)
            extra_requirement: 补充需求文本 (可选)
        """
        from apps.ai_service.tasks import ai_generate_scenario_case_task
        from apps.messages.models import Message
        from apps.projects.models import Project
        from apps.tests.models import FuncCase

        func_case_id = request.data.get('func_case_id')
        ai_config_id = request.data.get('ai_config_id')
        module_id = request.data.get('module_id')

        if not func_case_id:
            return Response({'detail': '功能用例ID不能为空'}, status=400)
        if not ai_config_id:
            return Response({'detail': '请选择AI模型'}, status=400)
        if not module_id:
            return Response({'detail': '请选择用例模块'}, status=400)

        # 解析模式(支持数组或逗号分隔)
        raw_mode = request.data.get('mode', 'api')
        if isinstance(raw_mode, (list, tuple)):
            modes = [str(m) for m in raw_mode]
        elif isinstance(raw_mode, str):
            modes = [m.strip() for m in raw_mode.replace('，', ',').split(',') if m.strip()]
        else:
            modes = ['api']
        modes = [m for m in modes if m in ('api', 'web_ui')]
        if not modes:
            return Response({'detail': '生成模式必须为api或web_ui'}, status=400)

        project_id = request.query_params.get('project') or request.data.get('project_id')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        func_case = FuncCase.objects.filter(id=func_case_id, is_delete=False).first()
        if not func_case:
            return Response({'detail': '功能用例不存在'}, status=404)

        project = Project.objects.filter(id=project_id).first()
        tasks_submitted = []
        for mode in modes:
            task_id = str(uuid.uuid4())[:8]
            message = Message.objects.create(
                user=request.user,
                project=project,
                title=f"AI{'接口' if mode == 'api' else 'WebUI'}脚本生成中",
                content=f"功能用例: {func_case.name}",
                message_type=Message.MessageType.TASK,
                task_status=Message.TaskStatus.RUNNING,
                total_count=0,
                success_count=0,
                failed_count=0,
                create_by=request.user,
                update_by=request.user,
            )
            async_task(
                'apps.ai_service.tasks.ai_generate_scenario_case_task',
                task_id=task_id,
                func_case_id=int(func_case_id),
                project_id=int(project_id),
                ai_config_id=int(ai_config_id),
                user_id=request.user.id,
                module_id=int(module_id),
                mode=mode,
                tag_ids=request.data.get('tag_ids', []),
                generate_count=int(request.data.get('generate_count', 3)),
                extra_requirement=request.data.get('extra_requirement', ''),
                message_id=message.id,
            )
            tasks_submitted.append({'task_id': task_id, 'mode': mode, 'message_id': message.id})

        return Response({'tasks': tasks_submitted, 'message': 'AI场景脚本生成任务已提交'})

    @action(detail=False, methods=['get'])
    def task_status(self, request, *args, **kwargs):
        """
        查询AI生成任务状态
        请求参数: task_id
        """
        from django.core.cache import cache

        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'detail': 'task_id不能为空'}, status=400)

        data = cache.get(f'ai_task_{task_id}')
        if not data:
            return Response({'status': 'not_found', 'message': '任务不存在或已过期'})

        return Response(data)

    @action(detail=False, methods=['post'])
    def rebuild_vectorstore(self, request, *args, **kwargs):
        """
        重建向量库（全量或按数据源类型）
        请求参数:
            project_id: 项目ID
            source_type: 数据源类型（可选: func_case/api/defect），不传则全量重建
        
        异步执行，过程写入任务消息通知
        """
        from apps.messages.models import Message
        from apps.projects.models import Project

        project_id = request.data.get('project_id') or request.query_params.get('project')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        project = Project.objects.filter(id=project_id).first()
        source_type = request.data.get('source_type')
        
        # 构建任务消息
        type_map = {'func_case': '功能用例', 'api': '接口文档', 'defect': '缺陷', 'element': '元素库'}
        type_label = type_map.get(source_type, '全部数据')
        
        message = Message.objects.create(
            user=request.user,
            project=project,
            title=f"向量库重建中 - {type_label}",
            content=f"项目: {project.name if project else '-'}\n正在重建{type_label}的向量库，请稍候...",
            message_type=Message.MessageType.TASK,
            task_status=Message.TaskStatus.RUNNING,
            total_count=0,
            success_count=0,
            failed_count=0,
            create_by=request.user,
            update_by=request.user,
        )

        # 异步执行重建（使用模块级函数，供 async_task 调用）
        async_task(
            'apps.ai_service.views.do_rebuild_vectorstore_task',
            project_id=int(project_id),
            source_type=source_type,
            user_id=request.user.id,
            message_id=message.id,
        )

        return Response({
            'success': True,
            'message': f'{type_label}向量库重建任务已提交',
            'message_id': message.id,
        })


# ===== 向量库重建异步任务（模块级函数，供 async_task 调用）=====
def do_rebuild_vectorstore_task(project_id: int, source_type: str = None, 
                                user_id: int = None, message_id: int = None):
    """
    异步执行向量库重建，并更新任务消息状态
    """
    import time
    import logging
    from django.utils import timezone
    from apps.ai_service.vectorstore import rebuild_vectorstore, rebuild_source
    from apps.messages.models import Message
    from apps.users.models import User
    from apps.projects.models import Project

    logger = logging.getLogger('ai_service')
    start_time = time.time()
    
    type_map = {'func_case': '功能用例', 'api': '接口文档', 'defect': '缺陷', 'element': '元素库'}
    type_label = type_map.get(source_type, '全部数据')
    
    try:
        logger.info(f"[向量库重建] 开始重建 {type_label}, project_id={project_id}")
        
        if source_type:
            result = rebuild_source(int(project_id), source_type)
        else:
            result = rebuild_vectorstore(int(project_id))
        
        duration = round(time.time() - start_time, 2)
        count = result.get('count', 0)
        
        # 更新消息为成功
        Message.objects.filter(id=message_id).update(
            title=f"向量库重建完成 - {type_label}",
            content=(
                f"项目: {Project.objects.get(id=project_id).name}\n"
                f"重建类型: {type_label}\n"
                f"重建条数: {count}\n"
                f"耗时: {duration} 秒"
            ),
            task_status=Message.TaskStatus.SUCCESS,
            total_count=count,
            success_count=count,
            failed_count=0,
            duration=duration,
            related_url='/resource/knowledgeBase',
            is_read=False,
            read_time=None,
            update_time=timezone.now(),
        )
        logger.info(f"[向量库重建] {type_label} 完成，共 {count} 条，耗时 {duration}s")
        _push_vectorstore_message(message_id)
        
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        logger.error(f"[向量库重建] {type_label} 失败: {e}")
        
        # 更新消息为失败
        try:
            project_name = Project.objects.get(id=project_id).name
        except Exception:
            project_name = '-'
            
        Message.objects.filter(id=message_id).update(
            title=f"向量库重建失败 - {type_label}",
            content=f"项目: {project_name}\n失败原因: {str(e)}",
            task_status=Message.TaskStatus.FAILED,
            fail_reason=str(e),
            duration=duration,
            is_read=False,
            read_time=None,
            update_time=timezone.now(),
        )
        _push_vectorstore_message(message_id)


def _push_vectorstore_message(message_id):
    """推送更新后的向量库重建消息到前端"""
    if not message_id:
        return
    try:
        from apps.messages.models import Message
        from apps.messages.push import push_message_to_user, build_message_payload
        msg = Message.objects.filter(id=message_id).first()
        if msg:
            push_message_to_user(msg.user_id, build_message_payload(msg))
    except Exception:
        pass


class VectorStoreViewSet(BaseModelViewSet):
    """向量库管理CRUD"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def vectorstore_stats(self, request, *args, **kwargs):
        """
        获取向量库统计信息
        请求参数: project_id
        """
        from apps.ai_service.vectorstore import get_vectorstore_stats

        project_id = request.query_params.get('project')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        result = get_vectorstore_stats(int(project_id))
        return Response(result)

    def list(self, request, *args, **kwargs):
        from apps.ai_service.vectorstore import list_items
        project_id = request.query_params.get('project') or request.data.get('project_id')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        source_type = request.query_params.get('source_type')
        chunk_type = request.query_params.get('chunk_type')
        module_id = request.query_params.get('module_id')
        keyword = request.query_params.get('keyword', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        result = list_items(
            project_id=int(project_id),
            source_type=source_type,
            chunk_type=chunk_type if chunk_type else None,
            module_id=int(module_id) if module_id else None,
            keyword=keyword if keyword else None,
            page=page,
            page_size=page_size,
        )
        return Response(result)

    def retrieve(self, request, pk=None):
        from apps.ai_service.vectorstore import get_item
        project_id = request.query_params.get('project')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        item = get_item(project_id=int(project_id), item_id=pk)
        if item is None:
            return Response({'detail': '分块不存在'}, status=404)
        return Response(item)

    def create(self, request, *args, **kwargs):
        from apps.ai_service.vectorstore import create_item
        from apps.ai_service.file_processor import process_documents, process_images
        project_id = request.data.get('project_id') or request.query_params.get('project')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        source_type = request.data.get('source_type', 'custom')
        source_id = request.data.get('source_id', 0)
        source_name = request.data.get('source_name', '')
        document = request.data.get('document', '')
        module_id = request.data.get('module_id')
        chunk_type = request.data.get('chunk_type', 'custom')
        extra_metadata = request.data.get('extra_metadata')
        files = request.data.get('files', [])
        
        # 获取当前用户
        user = request.user
        create_by_name = user.username if user and user.is_authenticated else None

        # 如果有文件，先解析文件内容并合并到document
        if files:
            # 分类：图片和文档
            images = []
            documents = []
            for f in files:
                ftype = f.get('type', '')
                if ftype.startswith('image/'):
                    images.append(f)
                else:
                    documents.append(f)

            parsed_texts = []

            # 处理图片
            if images:
                image_names = [img.get('name', f'image_{i}') for i, img in enumerate(images)]
                ocr_results = process_images(images)
                for i, r in enumerate(ocr_results):
                    text = r.get('text', '').strip()
                    if text:
                        name = image_names[i] if i < len(image_names) else f'图片{i+1}'
                        parsed_texts.append(f"=== 图片: {name} ===\n{text}")

            # 处理文档
            if documents:
                doc_results = process_documents(documents)
                for r in doc_results:
                    text = r.get('text', '').strip()
                    if text:
                        parsed_texts.append(f"=== 文档: {r.get('name', '未知')} ===\n{text}")

            # 合并文本
            if parsed_texts:
                parsed_full = '\n\n'.join(parsed_texts)
                if document and document.strip():
                    document = document.strip() + '\n\n' + parsed_full
                else:
                    document = parsed_full

        if not document or not document.strip():
            return Response({'detail': '文档内容不能为空'}, status=400)

        result = create_item(
            project_id=int(project_id),
            source_type=source_type,
            source_id=int(source_id) if source_id else 0,
            source_name=source_name,
            document=document,
            module_id=int(module_id) if module_id else None,
            chunk_type=chunk_type,
            extra_metadata=extra_metadata if isinstance(extra_metadata, dict) else None,
            create_by_name=create_by_name,
        )
        if result.get('success'):
            return Response(result, status=201)
        return Response(result, status=500)

    def update(self, request, pk=None, *args, **kwargs):
        from apps.ai_service.vectorstore import update_item
        project_id = request.query_params.get('project')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        document = request.data.get('document')
        metadata_update = request.data.get('metadata_update')

        result = update_item(
            project_id=int(project_id),
            item_id=pk,
            document=document,
            metadata_update=metadata_update if isinstance(metadata_update, dict) else None,
        )
        if result.get('success'):
            return Response(result)
        return Response(result, status=404 if '不存在' in str(result.get('error', '')) else 500)

    def destroy(self, request, pk=None, *args, **kwargs):
        from apps.ai_service.vectorstore import delete_item
        project_id = request.query_params.get('project')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        result = delete_item(project_id=int(project_id), item_id=pk)
        if result.get('success'):
            return Response(result)
        return Response(result, status=500)

    @action(detail=False, methods=['post'])
    def batch_delete(self, request, *args, **kwargs):
        from apps.ai_service.vectorstore import batch_delete
        project_id = request.data.get('project_id') or request.query_params.get('project')
        if not project_id:
            return Response({'detail': '项目ID不能为空'}, status=400)

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=400)

        result = batch_delete(project_id=int(project_id), ids=ids)
        return Response(result)

    @action(detail=False, methods=['get'])
    def source_types(self, request, *args, **kwargs):
        from apps.ai_service.vectorstore import SOURCE_TYPE_LABELS, CHUNK_TYPE_LABELS
        return Response({
            'source_types': [
                {'value': 'func_case', 'label': SOURCE_TYPE_LABELS.get('func_case', '功能用例')},
                {'value': 'api', 'label': SOURCE_TYPE_LABELS.get('api', '接口文档')},
                {'value': 'defect', 'label': SOURCE_TYPE_LABELS.get('defect', '已解决缺陷')},
                {'value': 'element', 'label': SOURCE_TYPE_LABELS.get('element', '元素库')},
                {'value': 'custom', 'label': SOURCE_TYPE_LABELS.get('custom', '自定义知识')},
            ],
            'chunk_types': [
                {'value': k, 'label': v} for k, v in CHUNK_TYPE_LABELS.items()
            ],
        })

    @action(detail=False, methods=['post'])
    def parse_file(self, request, *args, **kwargs):
        """
        解析文件（文档/图片）为文本
        请求参数:
            files: 文件列表 [{base64, name, ext, type, size}, ...]
        """
        from apps.ai_service.file_processor import process_documents, process_images

        files = request.data.get('files', [])
        if not files:
            return Response({'detail': '请提供文件列表'}, status=400)

        # 分类：图片和文档
        images = []
        documents = []
        for f in files:
            ftype = f.get('type', '')
            if ftype.startswith('image/'):
                images.append(f)
            else:
                documents.append(f)

        result_texts = []

        # 处理图片（保存原始文件名映射）
        if images:
            image_names = [img.get('name', f'image_{i}') for i, img in enumerate(images)]
            ocr_results = process_images(images)
            for i, r in enumerate(ocr_results):
                text = r.get('text', '').strip()
                if text:
                    name = image_names[i] if i < len(image_names) else f'图片{i+1}'
                    result_texts.append(f"=== 图片: {name} ===\n{text}")

        # 处理文档
        if documents:
            doc_results = process_documents(documents)
            for r in doc_results:
                text = r.get('text', '').strip()
                if text:
                    result_texts.append(f"=== 文档: {r.get('name', '未知')} ===\n{text}")

        if not result_texts:
            return Response({
                'text': '',
                'warning': '所有文件均未能解析出有效文本内容，请检查文件格式或直接粘贴文字',
            })

        full_text = '\n\n'.join(result_texts)
        return Response({
            'text': full_text,
            'file_count': len(files),
            'parsed_count': len(result_texts),
        })


def _parse_cases_from_response(text: str) -> list:
    """从AI回复中解析```json代码块里的用例数据"""
    try:
        # 匹配```json ... ```代码块
        pattern = r'```json\s*(\{.*?\})\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            data = json.loads(matches[-1])
            return data.get('cases', [])
        # 兜底：尝试匹配裸JSON
        pattern2 = r'\{[^{}]*"cases"[^{}]*\[.*?\][^{}]*\}'
        matches2 = re.findall(pattern2, text, re.DOTALL)
        if matches2:
            data = json.loads(matches2[-1])
            return data.get('cases', [])
    except (json.JSONDecodeError, IndexError) as e:
        logger.warning(f"解析用例JSON失败: {e}")
    return []
