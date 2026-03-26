from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .utils import predict
from predictor.models import CustomUser

# GLOBAL VARIABLE (temporary storage)
latest_data = {}


# =========================
# 🔐 LOGIN VIEW
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        print("USERNAME:", username)
        print("PASSWORD:", password)

        user = authenticate(request, username=username, password=password)

        print("AUTH USER:", user)   # 🔥 IMPORTANT

        if user is not None:
            if not user.is_approved:
                return render(request, 'core/login.html', {
                    'error': 'Access not approved yet.'
                })

            login(request, user)

            if user.is_superuser:
                return redirect('admin_panel')
            else:
                return redirect('dashboard')

        else:
            return render(request, 'core/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'core/login.html')

# =========================
# 🚪 LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# 🌐 LANDING PAGE
# =========================
def landing_view(request):
    return render(request, 'core/landing.html')


# =========================
# 📨 REQUEST ACCESS
# =========================
def request_access(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')

        CustomUser.objects.create_user(
            username=name,
            email=email,
            password=password,
            role=role,
            is_approved=False
        )

        return redirect('login')

    return render(request, 'core/request.html')


# =========================
# 🧠 DASHBOARD (ML)
# =========================
@login_required
def dashboard(request):
    print("AUTH:", request.user.is_authenticated)
    print("USER:", request.user)
    global latest_data

    if request.method == "POST":
        file = request.FILES.get('file')

        if file:
            result = predict(file)

            latest_data = {
                "cycles": result,
                "health": "Good" if result > 100 else "Warning" if result > 50 else "Critical",
                "vibration": round(0.2 + (150 - result) * 0.002, 2),
                "pressure": 60 + (result % 10),
                "fuel_flow": 8000 + (result * 10),
            }

            # 🎨 Color logic
            if latest_data["health"] == "Good":
                latest_data["color"] = "#4ade80"
            elif latest_data["health"] == "Warning":
                latest_data["color"] = "#facc15"
            else:
                latest_data["color"] = "#ef4444"

    return render(request, "core/dashboard.html", latest_data)


# =========================
# 📊 OTHER PAGES
# =========================
@login_required
def fleet(request):
    return render(request, "core/fleet.html", latest_data)


@login_required
def maintenance(request):
    return render(request, "core/maintenance.html", latest_data)


@login_required
def health(request):
    return render(request, "core/health.html", latest_data)


# =========================
# 🛡️ ADMIN PANEL
# =========================
@login_required
def admin_panel(request):

    # 🔥 DEBUG START
    print("USER:", request.user)
    print("AUTH:", request.user.is_authenticated)
    print("SUPER:", request.user.is_superuser)
    # 🔥 DEBUG END

    if not request.user.is_superuser:
        return redirect('dashboard')

    users = CustomUser.objects.filter(is_approved=False)

    return render(request, "core/admin_panel.html", {
        "users": users
    })

# =========================
# ✅ APPROVE USER
# =========================
@require_POST
@login_required
def approve_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()

    messages.success(request, f"{user.username} approved")
    return redirect('admin_panel')


# =========================
# ❌ REJECT USER
# =========================
@require_POST
@login_required
def reject_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()

    messages.error(request, f"{user.username} rejected")
    return redirect('admin_panel')