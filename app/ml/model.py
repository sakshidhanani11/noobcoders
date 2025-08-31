# app/ml/model.py
import tensorflow as tf
import numpy as np
import os

# Path to the saved model, configurable via environment variable
MODEL_PATH = os.getenv("MODEL_PATH", "app/ml/saved_model")

class CoastalThreatModel:
    def __init__(self, model_path=MODEL_PATH):
        self.model = None
        if os.path.exists(model_path):
            try:
                self.model = tf.keras.models.load_model(model_path)
                print(f"ML model loaded from {model_path}")
            except Exception as e:
                print(f"Error loading ML model from {model_path}: {e}")
                print("Falling back to heuristic model.")
        else:
            print(f"ML model not found at {model_path}. Falling back to heuristic model.")

    def predict(self, features: dict) -> float:
        # Convert features dict to a numpy array in the expected order
        # Ensure the order matches the training data: sea_level, wind_speed, salinity, temp, chl_a
        keys = ["sea_level", "wind_speed", "salinity", "temp", "chl_a"]
        x = np.array([[features.get(k, 0.0) for k in keys]])

        if self.model:
            try:
                prob = self.model.predict(x, verbose=0) # verbose=0 to suppress output
                return float(prob[0][0]) # Return the probability as a float
            except Exception as e:
                print(f"Error during ML model prediction: {e}. Falling back to heuristic.")

        # Fallback heuristic model if ML model is not loaded or fails
        # This is a simplified rule for demonstration
        sea_level = features.get("sea_level", 0)
        wind_speed = features.get("wind_speed", 0)
        chl_a = features.get("chl_a", 0)

        # Normalize values to contribute to a 0-1 score
        # Assuming typical ranges: sea_level (0-2m), wind_speed (0-50m/s), chl_a (0-2)
        normalized_sea = min(sea_level / 2.0, 1.0)
        normalized_wind = min(wind_speed / 50.0, 1.0)
        normalized_chl = min(chl_a / 2.0, 1.0)

        # Simple weighted sum for heuristic probability
        heuristic_score = (normalized_sea * 0.4 + normalized_wind * 0.3 + normalized_chl * 0.3)
        return min(max(heuristic_score, 0.0), 1.0) # Ensure score is between 0 and 1