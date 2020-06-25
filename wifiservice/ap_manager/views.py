"""Views for managing access points.

- GET access point name
- POST data
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from utils.utils import handle_uploaded_file
from db_manager.models import (
    get_public_ap_collection, get_internet_data_collection)
from .analysis import rate_and_insert, analyze_helper
from .utils import get_sorted_devices
import pymongo
import utils


@require_http_methods(['GET'])
def get_sessions_traffic(request):
    """Return a list of all session probes with ratings."""
    internet_data_collection = get_internet_data_collection()
    analysis_results = internet_data_collection.find(
        {'session_id': {'$exists': True}})
    results_list = {}
    for res in analysis_results:
        sess_id = res['session_id']
        ratings_available = all(['rating' in dev for dev in res['results']])
        # ratings_available = False
        if not ratings_available:
            res = rate_and_insert(
                sess_id, res['results'], res['screenshots'],
                internet_data_collection)
        results_list[sess_id] = {
            'session_id': sess_id,
            'rating': res['rating'],
            'creation_time': res['creation_time'],
            'num_devices': len(res['results'])
        }
    results = [val for key, val in results_list.items() if val['rating'] != 0]
    results.sort(reverse=True, key=lambda x: x['rating'])
    return JsonResponse(
        {'results': results})


@csrf_exempt
@require_http_methods(['POST'])
def analyze(request):
    """Analyze probe requests file."""
    ap_data = request.FILES['data']
    data = request.POST.dict()
    session_id = data['session_id']
    data_path = handle_uploaded_file(ap_data, data['name'])
    analyze_helper.delay(session_id, data_path)
    return JsonResponse({'ok': 1})


@require_http_methods(['GET'])
def get_latest(request):
    """Return latest result from probe request analysis."""
    internet_data_collection = get_internet_data_collection()
    res = internet_data_collection.find().sort(
        [("creation_time", pymongo.DESCENDING)]).limit(1)
    return JsonResponse({'results': res[0]['results']})


@require_http_methods(['GET'])
def get_session(request, session_id):
    """Get session data."""
    internet_data_collection = get_internet_data_collection()
    res_list = internet_data_collection.find(
        {'session_id': session_id})
    collected_data = []
    for res in res_list:
        collected_data.extend(res['results'])
    collected_data = get_sorted_devices(collected_data)
    return JsonResponse({'results': collected_data})


@require_http_methods(['GET'])
def get_session_screenshots(request, session_id):
    """Return HTTP screenshots for the session."""
    internet_data_collection = get_internet_data_collection()
    res_list = internet_data_collection.find(
        {'session_id': session_id})
    collected_data = []
    for res in res_list:
        collected_data.extend(res['screenshots'])
    return JsonResponse({'screenshots': collected_data})


@require_http_methods(['GET'])
def get_opted_out_mac(request):
    """Return opted out mac."""
    return JsonResponse({
        'mac': utils.optout.get_opted_out_mac()})


@csrf_exempt
@require_http_methods(['POST'])
def add_ap(request):
    """Add an access point."""
    public_ap_collection = get_public_ap_collection()
    data = request.POST.dict()
    ssid = data['ssid']
    channel = data['channel']
    ap = {'ssid': ssid, 'channel': channel}
    update = public_ap_collection.replace_one(ap, ap, upsert=True)
    return JsonResponse({'ok': update.modified_count})
