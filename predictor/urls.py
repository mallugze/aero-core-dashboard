from django.urls import path
from .views import upload_predict
from . import views

urlpatterns = [
    path('predict/', upload_predict, name='predict'),
    
]