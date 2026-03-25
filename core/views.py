from unittest import result

from django import core
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout



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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .utils import predict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import predict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from predictor.models import predict   

@login_required
def dashboard(request):
    context = {}

    if request.method == "POST":
        file = request.FILES.get('file')

        if file:
            result = predict(file)

            print("Prediction:", result)   # debug

            context['rul'] = result   # ✅ THIS LINE WAS MISSING

    return render(request, "core/dashboard.html", context) 
def logout_view(request):
    logout(request)
    return redirect('/login/')

from django.shortcuts import render

def landing_view(request):
    return render(request, 'core/landing.html')
print("Prediction:", result)
from django.contrib.auth.decorators import login_required

@login_required
def fleet(request):
    return render(request, "core/fleet.html")

@login_required
def maintenance(request):
    return render(request, "core/maintenance.html")

@login_required
def health(request):
    return render(request, "core/health.html")