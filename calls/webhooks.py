import requests
import logging

# Use Django's logging system (shows in Render logs)
logger = logging.getLogger(__name__)

def send_webhook(payload):
    WEBHOOK_URL = "https://webhook.site/1f9573c0-a4ba-45c6-85c6-5ed54180fd78"  # replace with your test webhook URL

    logger.info(f"🚀 Sending webhook to {WEBHOOK_URL} with payload: {payload}")

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        logger.info(f"✅ Webhook sent successfully! Status: {response.status_code}")
        logger.info(f"🔁 Webhook response: {response.text[:200]}")  # limit for readability
    except Exception as e:
        logger.error(f"❌ Webhook failed: {e}")
