from rest_framework import serializers
from apps.audit.models import AuditLog
from utils.base import BaseSerializer


class AuditLogSerializer(BaseSerializer):
    """审计日志序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    content_type_name = serializers.CharField(source='content_type.name', read_only=True)
    request_body_pretty = serializers.SerializerMethodField()
    response_body_pretty = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'username', 'action', 'action_display',
            'method', 'path', 'ip', 'module', 'project', 'project_name',
            'request_body', 'request_body_pretty',
            'response_body', 'response_body_pretty',
            'before_data', 'after_data',
            'status_code', 'description',
            'content_type', 'content_type_name', 'object_id',
            'create_time', 'update_time',
        ]
        read_only_fields = fields

    def get_request_body_pretty(self, obj):
        """格式化请求体JSON"""
        if not obj.request_body:
            return ''
        try:
            import json
            return json.dumps(json.loads(obj.request_body), ensure_ascii=False, indent=2)
        except Exception:
            return obj.request_body

    def get_response_body_pretty(self, obj):
        """格式化响应体JSON"""
        if not obj.response_body:
            return ''
        try:
            import json
            return json.dumps(json.loads(obj.response_body), ensure_ascii=False, indent=2)
        except Exception:
            return obj.response_body
