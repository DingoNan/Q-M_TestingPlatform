from django_filters import rest_framework
from apps.ai_service.models import AiConversation


class AiConversationFilter(rest_framework.FilterSet):
    class Meta:
        model = AiConversation
        fields = ['project']
