from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import csv
import os
from django.conf import settings
from reportlab.lib.utils import ImageReader

from .utils import predict
from predictor.models import CustomUser

# GLOBAL VARIABLE (temporary storage for ML results)
latest_data = {}

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
    logout(request)
    return redirect('login')

# =========================
# 🌐 LANDING PAGE
# =========================
def landing_view(request):
    return render(request, 'core/landing.html')

# =========================
# 📨 REQUEST ACCESS (With Admin Email Notification)
# =========================
def request_access(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')

        # Create the user in pending status
        CustomUser.objects.create_user(
            username=name,
            email=email,
            password=password,
            role=role,
            is_approved=False
        )

        # 📧 SEND EMAIL TO YOU (The Admin)
        try:
            send_mail(
                subject=f"🚀 NEW ACCESS REQUEST: {name}",
                message=f"Admin Notice,\n\nA new user has requested access to AERO_CORE.\n\nUser: {name}\nEmail: {email}\nRole: {role}\n\nPlease log in to the Admin Panel to approve or reject this request.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['mallikarjunpx@gmail.com'], # Your Super Admin Email
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email Error: {e}")

        messages.success(request, "Request submitted. Admin will notify you via email.")
        return redirect('login')

    return render(request, 'core/request.html')

# =========================
# 🧠 DASHBOARD (ML)
# =========================
@login_required
def dashboard(request):
    global latest_data
    
    # If the user just arrived (GET request), you might want to 
    # show empty values instead of the last person's results.
    display_data = {} 

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
            # Set colors based on health
            if latest_data["health"] == "Good":
                latest_data["color"] = "#4ade80"
            elif latest_data["health"] == "Warning":
                latest_data["color"] = "#facc15"
            else:
                latest_data["color"] = "#ef4444"
            
            display_data = latest_data
    
    # If it's a GET request and you WANT to show previous data, use latest_data
    # If you want it BLANK until upload, use display_data
    return render(request, "core/dashboard.html", display_data)

# =========================
# 📊 ANALYTICS PAGES
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
# 🛡️ ADMIN PANEL (With Filtering)
# =========================
@login_required
def admin_panel(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    # Filtering Logic
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

# =========================
# ✅ APPROVE USER (With User Email Notification)
# =========================
@require_POST
@login_required
def approve_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()

    # 📧 SEND EMAIL TO THE USER
    try:
        send_mail(
            subject="✅ ACCESS GRANTED: AERO_CORE SYSTEM",
            message=f"Greetings {user.username},\n\nYour request for access to the AERO_CORE system has been approved.\n\nYou may now log in to your dashboard.\n\nWelcome aboard.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email Error: {e}")

    messages.success(request, f"{user.username} approved and notified.")
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

    messages.error(request, f"{user.username} access revoked/rejected.")
    return redirect('admin_panel')

# =========================
# 📥 EXPORT USERS TO CSV
# =========================
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
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def export_pdf(request):
    global latest_data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="AeroCore_Report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    
    # --- 1. FIX THE LOGO ---
    # Change 'logo.png' to the actual name of your logo file in your images folder
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'images', 'logo.png') 
    
    if os.path.exists(logo_path):
        # Positioned in top right corner
        p.drawImage(logo_path, 480, 730, width=60, height=60, mask='auto')

    # --- 2. FIX THE TEXT SPACING ---
    # Title
    p.setFont("Helvetica-Bold", 20)
    p.setStrokeColorRGB(1, 0.72, 0.45) 
    p.drawString(100, 750, "AERO_CORE DIAGNOSTIC REPORT")
    
    # Horizontal Line (Moved down slightly to avoid overlap)
    p.setStrokeColorRGB(0.3, 0.3, 0.3)
    p.line(100, 735, 500, 735)
    
    # Body Content (Starting lower at 700 to create a gap)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 700, "Engine Performance Summary:")
    
    # Data points
    p.setFont("Helvetica", 12)
    y_position = 670 # Starting height for data
    
    data_points = [
        f"• Remaining Useful Life: {latest_data.get('cycles', '--')} CYCLES",
        f"• System Health Status: {latest_data.get('health', 'No Data')}",
        f"• Core Vibration: {latest_data.get('vibration', '--')} ips",
        f"• Oil Pressure: {latest_data.get('pressure', '--')} psi",
        f"• Fuel Flow: {latest_data.get('fuel_flow', '--')} pph"
    ]

    for line in data_points:
        p.drawString(120, y_position, line)
        y_position -= 25 # Moves the next line down by 25 units
    
    p.showPage()
    p.save()
    return response
# =========================
# 🚪 LOGOUT
# =========================
def logout_view(request):
    global latest_data
    latest_data = {}  # This clears the ML results from memory
    logout(request)
    return redirect('login')