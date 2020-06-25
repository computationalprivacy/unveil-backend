"""URLs for status."""
from django.urls import path

from . import views

urlpatterns = [
    path('update/', views.update_status, name='status-update'),
    path('list/', views.get_status, name='status-list'),
    path('recent/<int:num_secs>/',
         views.get_status_recent, name='status-recent')
]
