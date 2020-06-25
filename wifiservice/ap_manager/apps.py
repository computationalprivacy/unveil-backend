"""App initialization file."""
from django.apps import AppConfig


class ApManagerConfig(AppConfig):
    """ap_manager app config."""

    name = 'ap_manager'

    def ready(self):
        """Run function on initialization."""
        from .analysis import schedule_optout
        schedule_optout()
