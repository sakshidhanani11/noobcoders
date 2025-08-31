# schemas.py
from pydantic import BaseModel
from typing import Dict, Any, Optional

class ReadingIn(BaseModel):
    sensor_type: str
    source: str
    values: Dict[str, Any]
    timestamp: Optional[str] = None

class AlertOut(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    payload: Dict[str, Any]
    created_at: str
