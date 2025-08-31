# main.py
from flask import Flask, jsonify
from .routes.ingest import ingest_bp
from .routes.alerts import alerts_bp
from .database import Base, engine, SessionLocal
from . import models # Import models to ensure they are registered with Base
import os
import asyncio # Required for background tasks in utils.py

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_very_secret_key_for_dev') # For session management, etc.

# Register blueprints
app.register_blueprint(ingest_bp)
app.register_blueprint(alerts_bp)

# Create database tables if they don't exist
# In a production environment, you'd use migrations (e.g., Alembic)
with app.app_context():
    Base.metadata.create_all(bind=engine)
    print("Database tables checked/created.")

@app.route("/")
def root():
    return jsonify({"service": "coastal-threat-backend", "status": "ok"})

if __name__ == "__main__":
    try:
        print("[INFO] Starting backend application...")
        # Train the ML model if it doesn't exist
        from .ml.train_model import build_and_train
        if not os.path.exists("app/ml/saved_model"):
            print("[INFO] ML model not found. Training a new one...")
            build_and_train()
        else:
            print("[INFO] ML model found. Skipping training.")

        print("[INFO] Running Flask app on http://0.0.0.0:5000 ...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"[ERROR] Exception during startup: {e}")