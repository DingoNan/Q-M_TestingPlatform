from rest_framework.permissions import IsAuthenticated
from apps.defects.models import Defect, DefectComment
from apps.defects.serializers import DefectSerializer, DefectCommentSerializer
from apps.defects.filters import DefectFilter, DefectCommentFilter
from utils.base import BasePageNumberPagination
from utils.base_view import BaseModelViewSet


class DefectViewSet(BaseModelViewSet):
    serializer_class = DefectSerializer
    queryset = Defect.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = DefectFilter
    # 后端排序：使用实际模型字段路径（处理人需跨表用 assignee__username）
    ordering_fields = [
        'severity',
        'priority',
        'defect_type',
        'status',
        'owner__username',
        'assignee__username',
        'create_time',
        'update_time',
    ]


class DefectCommentViewSet(BaseModelViewSet):
    serializer_class = DefectCommentSerializer
    queryset = DefectComment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = DefectCommentFilter

    def get_queryset(self):
        return super().get_queryset().select_related('comment_by', 'defect')
