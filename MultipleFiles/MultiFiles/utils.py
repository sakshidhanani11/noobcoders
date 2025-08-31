# MultipleFiles/utils.py
import os
import json
import asyncio
import httpx # Make sure httpx is in your requirements.py
from twilio.rest import Client

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
SMS_RECIPIENT = os.getenv("SMS_RECIPIENT")  # comma separated

# This URL points to the HTTP endpoint of our websocket_server.py
# which will then broadcast the message to all connected WebSocket clients.
# 'websocket' is the service name in docker-compose.yml
HTTP_BROADCAST_URL = os.getenv("HTTP_BROADCAST_URL", "http://websocket:8002")

def send_sms_via_twilio(body, to):
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM):
        print("Twilio not configured. Skipping SMS.")
        return
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(body=body, from_=TWILIO_FROM, to=to)
        print(f"SMS sent to {to}: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

def send_sms_if_needed(alert_id, prob):
    # simple: notify admin recipients when high
    if prob < 0.7: return
    recipients = (SMS_RECIPIENT or "").split(",")
    for r in recipients:
        if r.strip():
            send_sms_via_twilio(f"ALERT {alert_id}: coastal threat prob {prob:.2f}", r.strip())

async def _send_to_websocket_server(payload: dict):
    """Internal helper to send data to the WebSocket server's HTTP endpoint."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(HTTP_BROADCAST_URL, json=payload, timeout=5)
            response.raise_for_status() # Raise an exception for 4xx/5xx responses
            print(f"Successfully sent to WebSocket server: {payload['type']}")
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
    except Exception as e:
        print(f"Unexpected error sending to WebSocket server: {e}")

def broadcast_alert(payload: dict):
    """Broadcasts an alert message to connected WebSocket clients."""
    # We need to run this in the event loop, but from a synchronous context (FastAPI route)
    # So, we use asyncio.create_task or similar.
    # For simplicity in this example, we'll assume it's called from a background task.
    # The ingest.py already uses background_tasks.add_task, which is good.
    payload["type"] = "alert" # Add type for frontend to distinguish
    asyncio.create_task(_send_to_websocket_server(payload))
    print("Scheduled alert broadcast:", payload)

def broadcast_reading(payload: dict):
    """Broadcasts a sensor reading message to connected WebSocket clients."""
    payload["type"] = "reading" # Add type for frontend to distinguish
    asyncio.create_task(_send_to_websocket_server(payload))
    print("Scheduled reading broadcast:", payload)
