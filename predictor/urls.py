from django.urls import path
from .views import upload_predict

urlpatterns = [
    path('predict/', upload_predict, name='predict'),
]