from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.messages.models import Message
from apps.messages.push import push_message_to_user, build_message_payload


@receiver(post_save, sender=Message)
def auto_push_message(sender, instance, created, **kwargs):
    """新消息创建后自动通过 WebSocket 推送给用户。"""
    if created and instance.user_id:
        push_message_to_user(instance.user_id, build_message_payload(instance))