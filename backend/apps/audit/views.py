import json
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core import serializers as django_serializers
from django.contrib.contenttypes.models import ContentType

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.audit.filters import AuditLogFilter
from utils.base import BasePageNumberPagination
from utils.base_view import BaseModelViewSet

logger = logging.getLogger('audit')


class AuditLogViewSet(BaseModelViewSet):
    """审计日志视图集 — 只读（list + retrieve）+ 版本回退"""
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = AuditLogFilter
    ordering = ['-create_time']
    http_method_names = ['get', 'post', 'head', 'options']  # 仅允许 GET 和 POST（POST用于rollback action）

    def get_queryset(self):
        """默认只返回非删除的记录，按创建时间倒序"""
        queryset = super().get_queryset()
        # project 参数为项目名称（前端下拉框传 name），由 filterset 的
        # project__name__icontains 负责过滤，此处不再按 project_id 过滤
        return queryset

    @action(detail=True, methods=['post'], url_path='rollback')
    def rollback(self, request, pk=None):
        """
        版本回退 — 根据审计日志记录回退操作

        - 新增回退：删除创建的对象
        - 修改回退：用 before_data 恢复对象到操作前的状态
        - 删除回退：用 before_data 重新创建对象
        """
        audit_log = self.get_object()

        if not audit_log.before_data and audit_log.action != 'create':
            return Response(
                {'detail': '该日志没有操作前数据，无法回退'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if audit_log.action == 'create':
                return self._rollback_create(audit_log, request)
            elif audit_log.action == 'update':
                return self._rollback_update(audit_log, request)
            elif audit_log.action == 'delete':
                return self._rollback_delete(audit_log, request)
            else:
                return Response(
                    {'detail': f'不支持对 {audit_log.get_action_display()} 操作的回退'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error('版本回退失败: %s', e)
            return Response(
                {'detail': f'回退失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _rollback_create(self, audit_log, request):
        """新增回退 — 删除创建的对象"""
        if not audit_log.content_type or not audit_log.object_id:
            return Response(
                {'detail': '无法确定操作对象，不能回退'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model_class = audit_log.content_type.model_class()
        if not model_class:
            return Response(
                {'detail': '模型类不存在，不能回退'},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = model_class.objects.filter(pk=audit_log.object_id).first()
        if not obj:
            return Response(
                {'detail': '对象已不存在，无需回退'},
                status=status.HTTP_200_OK
            )

        # 执行删除（逻辑删除）
        if hasattr(obj, 'is_delete'):
            obj.is_delete = True
            obj.save()
        else:
            obj.delete()

        return Response(
            {'detail': f'已回退新增操作，删除了 {audit_log.module} (ID: {audit_log.object_id})'},
            status=status.HTTP_200_OK
        )

    def _rollback_update(self, audit_log, request):
        """修改回退 — 用 before_data 恢复对象"""
        if not audit_log.content_type or not audit_log.object_id:
            return Response(
                {'detail': '无法确定操作对象，不能回退'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model_class = audit_log.content_type.model_class()
        if not model_class:
            return Response(
                {'detail': '模型类不存在，不能回退'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 使用 Django 反序列化恢复对象
        restored = False
        for deserialized_obj in django_serializers.deserialize('json', audit_log.before_data):
            obj = deserialized_obj.object
            # 确保对象存在（如果被删除了则恢复）
            obj.is_delete = False
            obj.save()
            restored = True

        if not restored:
            return Response(
                {'detail': '回退失败：无法解析操作前数据'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'detail': f'已回退修改操作，恢复了 {audit_log.module} (ID: {audit_log.object_id}) 到操作前状态'},
            status=status.HTTP_200_OK
        )

    def _rollback_delete(self, audit_log, request):
        """删除回退 — 用 before_data 重新创建对象"""
        # 使用 Django 反序列化重新创建对象
        restored = False
        for deserialized_obj in django_serializers.deserialize('json', audit_log.before_data):
            obj = deserialized_obj.object
            # 恢复：取消逻辑删除标记
            if hasattr(obj, 'is_delete'):
                obj.is_delete = False
            obj.save()
            restored = True

        if not restored:
            return Response(
                {'detail': '回退失败：无法解析操作前数据'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'detail': f'已回退删除操作，恢复了 {audit_log.module} (ID: {audit_log.object_id})'},
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        """禁止手动创建审计日志"""
        return Response({'detail': '不允许手动创建审计日志'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        """禁止修改审计日志"""
        return Response({'detail': '不允许修改审计日志'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        """禁止删除审计日志"""
        return Response({'detail': '不允许删除审计日志'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
