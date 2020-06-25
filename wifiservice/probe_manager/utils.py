"""Utilities being used."""
import datetime
from db_manager.models import get_probe_analysis_collection
from utils.scheduling import get_scheduler


def remove_result(result, probe_analysis_collection):
    """Remove result from probe analysis collection."""
    print("removing {} with rating of {} for curation".format(
        result['session_id'], result['rating']))
    probe_analysis_collection.delete_one(
        {'session_id': result['session_id']})


def remove_expired_result(result, probe_analysis_collection):
    """Removes the result if expired."""
    if (datetime.datetime.now().date() > result['creation_time'].date()):
        remove_result(result, probe_analysis_collection)
        return True
    return False


def clean_probe_analysis_collection():
    """Curate probe analysis collection."""
    probe_analysis_collection = get_probe_analysis_collection()
    analysis_results = list(probe_analysis_collection.find())
    for index, res in enumerate(analysis_results):
        remove_expired_result(res, probe_analysis_collection)


def schedule_data_cleaning():
    """Schedule data cleaning for 00:01:00 everyday."""
    scheduler = get_scheduler()
    date = datetime.date.today() + datetime.timedelta(days=1)
    time = datetime.time(0, 1, 0)
    schedule_time = datetime.datetim.combine(date, time)
    scheduler.schedule(
        scheduled_time=schedule_time,
        func=clean_probe_analysis_collection,
        interval=86400,
        repeat=None,
    )
