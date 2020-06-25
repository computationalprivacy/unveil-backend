import os
from ap_manager.analysis import analyze_helper
from db_manager.models import get_ssid_collection
from probe_manager.analyzer import ProbeAnalyzer


def test_ap():
    """Test access point data."""
    test_dp = [f.path for f in os.scandir('data') if '_ap.' in f.name]
    for data_path in test_dp:
        session_id = os.path.basename(data_path).split('_')[0]
        analyze_helper(session_id, data_path)


def test_probe():
    """Test probe analyzer."""
    ssid_collection = get_ssid_collection()
    probe_analyzer = ProbeAnalyzer(ssid_collection)
    test_dp = [f.path for f in os.scandir('data') if '_probe.' in f.name]
    for data_path in test_dp:
        analysis_result = probe_analyzer(data_path)
        print(analysis_result)


def run():
    test_ap()
    test_probe()
