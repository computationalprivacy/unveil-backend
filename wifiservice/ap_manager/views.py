"""Views for managing access points.

- GET access point name
- POST data
"""
import pymongo
import utils
import ap_manager.models as models

from .analysis import analyze_helper
from db_manager.models import get_public_ap_collection, get_internet_data_collection
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from security_manager.utils import (
    generate_orm_session_results,
    generate_orm_session_results_screen,
)
from utils.utils import handle_uploaded_file


@require_http_methods(["GET"])
def get_orm_sessions_traffic(request):
    """Return a list of session probes with ratings."""
    sessions = models.Session.objects.all()
    results = []
    for session in sessions:
        sess_id = session.session_id
        sess_rating = sum(
            list(
                models.Device.objects.filter(
                    session_id__session_id=sess_id
                ).values_list("rating", flat=True)
            )
        )
        results.append(
            {
                "session_id": sess_id,
                "rating": sess_rating,
                "creation_time": session.creation_time,
                "num_devices": models.Device.objects.filter(
                    session_id__session_id=sess_id
                ).count(),
            }
        )
    results.sort(reverse=True, key=lambda x: x["rating"])
    return JsonResponse({"results": results})


@csrf_exempt
@require_http_methods(["POST"])
def analyze(request):
    """Analyze probe requests file."""
    ap_data = request.FILES["data"]
    data = request.POST.dict()
    session_id = data["session_id"]
    data["name"] = data["name"].split("/")[-1]
    data_path = handle_uploaded_file(ap_data, data["name"])
    analyze_helper.delay(session_id, data_path)
    return JsonResponse({"ok": 1})


@require_http_methods(["GET"])
def get_latest(request):
    """Return latest result from probe request analysis."""
    internet_data_collection = get_internet_data_collection()
    res = (
        internet_data_collection.find()
        .sort([("creation_time", pymongo.DESCENDING)])
        .limit(1)
    )
    return JsonResponse({"results": res[0]["results"]})


@require_http_methods(["GET"])
def get_orm_session(request, session_id):
    """Get session data."""
    return generate_orm_session_results(
        request=request, session_id=session_id, filtered=False
    )


@require_http_methods(["GET"])
def get_orm_session_filtered(request, session_id):
    """Get session data filtered for user."""
    if request.mac_address is None:
        return HttpResponse(status=401)
    return generate_orm_session_results(
        request=request, session_id=session_id, filtered=True
    )


@require_http_methods(["GET"])
def get_orm_session_screen_data(request, session_id, data_screen):
    """Get session data filtered for a screen."""
    return generate_orm_session_results_screen(
        session_id=session_id, data_screen=data_screen
    )


@require_http_methods(["GET"])
def get_orm_session_screenshots(request, session_id):
    """Return HTTP screenshots for the session."""
    results = [
        screenshot.to_json()
        for screenshot in models.Screenshot.objects.filter(
            session_id__session_id=session_id
        ).all()
    ]

    results = list(filter(lambda a: a is not None, results))
    return JsonResponse({"screenshots": results})


@csrf_exempt
@require_http_methods(["POST"])
def add_ap(request):
    """Add an access point."""
    public_ap_collection = get_public_ap_collection()
    data = request.POST.dict()
    ssid = data["ssid"]
    channel = data["channel"]
    ap = {"ssid": ssid, "channel": channel}
    update = public_ap_collection.replace_one(ap, ap, upsert=True)
    return JsonResponse({"ok": update.modified_count})
