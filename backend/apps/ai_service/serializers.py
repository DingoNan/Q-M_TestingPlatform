from rest_framework import serializers
from apps.ai_service.models import AiConversation, AiMessage


class AiMessageSerializer(serializers.ModelSerializer):
    """AI对话消息序列化器"""
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = AiMessage
        fields = ['id', 'role', 'content', 'cases_data', 'create_time']


class AiConversationSerializer(serializers.ModelSerializer):
    """AI对话会话序列化器（列表/详情）"""
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    ai_config_name = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    module_name = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = AiConversation
        fields = [
            'id', 'title', 'ai_config_id', 'ai_config_name', 'model_name',
            'module_id', 'module_name', 'message_count', 'last_message',
            'create_time', 'update_time',
        ]

    def get_ai_config_name(self, obj):
        return obj.ai_config.provider_name if obj.ai_config else ''

    def get_model_name(self, obj):
        return obj.ai_config.model_name if obj.ai_config else ''

    def get_module_name(self, obj):
        return obj.module.name if obj.module else ''

    def get_message_count(self, obj):
        return obj.messages.filter(is_delete=False).count()

    def get_last_message(self, obj):
        last_msg = obj.messages.filter(is_delete=False).order_by('-create_time').first()
        return last_msg.content[:100] if last_msg else ''


class AiConversationCreateSerializer(serializers.ModelSerializer):
    """AI对话会话创建序列化器"""
    class Meta:
        model = AiConversation
        fields = ['id', 'title', 'ai_config_id', 'module_id']
        read_only_fields = ['id', 'title']
