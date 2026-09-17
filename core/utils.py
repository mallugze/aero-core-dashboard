import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
import os
from django.conf import settings

# Get paths from settings/base dir
BASE_DIR = settings.BASE_DIR
MODEL_PATH = os.path.join(BASE_DIR, 'turbofan_model.h5')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')

# Load model and scaler once when the server starts
try:
    model = load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("[INFO] ML Model and Scaler loaded successfully.")
except Exception as e:
    print(f"[ERROR] Error loading ML files: {e}")
    model = None
    scaler = None

def predict(file):
    if model is None or scaler is None:
        return "Error: Model not loaded"

    try:
        # Load the uploaded CSV
        df = pd.read_csv(file)

        # Step 1: Select only the columns the scaler was trained on
        # This prevents "feature mismatch" errors
        required_cols = scaler.feature_names_in_
        X = df[required_cols]

        # Step 2: Scale the data
        X_scaled = scaler.transform(X)

        # Step 3: Create sequences (Window size = 40)
        sequence_length = 40
        if len(X_scaled) < sequence_length:
            return 0  # Not enough data for a prediction

        sequences = []
        for i in range(len(X_scaled) - sequence_length + 1):
            sequences.append(X_scaled[i : i + sequence_length])

        X_seq = np.array(sequences)

        # Step 4: Run Prediction
        prediction = model.predict(X_seq)

        # Step 5: Return the last RUL (Remaining Useful Life) value
        return int(max(0, prediction[-1][0]))

    except Exception as e:
        print(f"[ERROR] Prediction Error: {e}")
        return 0