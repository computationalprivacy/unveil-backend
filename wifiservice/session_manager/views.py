"""Session management.

- POST Start a new session and create a session ID
- GET Return the session id for running session else 0 if no session.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from db_manager.models import get_session_collection, get_public_ap_collection
from status_manager.views import get_status_recent_helper
from .utils import (
    stop_session_helper,
    get_or_create_session,
    schedule_manual_mode_instructions,
    schedule_automated_mode_instructions,
    get_or_create_orm_session,
    is_session_active,
    stop_orm_session_helper,
)
from utils.utils import check_session_active
from utils.scheduling import empty_scheduler
from instructions_manager.views import empty_mac_instructions
from django.conf import settings
import random


@csrf_exempt
@require_http_methods(["POST"])
def start_session(request):
    """Create a session id."""
    sess_id, created = get_or_create_session()
    sess_id = get_or_create_orm_session(sess_id)
    return JsonResponse({"id": str(sess_id)})


@csrf_exempt
@require_http_methods(["POST"])
def stop_session(request):
    """Stop existing session."""

    # OLD CODE .
    session = check_session_active()
    if session:
        empty_scheduler()
        stop_session_helper(str(session["_id"]))
    session_id = str(session["_id"])
    session = is_session_active()
    if session:
        session_id = get_or_create_orm_session(session_id)
        empty_scheduler()
        stop_orm_session_helper(session_id)
    return JsonResponse({"ok": 1})


@csrf_exempt
@require_http_methods(["POST"])
def start_automated_session(request, delay=0):
    """Create a session id."""
    sess_id, created = get_or_create_session(automated=True)
    sess_id = get_or_create_orm_session(sess_id)
    available_pi = get_status_recent_helper(settings.DEMO_CONSTANTS.active_pi_threshold)
    if len(available_pi) == 0:
        return JsonResponse({"error": "No active Pi available."})
    for pi in available_pi:
        empty_mac_instructions(pi["mac"])
    if created:
        schedule_automated_mode_instructions(sess_id, available_pi, delay)
        return JsonResponse({"id": str(sess_id)})
    else:
        return JsonResponse(
            {
                "error": "Session in progress. Please stop current "
                "session and start again."
            }
        )


@csrf_exempt
@require_http_methods(["POST"])
def start_manual_session(request, delay=0):
    """Create a session id."""
    sess_id, created = get_or_create_session(automated=True)
    available_pi = get_status_recent_helper(settings.DEMO_CONSTANTS.active_pi_threshold)
    if len(available_pi) == 0:
        return JsonResponse({"error": "No active Pi available."})
    for pi in available_pi:
        empty_mac_instructions(pi["mac"])
    if created:
        schedule_manual_mode_instructions(sess_id, available_pi, delay)
        return JsonResponse({"id": str(sess_id)})
    else:
        return JsonResponse(
            {
                "error": "Session in progress. Please stop current "
                "session and start again."
            }
        )


@require_http_methods(["GET"])
def get_session(request):
    """Get session id for active session."""
    session = check_session_active()
    sess_id = 0
    if session:
        sess_id = str(session["_id"])
    return JsonResponse({"id": sess_id})


@require_http_methods(["GET"])
def get_ap(request):
    """Get access point params for the session."""
    sticky = request.GET.get("sticky", 0)
    session_collection = get_session_collection()
    public_ap_collection = get_public_ap_collection()
    session = check_session_active()
    if session:
        if "ap" not in session:
            session["ap"] = []
        ssid_list = list(public_ap_collection.find())
        ssid_to_send = dict(
            ssid="Experiment-UNVEIL-{}".format(random.randint(1, 100000)), channel=6
        )
        if sticky == 0:
            for ssid in ssid_list:
                if ssid["ssid"] not in session["ap"]:
                    ssid_to_send = ssid
                    break
            if not ssid_to_send:
                session["ap"] = []
                ssid_to_send = ssid_list[0]
            session["ap"].append(ssid_to_send["ssid"])
            session_collection.replace_one({"_id": session["_id"]}, session)
        return JsonResponse(
            {"ssid": ssid_to_send["ssid"], "channel": ssid_to_send["channel"]}
        )
    else:
        return JsonResponse({"error": "No active session."})
