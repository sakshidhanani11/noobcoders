# app/schemas.py
from pydantic import BaseModel
from typing import Dict, Any, Optional

class ReadingIn(BaseModel):
    sensor_type: str
    source: str
    values: Dict[str, Any] # e.g., {"sea_level": 1.2, "wind_speed": 30, "salinity": 35, "temp": 28, "chl_a": 0.5}
    timestamp: Optional[str] = None # Optional, backend will set if not provided

class AlertOut(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    payload: Dict[str, Any]
    created_at: str # Will be ISO formatted string