from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),   # homepage

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('fleet/', views.fleet, name='fleet'),
    path('maintenance/', views.maintenance, name='maintenance'),
    path('health/', views.health, name='health'),

    # ✅ ADD THIS LINE (IMPORTANT)
    path('request-access/', views.request_access, name='request_access'),
     # 🔥 ADD THESE
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject/<int:user_id>/', views.reject_user, name='reject_user'),
]