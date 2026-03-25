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

@login_required
def dashboard(request):
    result = None

    if request.method == "POST" and request.FILES.get('file'):
        file = request.FILES['file']
        result = predict(file)

    return render(request, "core/dashboard.html", {"result": result})
def logout_view(request):
    logout(request)
    return redirect('/login/')

from django.shortcuts import render

def landing_view(request):
    return render(request, 'core/landing.html')
