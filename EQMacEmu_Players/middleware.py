class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "cdnjs.cloudflare.com "
            "code.jquery.com "
            "cdn.jsdelivr.net "
            "unpkg.com; "
            "style-src 'self' 'unsafe-inline' "
            "fonts.googleapis.com "
            "cdn.jsdelivr.net "
            "use.fontawesome.com; "
            "font-src 'self' fonts.gstatic.com use.fontawesome.com; "
            "img-src 'self' data: *.cloudflare.com; "
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