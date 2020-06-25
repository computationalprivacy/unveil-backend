"""Display manager to manage what is displayed on the screen."""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import datetime
from db_manager.models import get_display_collection
import json


DEFAULT_ZOOM = 9
THRESHOLD = 1800  # display expires after 30 minutes


@require_http_methods(['GET'])
def get_session_to_display(request, screen):
    """Return session to display."""
    display_collection = get_display_collection()
    display = display_collection.find_one({'screen': screen})
    display_id = 0
    response = {'id': display_id}
    if (display and (
        datetime.datetime.now() -
            display['updated_at']).total_seconds() < THRESHOLD):
        display_id = display['session']
        response['id'] = display_id
        if 'zoom' in display:
            response['zoom'] = display['zoom']
    return JsonResponse(response)


@csrf_exempt
@require_http_methods(['POST'])
def post_session_to_display(request):
    """Add session to display."""
    display_collection = get_display_collection()
    data = json.loads(request.body)
    data['updated_at'] = datetime.datetime.now()
    update = display_collection.replace_one(
        {'screen': data['screen']}, data, upsert=True)
    return JsonResponse({'ok': update.modified_count})


@csrf_exempt
@require_http_methods(['POST'])
def post_zoom_level(request):
    """Add zoom level to the probe requests."""
    display_collection = get_display_collection()
    data = json.loads(request.body)
    data['updated_at'] = datetime.datetime.now()
    current_data = display_collection.find_one(
        {'screen': data['screen']})
    current_data['zoom'] = data['zoom']
    update = display_collection.replace_one(
        {'screen': data['screen']}, current_data, upsert=True)
    return JsonResponse({'ok': update.modified_count})
