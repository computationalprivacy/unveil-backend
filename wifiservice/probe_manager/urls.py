"""URLs for status."""
from django.urls import path

from . import views

urlpatterns = [
    path("analyze/", views.analyze, name="probes-analyze"),
    path("latest/", views.get_latest, name="probes-latest"),
    path("session/<session_id>/", views.get_session, name="probes-session"),
    path("list/", views.get_session_probes, name="probes-list"),
]
