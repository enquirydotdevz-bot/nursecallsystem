from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Call
from .utils import send_webhook_notification

@receiver(post_save, sender=Call)
def call_created_handler(sender, instance, created, **kwargs):
    if created:
        send_webhook_notification(instance)
