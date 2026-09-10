import asyncio
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)

# 群组前缀，group = f'user_{user_id}'
GROUP_PREFIX = 'user_'


class MessagePushConsumer(AsyncWebsocketConsumer):
    """用户消息实时推送 WebSocket。

    前端通过 query 参数 token 携带 JWT 进行鉴权，例如：
        ws://host/ws/message/?token=<access_token>
    连接后加入群组 user_<user_id>，后端调用 push_message_to_user
    即可将消息实时推送给该用户的所有在线连接。

    推送机制同时支持两种方式：
    1. channels layer group_send（在主进程内推送时生效）
    2. Redis pub/sub 直连（从 Q worker 等子进程推送时生效，避免 channels layer 挂起）
    """

    async def connect(self):
        self.user = None
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        token = self._extract_token(query_string)

        if token:
            self.user = await self._authenticate_user(token)

        if self.user is None or not self.user.is_authenticated:
            logger.warning('WebSocket 鉴权失败，关闭连接')
            await self.close(code=4401)
            return

        self.group_name = f'{GROUP_PREFIX}{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f'WebSocket 连接成功: user={self.user.id} group={self.group_name} channel={self.channel_name}')

        # 启动 Redis pub/sub 监听（用于接收来自 Q worker 等子进程的推送）
        self._redis_listener_task = asyncio.ensure_future(self._redis_listen())

    async def _redis_listen(self):
        """异步监听 Redis pub/sub 通道，接收从子进程（Q worker 等）推送的消息"""
        try:
            from django.conf import settings
            redis_host = settings.REDIS_HOST
            redis_port = settings.REDIS_PORT
            redis_password = settings.REDIS_PASSWORD or None
        except Exception:
            redis_host = 'redis'
            redis_port = 6379
            redis_password = None

        _redis_conn = None
        try:
            import redis.asyncio as aioredis
            _redis_conn = aioredis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=0,
                socket_connect_timeout=5,
                # 不设 socket_timeout: pub/sub listen() 是阻塞等待消息的，
                # 设了超时会在无消息时断开连接，导致收不到后续推送
            )
            pubsub = _redis_conn.pubsub()
            await pubsub.subscribe(f'ws:user:{self.user.id}')
            logger.info(f'Redis pub/sub 订阅成功: ws:user:{self.user.id}')
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        await self.send(text_data=message['data'].decode('utf-8'))
                    except Exception as e:
                        logger.error(f'Redis pub/sub 消息发送失败: {e}')
        except asyncio.CancelledError:
            logger.info('Redis pub/sub 监听任务已取消')
        except Exception as e:
            logger.error(f'Redis pub/sub 监听错误: {e}')
        finally:
            if _redis_conn:
                try:
                    await _redis_conn.close()
                except Exception:
                    pass

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, '_redis_listener_task'):
            self._redis_listener_task.cancel()
            try:
                await self._redis_listener_task
            except (asyncio.CancelledError, Exception):
                pass

    async def receive(self, text_data=None, bytes_data=None):
        # 服务端主动推送为主，前端暂无需额外指令；收到 ping 可回 pong 保持连接
        if text_data:
            try:
                payload = json.loads(text_data)
                if payload.get('type') == 'ping':
                    await self.send(text_data=json.dumps({'type': 'pong'}))
            except Exception:
                pass

    async def message_push(self, event):
        """处理 group_send 的 message.push 事件"""
        message = event.get('message', {})
        logger.info(f'WebSocket 收到推送消息: type={message.get("message_type")} task_status={message.get("task_status")} title={message.get("title")}')
        await self.send(text_data=json.dumps({'type': 'message.push', 'message': message}))

    @staticmethod
    def _extract_token(query_string: str) -> str:
        for part in query_string.split('&'):
            if part.startswith('token='):
                return part[len('token='):]
        return ''

    @database_sync_to_async
    def _authenticate_user(self, token: str):
        try:
            access = AccessToken(token)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(id=access['user_id']).first()
            if user and user.is_active:
                return user
        except (TokenError, InvalidToken, KeyError, Exception) as exc:
            logger.warning(f'WebSocket token 校验失败: {exc}')
        return None