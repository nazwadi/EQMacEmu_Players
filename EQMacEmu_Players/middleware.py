from django.conf import settings

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Use CSP from settings instead of hardcoding
        if hasattr(settings, 'SECURE_CONTENT_SECURITY_POLICY'):
            response['Content-Security-Policy'] = settings.SECURE_CONTENT_SECURITY_POLICY

        # Permissions Policy
        response['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), payment=(), "
            "usb=(), magnetometer=(), accelerometer=(), gyroscope=()"
        )

        return response