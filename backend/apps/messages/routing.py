from django.urls import re_path

from apps.messages import consumers

websocket_urlpatterns = [
    re_path(r'ws/message/', consumers.MessagePushConsumer.as_asgi()),
]