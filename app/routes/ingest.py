# app/routes/ingest.py
from flask import Blueprint, request, jsonify
from ..schemas import ReadingIn
from ..database import SessionLocal
from .. import models
from ..ml.model import CoastalThreatModel
from ..utils import broadcast_alert, send_sms_if_needed, broadcast_reading
import json
from datetime import datetime

# Create a Blueprint for ingest routes
ingest_bp = Blueprint('ingest', __name__, url_prefix='/ingest')

# Initialize the ML model globally to avoid reloading on each request
model = CoastalThreatModel()

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@ingest_bp.route("/reading", methods=["POST"])
def ingest_reading():
    """API endpoint to ingest sensor readings and predict threat."""
    try:
        # Validate incoming data using Pydantic schema
        reading_data = ReadingIn(**request.json)
    except Exception as e:
        return jsonify({"error": f"Invalid input data: {e}"}), 400

    db = next(get_db()) # Get a database session

    # Save the raw sensor reading to the database
    db_reading = models.SensorReading(
        sensor_type=reading_data.sensor_type,
        source=reading_data.source,
        values=reading_data.values,
        # timestamp is set by server_default=func.now() if not provided
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading) # Get the generated ID and timestamp

    # Broadcast the raw reading to the dashboard for real-time charts
    # Note: Flask's BackgroundTasks are not as direct as FastAPI's.
    # We'll use asyncio.create_task directly in utils.py for simplicity here,
    # assuming an event loop is available (e.g., when running with Gunicorn/ASGI server).
    broadcast_reading({
        "sensor_type": reading_data.sensor_type,
        "source": reading_data.source,
        "values": reading_data.values,
        "timestamp": db_reading.timestamp.isoformat() # Convert datetime to string
    })

    # Run threat prediction
    prob = model.predict(reading_data.values)

    # Define thresholds and create alerts
    alert_message = None
    severity = None

    if prob > 0.7:
        severity = "high"
        alert_message = f"High coastal threat detected ({prob:.2f})"
    elif prob > 0.4:
        severity = "medium"
        alert_message = f"Medium coastal threat detected ({prob:.2f})"

    if alert_message:
        alert = models.Alert(
            alert_type="coastal_threat",
            severity=severity,
            message=alert_message,
            payload=reading_data.values
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Broadcast the alert and send SMS in the background
        broadcast_alert({
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "payload": alert.payload,
            "created_at": alert.created_at.isoformat()
        })
        send_sms_if_needed(alert.id, prob)

    return jsonify({"status": "ok", "probability": prob}), 200