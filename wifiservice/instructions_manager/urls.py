"""URLs for instructions."""
from django.urls import path

from . import views

urlpatterns = [
    path("add/", views.add_instruction, name="instruction-add"),
    path(
        "get_for_execution/",
        views.get_instruction_for_execution,
        name="instruction-get_for_exec",
    ),
    path("executed/", views.executed_instruction, name="instruction-executed"),
]
