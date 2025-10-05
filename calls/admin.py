from django.contrib import admin
from .models import Call, Room


from django.contrib import admin
from .models import Call

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "call_from", "created_at", "acknowledged_at", "attended_at", "response_time_seconds", "attend_delay_seconds")

    def save_model(self, request, obj, form, change):
        obj.save()  # triggers the save() method with calculations



@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_no", "acknowledged", "created_at")
