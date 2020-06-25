"""Runs analysis."""
import datetime
from django_rq import job
from db_manager.models import (
    get_probe_analysis_collection, get_ssid_collection)
from .analyzer import ProbeAnalyzer
from utils.utils import get_expiry_date
import os


def rate_result(results):
    """Return a rating for the result."""
    rate = len(results['phones'].keys()) * 10
    rate += len(results['markers'])
    return rate


def rate_and_insert(analysis_result, session_id, data_path):
    """Rate the result and insert in db."""
    probe_analysis_collection = get_probe_analysis_collection()
    creation_time = datetime.datetime.now()
    probe_analysis_collection.replace_one(
        {'session_id': session_id}, {
            'creation_time': creation_time,
            'results': analysis_result, 'rating': rate_result(analysis_result),
            'session_id': session_id, 'expire_at': get_expiry_date()},
        upsert=True)


@job('data')
def analyze_helper(session_id, data_path):
    """Analyze helper."""
    ssid_collection = get_ssid_collection()
    probe_analyzer = ProbeAnalyzer(ssid_collection)
    analysis_result = probe_analyzer(data_path)
    rate_and_insert(analysis_result, session_id, data_path)
    os.remove(data_path)
