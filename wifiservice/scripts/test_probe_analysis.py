import os
from probe_manager.analyzer import ProbeAnalyzer
from db_manager.models import (
    get_ssid_collection, get_probe_analysis_collection)
from probe_manager.analysis import rate_and_insert


def test_probe():
    """Test probe analyzer."""
    ssid_collection = get_ssid_collection()
    p = ProbeAnalyzer(ssid_collection)
    test_dp = [f.path for f in os.scandir('data') if '_probe.' in f.name]
    for data_path in test_dp:
        analysis_result = p(data_path)
        session_id = os.path.basename(data_path).split('_')[0]
        rate_and_insert(analysis_result, session_id, data_path)


def remove_invalid_res():
    probe_analysis_collection = get_probe_analysis_collection()
    analysis_results = probe_analysis_collection.find(
        {'session_id': {'$exists': True}})
    results_list = {}
    for res in analysis_results:
        sess_id = res['session_id']
        results_list[sess_id] = {
            'session_id': sess_id,
            'rating': res['rating']
        }
    results = [val for key, val in results_list.items() if val['rating'] != 0]
    results.sort(reverse=True, key=lambda x: x['rating'])
    test_dp = [f.path for f in os.scandir('data') if '_probe.' in f.name]
    nondeletable_session_id = [res['session_id'] for res in results]
    for data_path in test_dp:
        session_id = os.path.basename(data_path).split('_')[0]
        if session_id not in nondeletable_session_id:
            print(data_path)
            os.remove(data_path)


def run():
    remove_invalid_res()
    # test_probe()
