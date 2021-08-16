from django.apps import AppConfig
from .utils import schedule_data_cleaning


class ProbeManagerConfig(AppConfig):
    name = "probe_manager"

    def ready(self):
        """Schedule curation and cleanup functions during start.

        1. Remove data at 12:00:01am everyday.
        """
        schedule_data_cleaning()
