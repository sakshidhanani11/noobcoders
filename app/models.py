# app/models.py
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    sensor_type = Column(String, index=True)  # e.g., tide, weather, salinity
    source = Column(String, default="unknown")  # e.g., tide_gauge_1
    values = Column(JSON)  # store raw payload (e.g., {"sea_level": 1.2, "wind_speed": 30})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String) # e.g., "coastal_threat"
    severity = Column(String)   # e.g., "high", "medium", "low"
    message = Column(String)
    payload = Column(JSON)      # The sensor data that triggered the alert
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Example User model for demonstration
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)