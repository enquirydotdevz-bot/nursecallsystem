import requests
import logging

logger = logging.getLogger(__name__)

def send_webhook(payload):
    WEBHOOK_URL = "https://webhook.site/your-test-url"  # replace this with your actual webhook endpoint

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        logger.info(f"Webhook sent successfully! Status: {response.status_code}")
        logger.info(f"Response: {response.text}")
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
