"""Utilities for ap manager."""
from db_manager.models import get_internet_data_collection
import datetime
from utils.scheduling import get_scheduler


def get_sorted_devices(dev_list):
    """Return sorted devices."""
    return sorted(
        dev_list, key=lambda k: k['rating'], reverse=True)


def remove_result(result):
    """Remove result from probe analysis collection."""
    internet_data_collection = get_internet_data_collection()
    print("removing {} with rating of {} for curation".format(
        result['session_id'], result['rating']))
    internet_data_collection.delete_one(
        {'session_id': result['session_id']})


def remove_expired_result(result):
    """Remove the result if expired."""
    if (datetime.datetime.now().date() > result['creation_time'].date()):
        remove_result(result)
        return True
    return False


def clean_internet_data_collection():
    """Curate internet data collection.

    Preserve only last two recent sessions and top 6 captures from previous
    sessions. The data is removed if not in this category. No data is retained
    for more than 6 months. Pseudonymize the MAC address for
    non-active sessions.

    """
    internet_data_collection = get_internet_data_collection()
    analysis_results = list(internet_data_collection.find())
    for index, res in enumerate(analysis_results):
        remove_expired_result(res)


def schedule_data_cleaning():
    """Schedule data cleaning for 00:01:00 everyday."""
    scheduler = get_scheduler()
    date = datetime.date.today() + datetime.timedelta(days=1)
    time = datetime.time(0, 1, 0)
    schedule_time = datetime.datetime.combine(date, time)
    scheduler.schedule(
        scheduled_time=schedule_time,
        func=clean_internet_data_collection,
        interval=86400,
        repeat=None,
    )
