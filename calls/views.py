from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Call
from .serializers import CallSerializer

from .webhooks import send_webhook

class CallViewSet(APIView):
    def post(self, request):
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

            # Log and send webhook
            send_webhook(payload)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_ws_notification(event_type, call):
    """Helper: push real-time WebSocket notifications"""
    channel_layer = get_channel_layer()
    content = {
        "event": event_type,
        "room_no": call.room.room_no,   # now using FK to Room
        "call_from": call.call_from,
        "created_at": call.created_at.isoformat(),
        "acknowledged_at": call.acknowledged_at.isoformat() if call.acknowledged_at else None,
        "attended_at": call.attended_at.isoformat() if call.attended_at else None,
    }
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {"type": "notify", "content": content}
    )


@api_view(["POST"])
def create_call(request):
    """Webhook: patient presses button -> create call"""
    serializer = CallSerializer(data=request.data)
    if serializer.is_valid():
        call = serializer.save()
        send_ws_notification("call_created", call)
        return Response(CallSerializer(call).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def acknowledge_call(request, pk):
    """Nurse acknowledges"""
    call = get_object_or_404(Call, pk=pk)

    if not call.acknowledged_at:
        call.acknowledged_at = timezone.now()
        call.response_time_seconds = int((call.acknowledged_at - call.created_at).total_seconds())
        call.save()
        send_ws_notification("call_acknowledged", call)

    return Response(CallSerializer(call).data, status=status.HTTP_200_OK)


@api_view(["POST"])
def attend_call(request, pk):
    """Nurse attends patient"""
    call = get_object_or_404(Call, pk=pk)

    if not call.attended_at:
        call.attended_at = timezone.now()
        if call.acknowledged_at:
            call.attend_delay_seconds = int((call.attended_at - call.acknowledged_at).total_seconds())
        else:
            call.attend_delay_seconds = int((call.attended_at - call.created_at).total_seconds())
        call.save()
        send_ws_notification("call_attended", call)

    return Response(CallSerializer(call).data, status=status.HTTP_200_OK)
from .models import Room
from .serializers import RoomSerializer


@api_view(["GET"])
def unacknowledged_calls(request):
    """List all calls not yet acknowledged (for dashboard)."""
    calls = Call.objects.filter(acknowledged_at__isnull=True).order_by("created_at")
    return Response(CallSerializer(calls, many=True).data)


@api_view(["POST"])
def create_random_rooms(request):
    """Generate 20 random rooms if not already created."""
    Room.create_random_rooms(n=20)
    return Response({"message": "20 random rooms created/ensured."}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def list_rooms(request):
    """List all rooms with their current state."""
    rooms = Room.objects.all().order_by("room_no")
    return Response(RoomSerializer(rooms, many=True).data)

# calls/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(["POST"])
def webhook_receiver(request):
    """
    Receives webhook notifications from this or other services
    """
    data = request.data
    print("Webhook received:", data)  # for debugging
    # You can add logic here (store in DB, trigger socket, etc.)
    return Response({"status": "received"}, status=status.HTTP_200_OK)

