"""URLs for ap manager."""
from django.urls import path

from . import views

urlpatterns = [
    path('analyze/', views.analyze, name='ap-analyze'),
    path('latest/', views.get_latest, name='ap-latest'),
    path('add/', views.add_ap, name='ap-add'),
    path('session/<session_id>/', views.get_session, name='ap-session'),
    path('screenshots/<session_id>/', views.get_session_screenshots,
         name='ap-screenshots'),
    path('list/', views.get_sessions_traffic, name='ap-traffic-list'),
    path('optout/', views.get_opted_out_mac, name='ap-optout')
]
