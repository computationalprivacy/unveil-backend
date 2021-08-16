"""All scheduling related functions."""
import django_rq
import datetime
from django.conf import settings


def get_scheduler(queue="instructions"):
    """Return the scheduler for instructions."""
    scheduler = django_rq.get_scheduler(queue)
    return scheduler


def empty_scheduler():
    """Empty the scheduler."""
    scheduler = get_scheduler()
    jobs = scheduler.get_jobs(
        until=datetime.timedelta(seconds=settings.DEMO_CONSTANTS.demo_time)
    )
    for job in jobs:
        scheduler.cancel(job)
