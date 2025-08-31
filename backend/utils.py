# utils.py
import os
import json
import asyncio
import httpx
from twilio.rest import Client
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
SMS_RECIPIENT = os.getenv("SMS_RECIPIENT")  # comma separated
WS_BROADCAST_URL = os.getenv("WS_BROADCAST_URL", "ws://websocket:8001")  # placeholder

def send_sms_via_twilio(body, to):
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM):
        print("Twilio not configured.")
        return
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(body=body, from_=TWILIO_FROM, to=to)
    return message.sid

def send_sms_if_needed(alert_id, prob):
    # simple: notify admin recipients when high
    if prob < 0.7: return
    recipients = (SMS_RECIPIENT or "").split(",")
    for r in recipients:
        if r.strip():
            send_sms_via_twilio(f"ALERT {alert_id}: coastal threat prob {prob:.2f}", r.strip())

# simple broadcast using HTTP POST to websocket service (or you can integrate uvicorn websockets on same app)
def broadcast_alert(payload: dict):
    # If you set up a separate websocket server, you can POST to it; here we just print.
    print("Broadcasting alert:", payload)
    # In production, connect to the websockets or use Redis pub/sub
