"""URLs for access checks."""
from django.urls import path

from . import views

urlpatterns = [
    path('verify/', views.verify_pin, name='pin-verify')
]
