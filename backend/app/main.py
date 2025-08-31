# main.py
from fastapi import FastAPI
from .routes import alerts
from .database import Base, engine
from . import ingest, models
import os

app = FastAPI(title="Coastal Threat Alert System")

# create tables (for dev)
Base.metadata.create_all(bind=engine)

app.include_router(ingest.router)
app.include_router(alerts.router)

@app.get("/")
def root():
    return {"service": "coastal-threat-backend", "status": "ok"}
