# calls/utils.py
import json
import requests
from django.conf import settings

def send_webhook_notification(call):
    payload = {
        "room_no": call.room.room_no,
        "call_from": call.call_from,
        "created_at": call.created_at.isoformat(),
        "status": "new_call"
    }

    # Use your same backend’s public URL (Render URL)
    webhook_url = "https://nursecallsystem.onrender.com/api/webhook/"

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Webhook send failed: {e}")
