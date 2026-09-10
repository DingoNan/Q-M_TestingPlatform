import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# 群组前缀，与 consumers.py 保持一致
GROUP_PREFIX = 'user_'


def _get_redis_conn():
    """创建同步 Redis 连接"""
    import redis
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD or None,
        db=0,
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=False,
    )


def push_message_to_user(user_id, message):
    """向指定用户的所有在线 WebSocket 连接推送一条消息。

    通过 Redis pub/sub 直连推送，避免 channels layer 在子进程(Q worker 等)中挂起。
    WebSocket consumer 已订阅对应的 Redis 频道，收到消息后转发给前端。

    :param user_id: 接收用户 id
    :param message: dict,需要推送给前端的消息数据
    """
    if not user_id:
        return

    logger.info(f'WebSocket推送开始 user={user_id} message_type={message.get("message_type")} task_status={message.get("task_status")}')

    try:
        r = _get_redis_conn()
        try:
            payload = json.dumps({'type': 'message.push', 'message': message}, ensure_ascii=False)
            r.publish(f'ws:user:{user_id}', payload)
            logger.info(f'Redis pub/sub 推送完成 user={user_id}')
        finally:
            try:
                r.close()
            except Exception:
                pass
    except Exception as exc:
        logger.warning(f'WebSocket 消息推送失败 user={user_id}: {exc}')


def build_message_payload(msg_obj):
    """将 Message 对象序列化为前端可直接渲染(复用消息列表接口)的 dict"""
    return {
        'id': msg_obj.id,
        'user': msg_obj.user_id,
        'project': msg_obj.project_id,
        'title': msg_obj.title,
        'content': msg_obj.content,
        'message_type': str(msg_obj.message_type),
        'is_read': msg_obj.is_read,
        'read_time': msg_obj.read_time.strftime('%Y-%m-%d %H:%M:%S') if msg_obj.read_time else None,
        'related_url': msg_obj.related_url,
        'task_status': msg_obj.task_status,
        'total_count': msg_obj.total_count,
        'success_count': msg_obj.success_count,
        'failed_count': msg_obj.failed_count,
        'fail_reason': msg_obj.fail_reason,
        'duration': msg_obj.duration,
        'create_time': msg_obj.create_time.strftime('%Y-%m-%d %H:%M:%S') if msg_obj.create_time else None,
        'update_time': msg_obj.update_time.strftime('%Y-%m-%d %H:%M:%S') if msg_obj.update_time else None,
    }