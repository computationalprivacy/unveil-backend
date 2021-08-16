"""Access api."""
import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from security_manager.models import AccessTokens
from .utils import register_user, verify_login, generate_jwt_token


@csrf_exempt
@require_http_methods(["POST"])
def verify_pin(request):
    """Verify PIN."""
    data = json.loads(request.body)
    pin = data["pin"]
    if (
        pin == settings.DEMO_SECURITY.pin
        or not settings.DEMO_SECURITY.security_check_required
    ):
        obj, _ = AccessTokens.objects.update_or_create(service="controller")
        obj.save()
        return JsonResponse({"token": obj.token}, status=200)
    else:
        return JsonResponse({"error": "Invalid PIN"}, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """Log User In"""
    data = json.loads(request.body)
    user_pin = data.get("user_pin", "")
    userid = verify_login(user_pin=user_pin)

    if userid is not None:
        return JsonResponse({"token": generate_jwt_token(userid=userid)}, status=200)
    return HttpResponse("Unauthorized", status=401)


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    data = json.loads(request.body)
    mac_address = data.get("mac_address", None)
    if mac_address:
        user = register_user(mac_address)
        return HttpResponse(user.user_pin, status=201)
    return HttpResponse("Bad Request", 400)
