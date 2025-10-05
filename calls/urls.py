from django.urls import path
from . import views

urlpatterns = [
    # Calls
    path("call/", views.create_call, name="create_call"),
    path("call/<int:pk>/ack/", views.acknowledge_call, name="ack_call"),
    path("call/<int:pk>/attend/", views.attend_call, name="attend_call"),

    # Extra APIs
    path("calls/unacknowledged/", views.unacknowledged_calls, name="unack_calls"),
    path("rooms/create-random/", views.create_random_rooms, name="create_random_rooms"),
    path("rooms/", views.list_rooms, name="list_rooms"),
]
