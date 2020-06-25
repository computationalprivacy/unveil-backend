"""Access api."""
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import AccessTokens


@csrf_exempt
@require_http_methods(['POST'])
def verify_pin(request):
    """Verify PIN."""
    data = json.loads(request.body)
    pin = data['pin']
    if (pin == settings.DEMO_SECURITY.pin or not
            settings.DEMO_SECURITY.security_check_required):
        obj, _ = AccessTokens.objects.update_or_create(service='controller')
        obj.save()
        return JsonResponse({'token': obj.token}, status=200)
    else:
        return JsonResponse({'error': 'Invalid PIN'}, status=401)
