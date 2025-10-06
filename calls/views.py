import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.views import APIView  
from .models import Call, Room
from .serializers import CallSerializer, RoomSerializer
from .webhooks import send_webhook

# ✅ Use Django’s logger (shows in Render logs)
logger = logging.getLogger(__name__)


class CallViewSet(APIView):
    def post(self, request):
        logger.info("📞 Received new call POST request")
        serializer = CallSerializer(data=request.data)

        if serializer.is_valid():
            call = serializer.save()

            payload = {
                "id": call.id,
                "room_no": call.room.room_no if call.room else None,
                "call_from": call.call_from,
                "created_at": str(call.created_at),
                "status": "New call received"
            }

            # ✅ Log & send webhook
            logger.info(f"🚀 Sending webhook for new call: {payload}")
            send_webhook(payload)

            logger.info(f"✅ Call created successfully (ID: {call.id})")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"❌ Invalid call data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_ws_notification(event_type, call):
    """Helper: push real-time WebSocket notifications"""
    channel_layer = get_channel_layer()
    content = {
        "event": event_type,
        "room_no": call.room.room_no,
        "call_from": call.call_from,
        "created_at": call.created_at.isoformat(),
        "acknowledged_at": call.acknowledged_at.isoformat() if call.acknowledged_at else None,
        "attended_at": call.attended_at.isoformat() if call.attended_at else None,
    }

    logger.info(f"📡 Sending WebSocket notification: {content}")
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {"type": "notify", "content": content}
    )


@api_view(["POST"])
def create_call(request):
    logger.info("📞 API /create_call triggered")
    serializer = CallSerializer(data=request.data)
    if serializer.is_valid():
        call = serializer.save()
        logger.info(f"✅ Call created with ID: {call.id}")
        send_ws_notification("call_created", call)
        send_webhook({
            "event": "call_created",
            "id": call.id,
            "room_no": call.room.room_no if call.room else None,
            "created_at": str(call.created_at)
        })
        return Response(CallSerializer(call).data, status=status.HTTP_201_CREATED)
    logger.error(f"❌ Invalid call data: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def acknowledge_call(request, pk):
    logger.info(f"👩‍⚕️ Nurse acknowledged call ID: {pk}")
    call = get_object_or_404(Call, pk=pk)

    if not call.acknowledged_at:
        call.acknowledged_at = timezone.now()
        call.response_time_seconds = int((call.acknowledged_at - call.created_at).total_seconds())
        call.save()

        logger.info(f"✅ Call acknowledged at {call.acknowledged_at}")
        send_ws_notification("call_acknowledged", call)
        send_webhook({
            "event": "call_acknowledged",
            "id": call.id,
            "acknowledged_at": str(call.acknowledged_at)
        })

    return Response(CallSerializer(call).data, status=status.HTTP_200_OK)


@api_view(["POST"])
def attend_call(request, pk):
    logger.info(f"🚶‍♀️ Nurse attending call ID: {pk}")
    call = get_object_or_404(Call, pk=pk)

    if not call.attended_at:
        call.attended_at = timezone.now()
        if call.acknowledged_at:
            call.attend_delay_seconds = int((call.attended_at - call.acknowledged_at).total_seconds())
        else:
            call.attend_delay_seconds = int((call.attended_at - call.created_at).total_seconds())
        call.save()

        logger.info(f"✅ Call attended at {call.attended_at}")
        send_ws_notification("call_attended", call)
        send_webhook({
            "event": "call_attended",
            "id": call.id,
            "attended_at": str(call.attended_at)
        })

    return Response(CallSerializer(call).data, status=status.HTTP_200_OK)


@api_view(["GET"])
def unacknowledged_calls(request):
    logger.info("📋 Fetching unacknowledged calls list")
    calls = Call.objects.filter(acknowledged_at__isnull=True).order_by("created_at")
    return Response(CallSerializer(calls, many=True).data)


@api_view(["POST"])
def create_random_rooms(request):
    logger.info("🏠 Creating random rooms")
    Room.create_random_rooms(n=20)
    return Response({"message": "20 random rooms created/ensured."}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def list_rooms(request):
    logger.info("📋 Listing all rooms")
    rooms = Room.objects.all().order_by("room_no")
    return Response(RoomSerializer(rooms, many=True).data)


@api_view(["POST"])
def webhook_receiver(request):
    """
    Receives webhook notifications from this or other services
    """
    data = request.data
    logger.info(f"📩 Webhook received: {data}")
    return Response({"status": "received"}, status=status.HTTP_200_OK)
