import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
import os

# Base path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load model and scaler
model_path = os.path.join(BASE_DIR, 'turbofan_model.h5')
scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')

model = load_model(model_path)
scaler = joblib.load(scaler_path)


def predict(file):
    df = pd.read_csv(file)

    # Step 1: select correct columns
    required_cols = scaler.feature_names_in_
    df = df[required_cols]

    # Step 2: scale
    X = scaler.transform(df)

    # Step 3: create sequences (WINDOW SIZE = 40)
    sequence_length = 40
    sequences = []

    for i in range(len(X) - sequence_length):
        sequences.append(X[i:i + sequence_length])

    X_seq = np.array(sequences)

    # Step 4: predict
    prediction = model.predict(X_seq)

    # Step 5: return last prediction
    return int(prediction[-1][0])