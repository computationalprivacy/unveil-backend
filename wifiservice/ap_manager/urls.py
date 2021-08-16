"""URLs for ap manager."""
from django.urls import path

from . import views

urlpatterns = [
    path("analyze/", views.analyze, name="ap-analyze"),
    path("latest/", views.get_latest, name="ap-latest"),
    path("add/", views.add_ap, name="ap-add"),
    path("session/<session_id>/", views.get_orm_session, name="ap-session"),
    path(
        "data/session/<session_id>/screen/<data_screen>/",
        views.get_orm_session_screen_data,
        name="ap-session-screen",
    ),
    path(
        "screenshots/<session_id>/",
        views.get_orm_session_screenshots,
        name="ap-screenshots",
    ),
    path("list/", views.get_orm_sessions_traffic, name="ap-traffic-list"),
    path(
        "session/mobile/<session_id>/",
        views.get_orm_session_filtered,
        name="ap-session",
    ),
]
