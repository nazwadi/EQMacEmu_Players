import django_otp
import logging

from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

from django_otp_webauthn import exceptions as webauthn_exceptions
from django_otp_webauthn.views import (
    BeginCredentialAuthenticationView,
    CompleteCredentialAuthenticationView,
)

from .utils import get_client_ip

logger = logging.getLogger('eqmacemu.security')
User = get_user_model()


def _get_pending_mfa_user(request):
    """Return the user stored during the password step of login, or None."""
    user_id = request.session.get('mfa_user_id')
    if user_id:
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            pass
    return None


class MfaWebAuthnBeginView(BeginCredentialAuthenticationView):
    """
    Supplies the pending (pre-MFA) user to the WebAuthn begin ceremony so the
    browser receives credential hints before the session is fully authenticated.
    When no pending user exists (passwordless path), get_user() returns None and
    the parent starts a discoverable-credentials ceremony instead.
    """

    def get_user(self):
        return super().get_user() or _get_pending_mfa_user(self.request)


class MfaWebAuthnCompleteView(CompleteCredentialAuthenticationView):
    """
    Completes the pending MFA session after successful WebAuthn verification,
    mirroring the log-in behaviour of the TOTP mfa_verify view.
    """

    def get_user(self):
        return super().get_user() or _get_pending_mfa_user(self.request)

    def complete_auth(self, device):
        if self.request.user.is_authenticated:
            # User is already logged in — just mark the session as OTP-verified.
            django_otp.login(self.request, device)
            return

        pending_id = self.request.session.pop('mfa_user_id', None)
        self.request.session.pop('mfa_timestamp', None)

        user = device.user
        if pending_id and user.pk != pending_id:
            # A second-factor passkey was used for the wrong pending user.
            raise webauthn_exceptions.CredentialDisabled()

        auth_login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        self.request.session['login_ip'] = get_client_ip(self.request)

        from .models import WebLoginHistory
        WebLoginHistory.objects.create(user=user, ip_address=get_client_ip(self.request))
        oldest_ids = WebLoginHistory.objects.filter(user=user).values_list('id', flat=True)[20:]
        if oldest_ids:
            WebLoginHistory.objects.filter(id__in=list(oldest_ids)).delete()

        logger.info('LOGIN_SUCCESS user=%s ip=%s method=webauthn', user.username, get_client_ip(self.request))
        django_otp.login(self.request, device)

    def get_success_url(self):
        return resolve_url('accounts:list_accounts')
