from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# app/utils.py
import os
import json
import asyncio
import httpx # Make sure httpx is in your requirements.txt
from twilio.rest import Client

# Load environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
SMS_RECIPIENT = os.getenv("SMS_RECIPIENT")  # comma separated list of phone numbers

# This URL points to the HTTP endpoint of your separate WebSocket server.
# In a Docker Compose setup, 'websocket' would be the service name.
# If running locally, it might be 'http://localhost:8002'
HTTP_BROADCAST_URL = os.getenv("HTTP_BROADCAST_URL", "http://localhost:8002/broadcast")

def send_sms_via_twilio(body: str, to: str):
    """Sends an SMS message using Twilio."""
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM):
        print("Twilio credentials not configured. Skipping SMS.")
        return None
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(body=body, from_=TWILIO_FROM, to=to)
        print(f"SMS sent to {to}: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending SMS to {to}: {e}")
        return None

def send_sms_if_needed(alert_id: int, prob: float):
    """Sends SMS to recipients if threat probability is high."""
    # Only send SMS for high severity alerts
    if prob < 0.7:
        return

    recipients = [r.strip() for r in (SMS_RECIPIENT or "").split(",") if r.strip()]
    for r in recipients:
        send_sms_via_twilio(f"ALERT {alert_id}: Coastal threat probability {prob:.2f}", r)

async def _send_to_websocket_server(payload: dict):
    """Internal helper to send data to the WebSocket server's HTTP endpoint."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(HTTP_BROADCAST_URL, json=payload, timeout=5)
            response.raise_for_status() # Raise an exception for 4xx/5xx responses
            print(f"Successfully sent to WebSocket server: {payload.get('type', 'unknown')}")
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} from {exc.request.url!r}: {exc.response.text}")
    except Exception as e:
        print(f"Unexpected error sending to WebSocket server: {e}")

def broadcast_alert(payload: dict):
    """Broadcasts an alert message to connected WebSocket clients."""
    payload["type"] = "alert" # Add type for frontend to distinguish
    # Use asyncio.create_task to run the async HTTP request in the background
    asyncio.create_task(_send_to_websocket_server(payload))
    print("Scheduled alert broadcast:", payload)

def broadcast_reading(payload: dict):
    """Broadcasts a sensor reading message to connected WebSocket clients."""
    payload["type"] = "reading" # Add type for frontend to distinguish
    asyncio.create_task(_send_to_websocket_server(payload))
    print("Scheduled reading broadcast:", payload)