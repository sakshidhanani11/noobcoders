# models.py
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    sensor_type = Column(String, index=True)  # e.g., tide, weather, salinity
    source = Column(String, default="unknown")  # e.g., tide_gauge_1
    values = Column(JSON)  # store raw payload
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String)
    severity = Column(String)
    message = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
