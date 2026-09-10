"""
ASGI config - Channels 协议路由
HTTP 走 Django，WebSocket 走消息推送 consumer
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

# 与 manage.py 保持一致：根据 RUN_ENV 选择 settings 模块(daphne 不经过 manage.py)
ENV = os.environ.get('RUN_ENV', 'dev')
SETTINGS_BY_ENV = {
    'dev': 'black_bag.settings_dev',
    'pro': 'black_bag.settings_pro',
    'docker': 'black_bag.settings_docker',
}
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_BY_ENV.get(ENV, 'black_bag.settings_dev'))

# 先初始化 Django 以注册所有 app
django_asgi_app = get_asgi_application()

# 在此之后导入 consumer 才能访问到已加载的 settings/apps
from apps.messages.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})