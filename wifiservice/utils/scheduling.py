"""All scheduling related functions."""
import django_rq
import datetime
from django.conf import settings


def get_scheduler():
    """Return the scheduler for instructions."""
    scheduler = django_rq.get_scheduler('instructions')
    return scheduler


def empty_scheduler(exclude_optout=True):
    """Empty the scheduler."""
    scheduler = get_scheduler()
    jobs = scheduler.get_jobs(
        until=datetime.timedelta(seconds=settings.DEMO_CONSTANTS.demo_time))
    for job in jobs:
        if (exclude_optout and
            job.description ==
                'ap_manager.analysis.remove_opt_out_users()'):
            continue
        scheduler.cancel(job)
