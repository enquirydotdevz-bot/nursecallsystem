from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Call

@shared_task
def notify_unacknowledged_calls():
    threshold = timezone.now() - timedelta(minutes=3)
    unacked_calls = Call.objects.filter(acknowledged_at__isnull=True, created_at__lte=threshold)
    channel_layer = get_channel_layer()

    for call in unacked_calls:
        content = {
            "event": "call_unacknowledged",
            "room_no": call.room.room_no,
            "created_at": call.created_at.isoformat()
        }
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {"type": "notify", "content": content}
        )
