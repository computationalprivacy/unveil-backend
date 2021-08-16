"""URLs for display data."""
from django.urls import path

from . import views

urlpatterns = [
    path("get/<screen>/", views.get_session_to_display, name="display-get"),
    path("post/", views.post_session_to_display, name="display-post"),
    path("zoom/", views.post_zoom_level, name="display-zoom"),
    path("set-filters/<session_id>", views.set_filter, name="set-filters"),
    path("get-filters/<session_id>", views.get_filter, name="get-filters"),
]
