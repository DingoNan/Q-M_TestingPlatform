from utils.base import BaseSerializer
from apps.messages.models import Message


class MessageSerializer(BaseSerializer):

    class Meta:
        model = Message
        fields = [
            'id', 'user', 'project', 'title', 'content', 'message_type',
            'is_read', 'read_time', 'related_url',
            'task_status', 'total_count', 'success_count', 'failed_count', 'fail_reason', 'duration',
            'create_time', 'update_time', 'create_by_name', 'update_by_name'
        ]
        read_only_fields = ['id', 'user', 'create_time', 'update_time', 'create_by_name', 'update_by_name']