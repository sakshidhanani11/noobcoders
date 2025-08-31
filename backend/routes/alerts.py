# alerts.py
from fastapi import APIRouter, Depends
from ..database import SessionLocal
from sqlalchemy.orm import Session
from .. import models
from ..schemas import AlertOut
from typing import List

router = APIRouter(prefix="/alerts", tags=["alerts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[AlertOut])
def list_alerts(limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(limit)
    return q.all()
