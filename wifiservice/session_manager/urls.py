"""URLs for session."""
from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.start_session, name='session-create'),
    path('automate/<int:delay>/', views.start_automated_session,
         name='session-automated'),
    path('manual/<int:delay>/', views.start_manual_session,
         name='session-cpg'),
    path('latest/', views.get_session, name='session-latest'),
    path('ap/', views.get_ap, name='session-ap'),
    path('stop/', views.stop_session, name='session-stop')
]
