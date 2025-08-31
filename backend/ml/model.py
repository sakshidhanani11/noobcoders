# model.py
import tensorflow as tf
import numpy as np
import os

MODEL_PATH = os.getenv("MODEL_PATH", "app/ml/saved_model")

class CoastalThreatModel:
    def __init__(self, model_path=MODEL_PATH):
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = None

    def predict(self, features: dict):
        # Convert features dict to vector. This depends on your trained model.
        # Example: features: {"sea_level": 1.2, "wind_speed": 30, "chl_a": 0.8}
        keys = ["sea_level", "wind_speed", "salinity", "temp", "chl_a"]
        x = np.array([[features.get(k, 0.0) for k in keys]])
        if self.model:
            probs = self.model.predict(x)
            # suppose model outputs [threat_probability]
            return float(probs[0][0])
        else:
            # fallback heuristic
            score = (features.get("sea_level",0)*0.5 + features.get("wind_speed",0)*0.3 + features.get("chl_a",0)*0.2)
            return min(1.0, score/100.0)
