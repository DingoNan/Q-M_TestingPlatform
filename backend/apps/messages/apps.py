from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.messages'
    label = 'app_messages'
    verbose_name = '消息通知'

    def ready(self):
        import apps.messages.signals  # noqa