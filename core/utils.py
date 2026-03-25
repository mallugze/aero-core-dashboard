import numpy as np
import joblib
from tensorflow.keras.models import load_model
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

scaler = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))
model = load_model(os.path.join(BASE_DIR, "turbofan_model.h5"))

def predict(file):
    return 120