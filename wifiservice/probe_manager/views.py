"""Views for managing probe requests.

The views supported
- POST probe request file and analyze it.
"""
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from db_manager.models import get_probe_analysis_collection
from .analysis import rate_result, analyze_helper
from utils.utils import handle_uploaded_file
import pymongo


@require_http_methods(["GET"])
def get_session_probes(request):
    """Return a list of all session probes with ratings."""
    probe_analysis_collection = get_probe_analysis_collection()
    analysis_results = probe_analysis_collection.find({"session_id": {"$exists": True}})
    results_list = []
    for res in analysis_results:
        if "rating" not in res:
            res["rating"] = rate_result(res["results"])
            probe_analysis_collection.replace_one(
                {"session_id": res["session_id"]}, res
            )
        results_list.append(
            {
                "session_id": res["session_id"],
                "rating": res["rating"],
                "creation_time": res["creation_time"],
            }
        )
    return JsonResponse({"results": results_list})


# Create your views here.
@csrf_exempt
@require_http_methods(["POST"])
def analyze(request):
    """Analyze probe requests file."""
    probe_data = request.FILES["data"]
    data = request.POST.dict()
    session_id = data["session_id"]
    data_path = handle_uploaded_file(probe_data, data["name"])
    analyze_helper.delay(session_id, data_path)
    return JsonResponse({"ok": 1})


@require_http_methods(["GET"])
def get_session(request, session_id):
    """Get session data."""
    probe_analysis_collection = get_probe_analysis_collection()
    res_list = probe_analysis_collection.find({"session_id": session_id})
    collected_data = {"phones": {}, "markers": []}
    for res in res_list:
        collected_data["phones"].update(res["results"]["phones"])
        collected_data["markers"].extend(res["results"]["markers"])
    return JsonResponse({"results": collected_data})


@require_http_methods(["GET"])
def get_latest(request):
    """Return latest result from probe request analysis."""
    probe_analysis_collection = get_probe_analysis_collection()
    res = (
        probe_analysis_collection.find()
        .sort([("creation_time", pymongo.DESCENDING)])
        .limit(1)
    )
    return JsonResponse({"results": res[0]["results"]})
