from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)