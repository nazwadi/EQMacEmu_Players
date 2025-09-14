class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy - fixed syntax
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "https://cdnjs.cloudflare.com "
            "https://code.jquery.com "
            "https://cdn.jsdelivr.net "
            "https://unpkg.com "
            "https://cdn.datatables.net; "
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com "
            "https://cdn.jsdelivr.net "
            "https://use.fontawesome.com "
            "https://cdn.datatables.net; "
            "font-src 'self' https://fonts.gstatic.com https://use.fontawesome.com; "
            "img-src 'self' data: https://*.cloudflare.com https://secure.gravatar.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # Permissions Policy
        response['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), payment=(), "
            "usb=(), magnetometer=(), accelerometer=(), gyroscope=()"
        )

        return response