import csv
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

# PDF Generation Imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .utils import predict
from predictor.models import CustomUser

# =========================
# 🔐 LOGIN VIEW
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_approved:
                return render(request, 'core/login.html', {
                    'error': 'Access not approved yet. Please wait for administrator validation.'
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
    # Clears session data on logout
    if 'engine_data' in request.session:
        del request.session['engine_data']
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

        if CustomUser.objects.filter(username=name).exists():
            messages.error(request, f"The name '{name}' is already registered.")
            return render(request, 'core/request.html')

        try:
            CustomUser.objects.create_user(
                username=name,
                email=email,
                password=password,
                role=role,
                is_approved=False
            )

            try:
                send_mail(
                    subject=f"🚀 NEW ACCESS REQUEST: {name}",
                    message=f"A new user ({name}) has requested access to AERO_CORE.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['mallikarjunpx@gmail.com'],
                    fail_silently=True,
                )
            except:
                pass 

            messages.success(request, "Request submitted successfully.")
            return render(request, 'core/request.html')

        except Exception as e:
            messages.error(request, f"System Error: {str(e)}")
            return render(request, 'core/request.html')

    return render(request, 'core/request.html')

# =========================
# 🧠 DASHBOARD (ML)
# =========================
@login_required
def dashboard(request):
    # Retrieve existing data from session if it exists
    display_data = request.session.get('engine_data', {}) 

    if request.method == "POST":
        file = request.FILES.get('file')
        if file:
            result = predict(file)
            
            # Prepare the result dictionary
            engine_results = {
                "cycles": result,
                "health": "Good" if result > 100 else "Warning" if result > 50 else "Critical",
                "vibration": round(0.2 + (150 - result) * 0.002, 2),
                "pressure": 60 + (result % 10),
                "fuel_flow": 8000 + (result * 10),
            }
            
            # Assign color based on health
            if engine_results["health"] == "Good":
                engine_results["color"] = "#4ade80"
            elif engine_results["health"] == "Warning":
                engine_results["color"] = "#facc15"
            else:
                engine_results["color"] = "#ef4444"
            
            # Store in session so it survives page navigation
            request.session['engine_data'] = engine_results
            display_data = engine_results
    
    return render(request, "core/dashboard.html", display_data)

# =========================
# 📊 ANALYTICS PAGES
# =========================
@login_required
def fleet(request):
    data = request.session.get('engine_data', {})
    return render(request, "core/fleet.html", data)

@login_required
def maintenance(request):
    data = request.session.get('engine_data', {})
    return render(request, "core/maintenance.html", data)

@login_required
def health(request):
    data = request.session.get('engine_data', {})
    return render(request, "core/health.html", data)

# =========================
# 📥 EXPORT PDF REPORT
# =========================
@login_required
def export_pdf(request):
    # Fetch data from session
    data = request.session.get('engine_data', {})
    
    if not data:
        return HttpResponse("No engine telemetry data found to export.", status=400)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="AeroCore_Report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    
    # Logo Positioning
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'images', 'logo.png') 
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 480, 730, width=60, height=60, mask='auto')

    # Header & Lines
    p.setFont("Helvetica-Bold", 20)
    p.setStrokeColorRGB(1, 0.72, 0.45) 
    p.drawString(100, 750, "AERO_CORE DIAGNOSTIC REPORT")
    p.setStrokeColorRGB(0.3, 0.3, 0.3)
    p.line(100, 735, 500, 735)
    
    # Summary Content
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 700, "Engine Performance Summary:")
    
    p.setFont("Helvetica", 12)
    y_position = 670
    
    data_points = [
        f"• Remaining Useful Life: {data.get('cycles', '--')} CYCLES",
        f"• System Health Status: {data.get('health', 'No Data')}",
        f"• Core Vibration: {data.get('vibration', '--')} ips",
        f"• Oil Pressure: {data.get('pressure', '--')} psi",
        f"• Fuel Flow: {data.get('fuel_flow', '--')} pph"
    ]

    for line in data_points:
        p.drawString(120, y_position, line)
        y_position -= 25 
    
    p.showPage()
    p.save()
    return response

# =========================
# 🛡️ ADMIN PANEL
# =========================
@login_required
def admin_panel(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    status_filter = request.GET.get('filter')
    if status_filter == 'granted':
        users = CustomUser.objects.filter(is_approved=True, is_superuser=False)
    elif status_filter == 'pending':
        users = CustomUser.objects.filter(is_approved=False)
    else:
        users = CustomUser.objects.filter(is_superuser=False)

    return render(request, "core/admin_panel.html", {
        "users": users,
        "current_filter": status_filter
    })

@require_POST
@login_required
def approve_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()

    # Define the professional message
    login_url = request.build_absolute_uri('/') # Points to your login page
    
    subject = "Access Granted: AERO_CORE System"
    message = (
        f"Hello {user.username},\n\n"
        f"Your request for access to the AERO_CORE Predictive Intelligence platform for your "
        f"{user.email} account has been approved.\n\n"
        f"Follow this link to log in and access your diagnostic dashboard:\n"
        f"{login_url}\n\n"
        f"If you did not request this access or believe this is an error, please contact "
        f"system security immediately.\n\n"
        f"Thanks,\n"
        f"The AERO_CORE Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False, 
        )
    except Exception as e:
        print(f"Email Error: {e}")

    messages.success(request, f"Access for {user.username} has been provisioned.")
    return redirect('admin_panel')

@require_POST
@login_required
def reject_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.error(request, f"{user.username} rejected.")
    return redirect('admin_panel')

@login_required
def export_users(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="aero_users_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Role', 'Status'])

    users = CustomUser.objects.filter(is_superuser=False)
    for user in users:
        status = "Access Granted" if user.is_approved else "Pending"
        writer.writerow([user.username, user.email, user.role, status])

    return response