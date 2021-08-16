"""Display manager to manage what is displayed on the screen."""
import json
import datetime
import ap_manager.models as models

from db_manager.models import get_display_collection
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from security_manager.models import User


DEFAULT_ZOOM = 9
THRESHOLD = 18000  # display expires after 30 minutes


@require_http_methods(["GET"])
def get_session_to_display(request, screen):
    """Return session to display."""
    display_collection = get_display_collection()
    display = display_collection.find_one({"screen": screen})
    display_id = 0
    response = {"id": display_id}
    if (
        display
        and (datetime.datetime.now() - display["updated_at"]).total_seconds()
        < THRESHOLD
    ):
        display_id = display["session"]
        response["id"] = display_id
        if "zoom" in display:
            response["zoom"] = display["zoom"]
    return JsonResponse(response)


@csrf_exempt
@require_http_methods(["POST"])
def post_session_to_display(request):
    """Add session to display."""
    display_collection = get_display_collection()
    data = json.loads(request.body)
    data["updated_at"] = datetime.datetime.now()
    update = display_collection.replace_one(
        {"screen": data["screen"]}, data, upsert=True
    )
    return JsonResponse({"ok": update.modified_count})


@csrf_exempt
@require_http_methods(["POST"])
def post_zoom_level(request):
    """Add zoom level to the probe requests."""
    display_collection = get_display_collection()
    data = json.loads(request.body)
    data["updated_at"] = datetime.datetime.now()
    current_data = display_collection.find_one({"screen": data["screen"]})
    current_data["zoom"] = data["zoom"]
    update = display_collection.replace_one(
        {"screen": data["screen"]}, current_data, upsert=True
    )
    return JsonResponse({"ok": update.modified_count})


def get_pin_from_mac(mac_address):
    user = User.objects.filter(mac_address=mac_address)
    if user.exists():
        return user.user_pin
    else:
        return "ERROR: USER NOT FOUND"


@require_http_methods(["GET"])
def get_filter(request, session_id):
    filters = models.Filters.objects.filter(device__session_id__session_id=session_id)
    results = [filter.to_json_with_rating() for filter in filters]
    return JsonResponse({"filters": results})


def update_orm_filter(updated_filter, session_id):
    filters = models.Filters.objects.get(
        device_id=updated_filter.get("device_id", ""),
        device__session_id__session_id=session_id,
    )
    filters.update_filters(updated_filter)


@csrf_exempt
@require_http_methods(["POST"])
def set_filter(request, session_id):
    data = json.loads(request.body)
    [update_orm_filter(new_filter, session_id) for new_filter in data]
    return HttpResponse("SUCCESS", 201)
