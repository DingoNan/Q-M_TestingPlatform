"""
异步任务 - 接口文档导入（V2）
- import_api_doc_task: 后台解析 OpenAPI/Swagger/Postman/JMeter/cURL 文档并批量落库，
  完成后更新站内信任务状态并推送消息。
"""
import logging
from django.utils import timezone

from apps.interfaces.views import (
    ImportApiTypeV2,
    ImportMatchMode,
    _parse_spec_content_v2,
    _fetch_url_content_v2,
    _parse_openapi_v2,
    _parse_postman_v2,
    _parse_jmeter_v2,
    _parse_curl_v2,
)
from apps.messages.models import Message
from apps.users.models import User

logger = logging.getLogger('interfaces')


def import_api_doc_task(task_id: str, format: str, source: str, service_id: int,
                        user_id: int, message_id: int = None,
                        url: str = None, content: str = None,
                        uri_prefix: str = '', match_mode: str = ImportMatchMode.Overwrite,
                        target_module_id=None):
    """
    异步导入接口文档：
      1. 获取原始内容（URL 拉取 / 已传入的文件文本）
      2. 按格式解析并批量创建/更新接口
      3. 更新站内信状态为已完成/失败并推送
    """
    logger.info(f"[接口导入任务 {task_id}] 开始 - format={format}, source={source}, service={service_id}")
    start = timezone.now()
    user = User.objects.filter(id=user_id).first()
    stats = {'success': 0, 'skipped': 0, 'updated': 0, 'failed': 0, 'total': 0, 'errors': []}
    error = None

    try:
        # cURL 格式：content 直接来自粘贴文本
        if format == ImportApiTypeV2.Curl:
            if not content or not content.strip():
                raise ValueError('请粘贴 cURL 命令')
            stats = _parse_curl_v2(content, service_id, user_id, uri_prefix, match_mode, target_module_id)
        else:
            # 文件内容已在请求中读取为 content；URL 来源在任务内拉取
            if source == 'url':
                if not url:
                    raise ValueError('请输入 URL')
                content = _fetch_url_content_v2(url)
            if not content or not content.strip():
                raise ValueError('导入内容不能为空')

            if format in ImportApiTypeV2.OPENAPI_FAMILY:
                spec = _parse_spec_content_v2(content)
                stats = _parse_openapi_v2(spec, service_id, user_id, uri_prefix, match_mode, target_module_id)
            elif format == ImportApiTypeV2.PostmanV21:
                collection = _parse_spec_content_v2(content)
                stats = _parse_postman_v2(collection, service_id, user_id, uri_prefix, match_mode, target_module_id)
            elif format == ImportApiTypeV2.Jmeter:
                stats = _parse_jmeter_v2(content, service_id, user_id, uri_prefix, match_mode, target_module_id)
            else:
                raise ValueError(f'不支持的格式: {format}')
        logger.info(f"[接口导入任务 {task_id}] 完成 - 新增{stats['success']}, 更新{stats['updated']}, "
                    f"跳过{stats['skipped']}, 失败{stats['failed']}")
    except Exception as e:
        error = str(e)
        logger.error(f"[接口导入任务 {task_id}] 失败: {e}", exc_info=True)
    finally:
        _update_message(task_id, service_id, message_id, user, stats, error,
                        duration=(timezone.now() - start).total_seconds())


def _update_message(task_id, service_id, message_id, user, stats, error, duration):
    """更新站内信状态为已完成/失败，并推送最新消息"""
    try:
        from apps.envs.models import Service
        service = Service.objects.filter(id=service_id).first()
        total = sum([stats['success'], stats['updated'], stats['skipped'], stats['failed']])
        if error:
            title = '接口文档导入失败'
            content = (f"服务: {service.name if service else service_id}\n"
                       f"任务ID: {task_id}\n失败原因: {error}")
            task_status = Message.TaskStatus.FAILED
            fail_reason = error
        else:
            title = '接口文档导入完成'
            content = (
                f"服务: {service.name if service else service_id}\n"
                f"新增: {stats['success']}\n"
                f"更新: {stats['updated']}\n"
                f"跳过: {stats['skipped']}\n"
                f"失败: {stats['failed']}\n"
                f"耗时: {duration:.1f} 秒"
            )
            task_status = Message.TaskStatus.SUCCESS
            fail_reason = ''
            if stats['errors']:
                content += "\n失败明细:\n" + "\n".join(stats['errors'][:20])

        if message_id:
            Message.objects.filter(id=message_id).update(
                title=title,
                content=content,
                task_status=task_status,
                total_count=total,
                success_count=stats['success'],
                failed_count=stats['failed'],
                fail_reason=fail_reason,
                related_url='/resource/api',
                is_read=False,
                read_time=None,
                duration=duration,
                update_by=user,
                update_time=timezone.now(),
            )
            logger.info(f"[接口导入任务 {task_id}] 站内信 {message_id} 已更新为 {title}")
            _push_updated_message(message_id)
    except Exception as e:
        logger.error(f"[接口导入任务 {task_id}] 更新站内信失败: {e}")


def _push_updated_message(message_id):
    """推送最新消息到前端"""
    if not message_id:
        return
    try:
        from apps.messages.models import Message
        from apps.messages.push import push_message_to_user, build_message_payload
        msg = Message.objects.filter(id=message_id).first()
        if msg:
            logger.info(f"[接口导入任务] 推送站内信 message_id={message_id} user_id={msg.user_id}")
            push_message_to_user(msg.user_id, build_message_payload(msg))
    except Exception as e:
        logger.error(f"[接口导入任务] 推送站内信失败: {e}", exc_info=True)
