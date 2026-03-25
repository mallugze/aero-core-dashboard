import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Load model
model = load_model('turbofan_model.h5')

# Load scaler
scaler = joblib.load('scaler.pkl')

def predict(data):
    sequence_length = 40

    sequences = []

    for i in range(len(data) - sequence_length):
        sequences.append(data[i:i+sequence_length])

    sequences = np.array(sequences)

    # Scale
    sequences = scaler.transform(
        sequences.reshape(-1, sequences.shape[-1])
    ).reshape(sequences.shape)

    # Predict
    prediction = model.predict(sequences)

    return int(prediction[-1][0])