# app/routes/alerts.py
from flask import Blueprint, request, jsonify
from ..database import SessionLocal
from .. import models
from ..schemas import AlertOut
from typing import List

# Create a Blueprint for alerts routes
alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@alerts_bp.route("/", methods=["GET"])
def list_alerts():
    """API endpoint to list recent alerts."""
    db = next(get_db()) # Get a database session
    limit = request.args.get('limit', 50, type=int)

    # Query alerts, order by creation time descending, and limit
    alerts = db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(limit).all()

    # Convert SQLAlchemy objects to Pydantic models for consistent output
    # and proper serialization (e.g., datetime to ISO string)
    response_alerts: List[AlertOut] = []
    for alert in alerts:
        response_alerts.append(AlertOut(
            id=alert.id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            payload=alert.payload,
            created_at=alert.created_at.isoformat()
        ))

    return jsonify([alert.model_dump() for alert in response_alerts]), 200 # Use model_dump() for Pydantic v2