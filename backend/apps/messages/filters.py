from django_filters import rest_framework

from apps.messages.models import Message


class MessageFilter(rest_framework.FilterSet):
    title = rest_framework.CharFilter(lookup_expr='contains')

    class Meta:
        model = Message
        fields = ['user', 'project', 'message_type', 'is_read', 'title']