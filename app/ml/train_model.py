# app/ml/train_model.py
import numpy as np
import tensorflow as tf
import os

def synth_data(n=2000):
    # features: sea_level, wind_speed, salinity, temp, chl_a
    sea = np.random.normal(0.5, 0.5, n)
    wind = np.abs(np.random.normal(10, 8, n))
    sal = np.random.normal(34, 2, n)
    temp = np.random.normal(25, 3, n)
    chl = np.abs(np.random.normal(0.5, 0.4, n))

    X = np.stack([sea, wind, sal, temp, chl], axis=1)
    # target: probability of threat — synthetic rule
    y = (sea*0.6 + (wind/50)*0.3 + (chl/2)*0.4) / 2.0
    y = np.clip(y, 0, 1) # Ensure probability is between 0 and 1
    return X, y

def build_and_train(save_path="app/ml/saved_model.keras"):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    X, y = synth_data()
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(5,)), # 5 features
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid") # Output a probability
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["AUC"])
    model.fit(X, y, epochs=10, batch_size=32, validation_split=0.1, verbose=1)
    model.save(save_path)
    print("Saved model to", save_path)

if __name__ == "__main__":
    build_and_train()