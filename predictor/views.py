import pandas as pd
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .ml import predict
from .models import CustomUser


# =========================
# DASHBOARD + ML PREDICTION
# =========================
@login_required
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


# =========================
# CUSTOM ADMIN PANEL
# =========================
@login_required
def admin_panel(request):
    if not request.user.is_superuser:
        return redirect("upload_predict")  # redirect to dashboard

    users = CustomUser.objects.filter(is_approved=False)
    pending_count = users.count()

    return render(request, "core/admin_panel.html", {
        "users": users,
        "pending_count": pending_count
    })


# =========================
# APPROVE USER
# =========================
@require_POST
@login_required
def approve_user(request, user_id):
    if not request.user.is_superuser:
        return redirect("upload_predict")

    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()

    messages.success(request, f"{user.username} approved successfully")
    return redirect("admin_panel")


# =========================
# REJECT USER
# =========================
@require_POST
@login_required
def reject_user(request, user_id):
    if not request.user.is_superuser:
        return redirect("upload_predict")

    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()  # or mark rejected instead

    messages.error(request, f"{user.username} rejected")
    return redirect("admin_panel")