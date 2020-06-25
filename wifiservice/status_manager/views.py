"""Views for the status management."""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from instructions_manager.views import is_instruction_available
from db_manager.models import get_status_collection
import datetime
import json
from instructions_manager.views import add_instruction_helper
from utils.utils import check_session_active


# update access point if last null time is earlier than 60 seconds
UPDATE_AP_TIME = 60
FETCH_AP_INSTR = 3


def ap_change_device(status):
    """Add instruction if AP change is needed.

    Side effects:
        - Update last_useful_time
    """
    status_collection = get_status_collection()
    if (status['state'].find("HostAP") == -1 or
            status['ap_details']['access_point']['sticky_ap'] == 1):
        return status
    last_status = status_collection.find_one({'mac': status['mac']})
    update_last_useful_time = False
    if not last_status or 'last_useful_time' not in last_status:
        update_last_useful_time = True
    else:
        if (last_status['state'] != status['state'] or
            last_status['ap_details']['access_point']['ssid'] !=
            status['ap_details']['access_point']['ssid'] or
                len(status['ap_details']['connected_users']) != 0):
            update_last_useful_time = True
    if update_last_useful_time:
        status['last_useful_time'] = datetime.datetime.now()
    elif ((datetime.datetime.now() -
           last_status['last_useful_time']).total_seconds() > UPDATE_AP_TIME):
        print("Change ap.")
        add_instruction_helper(status['mac'], FETCH_AP_INSTR)
        status['last_useful_time'] = datetime.datetime.now()
    else:
        status['last_useful_time'] = last_status['last_useful_time']
    return status


# Create your views here.
@csrf_exempt
@require_http_methods(['POST'])
def update_status(request):
    """Update status of the pi in mongo."""
    status_collection = get_status_collection()
    status = json.loads(request.body)
    if check_session_active():
        status = ap_change_device(status)
    status['updated_at'] = datetime.datetime.now()
    update_result = status_collection.replace_one(
        {'mac': status['mac']}, status, upsert=True)
    return JsonResponse({
        'ok': update_result.matched_count,
        'is_instruction_available': int(
            is_instruction_available(status['mac']))})


@require_http_methods(['GET'])
def get_status(request):
    """Get all the status."""
    status_collection = get_status_collection()
    status_list = []
    for status in status_collection.find():
        status.pop('_id')
        status['is_instruction_available'] = is_instruction_available(
            status['mac'])
        status_list.append(status)
    return JsonResponse(status_list, safe=False)


def get_status_recent_helper(num_secs):
    """Get recently available status."""
    status_collection = get_status_collection()
    status_list = []
    filter_criteria = {
        'updated_at':
            {'$gt': datetime.datetime.now() - datetime.timedelta(
                seconds=num_secs)}}
    for status in status_collection.find(filter_criteria):
        status.pop('_id')
        status_list.append(status)
    return status_list


@require_http_methods(['GET'])
def get_status_recent(request, num_secs):
    """Get only the recent status from past num_secs here."""
    return JsonResponse(get_status_recent_helper(num_secs), safe=False)
