import os
from db_manager.models import get_internet_data_collection
from ap_manager.analysis import analyze_helper


def test_ap():
    """Test access point data."""
    internet_data_collection = get_internet_data_collection()
    test_dp = [f.path for f in os.scandir('data') if '_ap.' in f.name]
    # test_dp = [
    #     'data/5c0582a3289ca023d5a13421_03122018192837_ap.pcapng',
    #     'data/5bffc11e289ca021ab1642f8_29112018104920_ap.pcapng',
    #     'data/5c0909dd289ca079d6f07c96_06122018114349_ap.pcapng'
    # ]
    # data_points = internet_data_collection.find()
    # test_dp = [res['path'] for res in data_points]
    internet_data_collection.drop()
    for data_path in test_dp:
        session_id = os.path.basename(data_path).split('_')[0]
        analyze_helper(session_id, data_path)


def remove_invalid_res():
    internet_data_collection = get_internet_data_collection()
    analysis_results = internet_data_collection.find(
        {'session_id': {'$exists': True}})
    results_list = {}
    for res in analysis_results:
        sess_id = res['session_id']
        results_list[sess_id] = {
            'session_id': sess_id,
            'rating': res['rating'],
            'creation_time': res['creation_time'],
            'num_devices': len(res['results'])
        }
    results = [val for key, val in results_list.items() if val['rating'] != 0]
    results.sort(reverse=True, key=lambda x: x['rating'])
    test_dp = [f.path for f in os.scandir('data') if '_ap.' in f.name]
    deletable_session_id = [res['session_id'] for res in results[4:]]
    for data_path in test_dp:
        session_id = os.path.basename(data_path).split('_')[0]
        if session_id in deletable_session_id:
            os.remove(data_path)


def run():
    # remove_invalid_res()
    test_ap()
