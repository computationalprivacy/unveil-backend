"""Security middleware."""
from ipware import get_client_ip
from django.conf import settings
import ipaddress
from .models import AccessTokens
from django.http import JsonResponse
from django.urls import reverse


class AccessVerificationMiddleware:
    """Access verification middleware."""

    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response
        self.permissible_ips = ipaddress.ip_network(
            settings.DEMO_SECURITY.allowed_ips)

    def __call__(self, request):
        """Verify if the request has access to the APIs."""
        is_request_valid = not settings.DEMO_SECURITY.security_check_required \
            or request.path == reverse('pin-verify')
        if not is_request_valid:
            client_ip, is_routable = get_client_ip(request)
            is_ip_safe = ipaddress.ip_address(
                client_ip) in self.permissible_ips
            if not is_ip_safe and 'HTTP_TOKEN' in request.META:
                token = request.META['HTTP_TOKEN']
                obj = AccessTokens.objects.filter(token__exact=token).first()
                if obj:
                    is_request_valid = True
            is_request_valid = is_request_valid or is_ip_safe

        if is_request_valid:
            return self.get_response(request)
        else:
            return JsonResponse(
                {'message': 'Invalid request.'}, status=401)
