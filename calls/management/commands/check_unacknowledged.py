from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from calls.models import Room  # ✅ correct
 # change Patient -> Room

class Command(BaseCommand):
    help = 'Send notifications for rooms not acknowledged in 3 minutes'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        threshold = now - timedelta(minutes=3)
        unack_rooms = Room.objects.filter(
            acknowledged=False,
            created_at__lte=threshold
        )

        channel_layer = get_channel_layer()

        for room in unack_rooms:
            content = {
                "room_no": room.room_no,
                "message": f"Room {room.room_no} not acknowledged in 3 minutes"
            }
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {"type": "notify", "content": content}
            )
            self.stdout.write(self.style.SUCCESS(f"Notification sent for room {room.room_no}"))
