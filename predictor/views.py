import pandas as pd
import random
from django.shortcuts import render
from .ml import predict

def upload_predict(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        df = pd.read_csv(file)

        # ===== ENGINE NAME =====
        engine_models = ["GE90", "CFM56", "PW1000G", "TrentXWB"]
        engine_id = int(df.iloc[0, 0])
        engine_name = f"{random.choice(engine_models)}-{engine_id}"

        # ===== ML PREDICTION =====
        # Drop unwanted columns (example)
        selected_columns = df.columns[2:19]
        data = df[selected_columns].values
        cycles = int(predict(data))

        # ===== HEALTH STATUS =====
        if cycles > 120:
            health = "Healthy"
            color = "green"
        elif cycles > 60:
            health = "Warning"
            color = "orange"
        else:
            health = "Critical"
            color = "red"

        # ===== METRICS =====
        vibration = round(random.uniform(0.2, 1.5), 2)
        pressure = random.randint(40, 90)
        fuel_flow = random.randint(5000, 9000)

        # ===== MAINTENANCE =====
        if cycles < 50:
            action = "Immediate inspection required"
        elif cycles < 100:
            action = "Schedule maintenance soon"
        else:
            action = "No action needed"

        # ===== CONTEXT =====
        context = {
            "engine_name": engine_name,
            "cycles": cycles,
            "health": health,
            "color": color,
            "vibration": vibration,
            "pressure": pressure,
            "fuel_flow": fuel_flow,
            "action": action
        }

    return render(request, 'core/dashboard.html', context)