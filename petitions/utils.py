import json
import urllib.request

from accounts.models import Account, LoginServerAccounts


def get_staff_status(user):
    """Returns the highest game account status for this user, or 0 if not staff."""
    ls_ids = LoginServerAccounts.objects.filter(
        ForumName=user.username
    ).values_list('LoginServerID', flat=True)

    account = Account.objects.using('game_database').filter(
        lsaccount_id__in=list(ls_ids),
        status__gte=50
    ).order_by('-status').first()

    return account.status if account else 0


def is_staff_member(user):
    if not user.is_authenticated:
        return False
    # Cache on the user object for the lifetime of the request (Django recreates the
    # user object per request, so this never leaks across requests).
    if not hasattr(user, '_is_staff_member_cache'):
        user._is_staff_member_cache = user.is_superuser or get_staff_status(user) >= 50
    return user._is_staff_member_cache


def get_user_characters(user):
    """Returns character names for a user's game accounts, for the petition form dropdown."""
    from common.models.characters import Characters

    ls_ids = LoginServerAccounts.objects.filter(
        ForumName=user.username
    ).values_list('LoginServerID', flat=True)

    account_ids = Account.objects.using('game_database').filter(
        lsaccount_id__in=list(ls_ids)
    ).values_list('id', flat=True)

    return Characters.objects.filter(
        account_id__in=list(account_ids),
        is_deleted=0
    ).values_list('name', flat=True).order_by('name')


def notify_staff(petition, message, exclude_user=None):
    """Notify all staff of a new petition or player reply, on-site, by email, and Discord."""
    from django.conf import settings
    from django.contrib.auth.models import User
    from django.db.models import Q
    from django.core.mail import send_mail
    from .models import Notification, StaffEmailPreference
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    # All active staff: superusers + anyone who has ever claimed a petition
    staff_users = (
        User.objects
        .filter(is_active=True)
        .filter(Q(is_superuser=True) | Q(claimed_petitions__isnull=False))
        .distinct()
    )

    for user in staff_users:
        if exclude_user and user == exclude_user:
            continue
        Notification.objects.create(user=user, petition=petition, message=message)
        try:
            pref = user.staff_email_pref
            if pref.email_notifications and user.email:
                send_mail(
                    subject=f'[EQ Archives] Petition #{petition.pk}: {petition.subject}',
                    message=f'{message}\n\n{site_url}/petitions/{petition.pk}/',
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
        except StaffEmailPreference.DoesNotExist:
            pass

    _post_to_discord(petition, message)


def notify_petitioner(petition, message):
    """Notify the petition owner of a staff action, on-site and by email (if not opted out)."""
    from django.conf import settings
    from django.core.mail import send_mail
    from .models import Notification, PlayerEmailPreference
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    Notification.objects.create(user=petition.user, petition=petition, message=message)

    # Respect player email opt-out (default is opted in)
    try:
        if not petition.user.player_email_pref.email_notifications:
            return
    except PlayerEmailPreference.DoesNotExist:
        pass  # no preference saved → send by default

    if petition.user.email:
        send_mail(
            subject=f'[EQ Archives] Your petition has been updated: {petition.subject}',
            message=(
                f'{message}\n\n'
                f'View your petition: {site_url}/petitions/{petition.pk}/'
            ),
            from_email=None,
            recipient_list=[petition.user.email],
            fail_silently=True,
        )


def _post_to_discord(petition, message):
    """Post a petition event to the configured Discord webhook, if set."""
    from django.conf import settings

    webhook_url = getattr(settings, 'PETITION_DISCORD_WEBHOOK_URL', '')
    if not webhook_url:
        return
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    color_map = {
        'critical': 0xED4245,
        'high':     0xFEE75C,
        'normal':   0x5865F2,
        'low':      0x95A5A6,
    }

    fields = [
        {'name': 'Player',   'value': petition.user.username,    'inline': True},
        {'name': 'Category', 'value': petition.category.name,    'inline': True},
    ]
    if petition.character_name:
        fields.append({'name': 'Character', 'value': petition.character_name, 'inline': True})
    if petition.priority != 'normal':
        fields.append({'name': 'Priority', 'value': petition.get_priority_display(), 'inline': True})

    payload = {
        'embeds': [{
            'title': f'Petition #{petition.pk}: {petition.subject}',
            'description': message,
            'color': color_map.get(petition.priority, 0x5865F2),
            'fields': fields,
            'url': f'{site_url}/petitions/{petition.pk}/',
        }]
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # never crash the request over a notification failure
