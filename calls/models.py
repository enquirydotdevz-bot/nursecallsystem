from django.db import models
from django.utils import timezone
import random


class Room(models.Model):
    room_no = models.CharField(max_length=10, unique=True)
    acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_no}"

    @staticmethod
    def create_random_rooms(n=20):
        """Generate N random rooms (100–999)."""
        for i in range(n):
            room_no = str(random.randint(100, 999))
            Room.objects.get_or_create(room_no=room_no)


from django.db import models
from django.utils import timezone

class Call(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    call_from = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    acknowledged_at = models.DateTimeField(null=True, blank=True)
    attended_at = models.DateTimeField(null=True, blank=True)

    response_time_seconds = models.IntegerField(null=True, blank=True)
    attend_delay_seconds = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate response time
        if self.acknowledged_at and not self.response_time_seconds:
            self.response_time_seconds = int((self.acknowledged_at - self.created_at).total_seconds())
        # Calculate attend delay
        if self.attended_at and not self.attend_delay_seconds:
            if self.acknowledged_at:
                self.attend_delay_seconds = int((self.attended_at - self.acknowledged_at).total_seconds())
            else:
                self.attend_delay_seconds = int((self.attended_at - self.created_at).total_seconds())
        super().save(*args, **kwargs)
