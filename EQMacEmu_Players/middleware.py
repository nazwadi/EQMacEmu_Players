from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

# URL prefixes that staff are allowed to visit without MFA set up.
# Everything else is blocked until they configure TOTP or a passkey.
_MFA_EXEMPT_PREFIXES = (
    '/accounts/mfa/',       # setup, verify, backup codes, passkeys management
    '/accounts/webauthn/',  # WebAuthn API endpoints (registration & authentication)
    '/accounts/login',
    '/accounts/logout',
    '/accounts/register',
    '/accounts/password_reset',
    '/accounts/reset/',
)


class StaffMFARequiredMiddleware:
    """
    Redirect staff/superusers to MFA setup if they have no confirmed OTP
    device. Regular users are unaffected — MFA remains optional for them.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.user.is_staff
            and not any(request.path.startswith(p) for p in _MFA_EXEMPT_PREFIXES)
        ):
            from django_otp.plugins.otp_totp.models import TOTPDevice
            has_totp = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
            has_webauthn = False
            try:
                from django_otp_webauthn.models import WebAuthnCredential
                has_webauthn = WebAuthnCredential.objects.filter(user=request.user, confirmed=True).exists()
            except ImportError:
                pass
            if not has_totp and not has_webauthn:
                messages.warning(
                    request,
                    "Staff accounts must have two-factor authentication enabled. "
                    "Please set up 2FA to continue."
                )
                return redirect('accounts:mfa_setup')

        return self.get_response(request)


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