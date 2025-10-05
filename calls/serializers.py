from rest_framework import serializers
from .models import Room, Call


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["room_no", "acknowledged", "created_at"]


class CallSerializer(serializers.ModelSerializer):
    # expose room_no instead of internal id
    room_no = serializers.CharField(source="room.room_no", read_only=True)

    class Meta:
        model = Call
        fields = [
            "id",                   # keep for API updates
            "room",                 # ForeignKey for POSTs
            "room_no",              # exposed to frontend
            "call_from",
            "created_at",
            "acknowledged_at",
            "attended_at",
            "response_time_seconds",
            "attend_delay_seconds",
        ]
        read_only_fields = [
            "id",
            "room_no",
            "created_at",
            "acknowledged_at",
            "attended_at",
            "response_time_seconds",
            "attend_delay_seconds",
        ]
