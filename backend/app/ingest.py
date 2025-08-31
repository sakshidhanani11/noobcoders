# ingest.py
from fastapi import APIRouter, Depends, BackgroundTasks
from .schemas import ReadingIn
from .database import SessionLocal
from . import models
from .ml.model import CoastalThreatModel
from sqlalchemy.orm import Session
import json
from .utils import broadcast_alert, send_sms_if_needed

router = APIRouter(prefix="/ingest", tags=["ingest"])
model = CoastalThreatModel()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/reading")
async def ingest_reading(reading: ReadingIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_reading = models.SensorReading(
        sensor_type=reading.sensor_type,
        source=reading.source,
        values=reading.values
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    # run threat prediction (synchronous quick call), but send notifications in background
    prob = model.predict(reading.values)
    # define thresholds
    if prob > 0.7:
        alert = models.Alert(alert_type="coastal_threat", severity="high",
                             message=f"High coastal threat detected ({prob:.2f})", payload=reading.values)
        db.add(alert); db.commit(); db.refresh(alert)
        background_tasks.add_task(broadcast_alert, {
            "id": alert.id,
            "type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "payload": alert.payload
        })
        background_tasks.add_task(send_sms_if_needed, alert.id, prob)
    elif prob > 0.4:
        alert = models.Alert(alert_type="coastal_threat", severity="medium",
                             message=f"Medium threat detected ({prob:.2f})", payload=reading.values)
        db.add(alert); db.commit(); db.refresh(alert)
        background_tasks.add_task(broadcast_alert, {
            "id": alert.id,
            "type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "payload": alert.payload
        })

    return {"status": "ok", "probability": prob}
