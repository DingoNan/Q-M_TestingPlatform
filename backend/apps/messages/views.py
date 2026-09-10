from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import json
import time

from utils.base import BasePageNumberPagination
from apps.messages.models import Message
from apps.messages.filters import MessageFilter
from apps.messages.serializers import MessageSerializer
from utils.base_view import BaseModelViewSet


class MessageViewSet(BaseModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = MessageFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='mark-read')
    def mark_read(self, request):
        """标记消息为已读"""
        message_ids = request.data.get('message_ids', [])
        if message_ids:
            Message.objects.filter(
                id__in=message_ids,
                user=request.user
            ).update(is_read=True, read_time=timezone.now())
        return Response({'detail': '标记成功'})

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """标记所有消息为已读"""
        Message.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_time=timezone.now())
        return Response({'detail': '全部已读'})


@api_view(['GET'])
def unread_count(request: Request):
    """获取未读消息数量"""
    if not request.user.is_authenticated:
        return Response({"code": 200, "msg": "ok", "result": {"count": 0}})

    queryset = Message.objects.filter(user=request.user, is_read=False)

    # 根据 project_id 过滤
    project_id = request.query_params.get('project_id')
    if project_id:
        queryset = queryset.filter(project_id=project_id)

    count = queryset.count()
    # 按类型统计未读数
    by_type = {}
    for msg_type, label in [('1', 'system'), ('2', 'task'), ('3', 'alert')]:
        by_type[msg_type] = queryset.filter(message_type=msg_type).count()

    return Response({"count": count, "by_type": by_type})