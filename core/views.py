from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .utils import predict   # ✅ correct import

# GLOBAL VARIABLE (for now - simple approach)
latest_data = {}


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid username or password'})

    return render(request, 'core/login.html')


@login_required
def dashboard(request):
    global latest_data

    if request.method == "POST":
        file = request.FILES.get('file')

        if file:
            result = predict(file)

            print("Prediction:", result)

            # 🔥 STORE DATA FOR ALL PAGES
            latest_data = result

    return render(request, "core/dashboard.html", latest_data)


@login_required
def fleet(request):
    return render(request, "core/fleet.html", latest_data)


@login_required
def maintenance(request):
    return render(request, "core/maintenance.html", latest_data)


@login_required
def health(request):
    return render(request, "core/health.html", latest_data)


def logout_view(request):
    logout(request)
    return redirect('/login/')


def landing_view(request):
    return render(request, 'core/landing.html')