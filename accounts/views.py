import base64
import csv
import io
import logging
import qrcode
from datetime import datetime

logger = logging.getLogger('eqmacemu.security')


def _rate_limit_key(group, request):
    return get_client_ip(request)


def _log_web_login(user, ip_address, keep=20):
    WebLoginHistory.objects.create(user=user, ip_address=ip_address)
    oldest_ids = WebLoginHistory.objects.filter(user=user).values_list('id', flat=True)[keep:]
    if oldest_ids:
        WebLoginHistory.objects.filter(id__in=list(oldest_ids)).delete()
from django.utils import timezone
from collections import namedtuple

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import connections
from django.shortcuts import redirect, render

import secrets
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django.contrib.auth.models import User
from django.http import HttpResponse

from common.constants import (
    CONTAINER_TYPES,
    EQUIPMENT_SLOTS,
    ITEM_STATS,
    ITEM_TYPES,
    PLAYER_CLASSES,
    PLAYER_RACES,
)
from items.utils import build_stat_query, get_class_bitmask, get_item_effect, get_race_bitmask

from django_ratelimit.decorators import ratelimit

from .forms import NewLSAccountForm, NewUserForm, UpdateLSAccountForm
from .models import Account, LoginServerAccounts, WebLoginHistory, WorldServerRegistration
from common.models.characters import Characters
from .utils import get_client_ip, sha1_password


def index_request(request):
    if request.method == "GET" or request.method == "POST":
        if request.user.is_authenticated:
            return render(request=request, template_name="accounts/index.html")
    return render(request=request, template_name="accounts/index.html")


def server_list(request):
    if request.method == "GET":
        servers = WorldServerRegistration.objects.all()
        cursor = connections['game_database'].cursor()
        cursor.execute("SELECT count(*) FROM account WHERE `active` = '1' AND `mule` = '0';")
        population = cursor.fetchone()[0]
        return render(request=request,
                      template_name="accounts/server_list.html",
                      context={"servers": servers,
                               "population": population})


@ratelimit(key=_rate_limit_key, rate='10/m', method='POST', block=False)
def login_request(request):
    if getattr(request, 'limited', False):
        logger.warning('RATE_LIMITED_LOGIN ip=%s', get_client_ip(request))
        messages.error(request, "Too many login attempts. Please try again later.")
        return render(request=request, template_name="accounts/login.html", context={"login_form": AuthenticationForm()})
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
                if device:
                    # Don't log in yet — store user ID and redirect to MFA verify
                    request.session['mfa_user_id'] = user.id
                    request.session['mfa_timestamp'] = timezone.now().timestamp()
                    return redirect('accounts:mfa_verify')
                else:
                    # No MFA set up — log in normally
                    login(request, user)
                    request.session['login_ip'] = get_client_ip(request)
                    _log_web_login(user, get_client_ip(request))
                    logger.info('LOGIN_SUCCESS user=%s ip=%s', username, get_client_ip(request))
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect("accounts:list_accounts")
            else:
                logger.warning('LOGIN_FAILED user=%s ip=%s', username, get_client_ip(request))
                messages.error(request, "Invalid username or password.")
        else:
            logger.warning('LOGIN_FAILED user=%s ip=%s', form.data.get('username', ''), get_client_ip(request))
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="accounts/login.html", context={"login_form": form})


def mfa_verify(request):
    user_id = request.session.get('mfa_user_id')
    if not user_id:
        return redirect('accounts:login')

    import time
    timestamp = request.session.get('mfa_timestamp', 0)
    if time.time() - timestamp > 300:
        request.session.pop('mfa_user_id', None)
        request.session.pop('mfa_timestamp', None)
        messages.error(request, "Session expired. Please log in again.")
        return redirect('accounts:login')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if device and device.verify_token(token):
            del request.session['mfa_user_id']
            login(request, user)
            request.session['login_ip'] = get_client_ip(request)
            _log_web_login(user, get_client_ip(request))
            logger.info('LOGIN_SUCCESS user=%s ip=%s', user.username, get_client_ip(request))
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("accounts:list_accounts")
        else:
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'accounts/mfa_verify.html')


@login_required
def mfa_setup(request):
    if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
        messages.info(request, "Two-factor authentication is already enabled.")
        return redirect("accounts:list_accounts")

    device, _ = TOTPDevice.objects.get_or_create(
        user=request.user,
        confirmed=False,
        defaults={"name": "default"}
    )

    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            logger.info('MFA_SETUP user=%s ip=%s', request.user.username, get_client_ip(request))
            messages.success(request, "Two-factor authentication has been enabled.")
            return redirect("accounts:mfa_backup_codes")
        else:
            messages.error(request, "Invalid code. Please try again.")

    img = qrcode.make(device.config_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    return render(request, "accounts/mfa_setup.html", {
        "qr_code": qr_code,
        "secret": device.key,
    })


def _generate_backup_codes(device, count=10):
    StaticToken.objects.filter(device=device).delete()
    for _ in range(count):
        StaticToken.objects.create(device=device, token=secrets.token_hex(4))


@login_required
def mfa_backup_codes(request):
    if not TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
        messages.info(request, "You need to enable two-factor authentication first.")
        return redirect("accounts:mfa_setup")

    device, created = StaticDevice.objects.get_or_create(
        user=request.user,
        defaults={"name": "backup"}
    )

    freshly_generated = False

    if created or not StaticToken.objects.filter(device=device).exists():
        _generate_backup_codes(device)
        freshly_generated = True
    elif request.method == "POST" and request.POST.get("action") == "regenerate":
        _generate_backup_codes(device)
        logger.info('MFA_BACKUP_REGENERATE user=%s ip=%s', request.user.username, get_client_ip(request))
        freshly_generated = True

    backup_codes = StaticToken.objects.filter(device=device)

    return render(request, "accounts/mfa_backup_codes.html", {
        "backup_codes": backup_codes,
        "freshly_generated": freshly_generated,
    })


@login_required
def mfa_disable(request):
    totp_device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()

    if not totp_device:
        messages.info(request, "Two-factor authentication is not enabled on your account.")
        return redirect("accounts:list_accounts")

    if request.method == "POST":
        token = request.POST.get("token", "").strip()

        # Check TOTP device first, then fall back to backup codes
        verified = totp_device.verify_token(token)
        if not verified:
            static_device = StaticDevice.objects.filter(user=request.user).first()
            if static_device:
                verified = static_device.verify_token(token)

        if verified:
            TOTPDevice.objects.filter(user=request.user).delete()
            StaticDevice.objects.filter(user=request.user).delete()
            logger.info('MFA_DISABLE user=%s ip=%s', request.user.username, get_client_ip(request))
            messages.success(request, "Two-factor authentication has been disabled.")
            return redirect("accounts:list_accounts")
        else:
            messages.error(request, "Invalid code. Please try again.")

    return render(request, "accounts/mfa_disable.html")


@login_required
def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("accounts:index")


@ratelimit(key=_rate_limit_key, rate='5/h', method='POST', block=False)
def register_request(request):
    if getattr(request, 'limited', False):
        logger.warning('RATE_LIMITED_REGISTER ip=%s', get_client_ip(request))
        messages.error(request, "Too many registration attempts. Please try again later.")
        return render(request, "accounts/register.html", {'form': NewUserForm})
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info('REGISTER user=%s ip=%s', user.username, get_client_ip(request))
            messages.success(request, "Registration successful! Welcome to EQArchives.")
            return redirect("accounts:index")
        messages.error(request, "Registration unsuccessful. Please check the information and try again.")
    form = NewUserForm
    return render(request, "accounts/register.html", {'form': form})

@login_required
def accounts(request):
    from django.db.models import Case, When, IntegerField

    # Get mule account IDs from the world server
    mule_lsaccount_ids = Account.objects.filter(mule=1).values_list('lsaccount_id', flat=True)

    # Create annotated queryset with mule status
    queryset = LoginServerAccounts.objects.filter(
        ForumName=request.user.username
    ).annotate(
        is_mule=Case(
            When(LoginServerID__in=list(mule_lsaccount_ids), then=1),
            default=0,
            output_field=IntegerField()
        )
    )

    if request.GET.get("_export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="accounts.csv"'
        writer = csv.writer(response)
        writer.writerow(["Account Name", "Email", "Created", "Last Login"])
        for acct in queryset.order_by('AccountName'):
            writer.writerow([acct.AccountName, acct.AccountEmail, acct.AccountCreateDate, acct.LastLoginDate])
        return response

    mfa_enabled = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
    account_count = queryset.count()

    return render(request,
                  "accounts/list_accounts.html",
                  {
                      "accounts_list": queryset.order_by('AccountName'),
                      "mfa_enabled": mfa_enabled,
                      "account_count": account_count,
                  })


@login_required
def create_account(request):
    if request.method == 'POST':
        form = NewLSAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)

            account.AccountPassword = sha1_password(form.cleaned_data['AccountPassword'])

            account.LastIPAddress = get_client_ip(request)
            account.client_unlock = 1
            account.creationIP = get_client_ip(request)
            account.max_accts = 10
            account.Num_IP_Bypass = 1
            account.ForumName = request.user.username
            account.save()
            logger.info('ACCOUNT_CREATE user=%s ip=%s account=%s', request.user.username, get_client_ip(request), account.AccountName)
            messages.success(request, "Login Account Registration successful.")
            return redirect("accounts:list_accounts")
        messages.error(request, "Unsuccessful registration. Invalid information.")

    form = NewLSAccountForm
    return render(request,
                  "accounts/create_account.html",
                  {'form': form}
                  )


@login_required
def update_account(request, pk):
    """Defines view for https://url.tld/accounts/update/<int:pk>"""
    queryset = LoginServerAccounts.objects.filter(LoginServerID=pk, ForumName=request.user.username)
    if queryset.exists():
        data = queryset.values()[0]
        if request.method == 'POST':
            form = UpdateLSAccountForm(request.POST)
            if form.is_valid():
                queryset.update(AccountPassword=sha1_password(form.cleaned_data['AccountPassword']),
                                AccountEmail=form.cleaned_data['AccountEmail'],
                                LastIPAddress=get_client_ip(request))
                logger.info('ACCOUNT_UPDATE user=%s ip=%s pk=%s', request.user.username, get_client_ip(request), pk)
                messages.success(request, "Update successful for " + data['AccountName'] + ".")
                return redirect("accounts:list_accounts")
            for key, value in form.errors.items():
                messages.error(request, "Update unsuccessful. " + key + ", " + ''.join(value))

        # For all other request methods that are not POST - including GET requests
        form = UpdateLSAccountForm(initial={'AccountEmail': data['AccountEmail']})
        return render(request,
                      "accounts/update_account.html",
                      {'form': form, 'AccountName': queryset.values()[0]["AccountName"]}
                      )

    logger.warning('ACCOUNT_UPDATE_DENIED user=%s ip=%s pk=%s', request.user.username, get_client_ip(request), pk)
    return redirect("accounts:list_accounts")


@login_required
def delete_account(request, pk):
    account = LoginServerAccounts.objects.filter(LoginServerID=pk, ForumName=request.user.username).first()

    if not account:
        logger.warning('ACCOUNT_DELETE_DENIED user=%s ip=%s pk=%s', request.user.username, get_client_ip(request), pk)
        messages.error(request, "That account doesn't exist or doesn't belong to you.")
        return redirect("accounts:list_accounts")

    if request.method == "POST":
        typed_name = request.POST.get("account_name", "").strip()
        if typed_name == account.AccountName:
            account.delete()
            logger.info('ACCOUNT_DELETE user=%s ip=%s pk=%s', request.user.username, get_client_ip(request), pk)
            messages.success(request, f"Account '{account.AccountName}' deleted successfully.")
            return redirect("accounts:list_accounts")
        else:
            messages.error(request, "Account name did not match. Please try again.")

    return render(request, "accounts/delete_account.html", {"account": account})


@login_required
def login_history(request):
    history = WebLoginHistory.objects.filter(user=request.user)[:20]
    return render(request, "accounts/login_history.html", {"history": history})


def _get_user_sessions(user, current_key):
    from django.contrib.sessions.models import Session
    user_sessions = []
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        data = session.get_decoded()
        if str(user.pk) == data.get('_auth_user_id'):
            user_sessions.append({
                'session_key': session.session_key,
                'expire_date': session.expire_date,
                'ip_address': data.get('login_ip', 'Unknown'),
                'is_current': session.session_key == current_key,
            })
    user_sessions.sort(key=lambda s: (not s['is_current']))
    return user_sessions


@login_required
def session_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'revoke_all':
            from django.contrib.sessions.models import Session
            for session in Session.objects.filter(expire_date__gte=timezone.now()):
                data = session.get_decoded()
                if str(request.user.pk) == data.get('_auth_user_id'):
                    if session.session_key != request.session.session_key:
                        session.delete()
            logger.info('SESSION_REVOKE_ALL user=%s ip=%s', request.user.username, get_client_ip(request))
            messages.success(request, "All other sessions have been signed out.")

        elif action == 'revoke':
            from django.contrib.sessions.models import Session
            key = request.POST.get('session_key', '')
            if key != request.session.session_key:
                try:
                    session = Session.objects.get(session_key=key, expire_date__gte=timezone.now())
                    data = session.get_decoded()
                    if str(request.user.pk) == data.get('_auth_user_id'):
                        session.delete()
                        logger.info('SESSION_REVOKE user=%s ip=%s', request.user.username, get_client_ip(request))
                        messages.success(request, "Session signed out.")
                except Session.DoesNotExist:
                    pass

        return redirect('accounts:session_management')

    active_sessions = _get_user_sessions(request.user, request.session.session_key)
    return render(request, 'accounts/session_management.html', {'active_sessions': active_sessions})


@login_required
def convert_to_trader(request):
    # Get user's login server accounts
    user_ls_accounts = list(
        LoginServerAccounts.objects.using('login_server_database').filter(
            ForumName=request.user.username
        ).values_list('LoginServerID', flat=True)
    )

    if not user_ls_accounts:
        messages.info(request,
                      "You must create at least one login server account before converting to trader accounts.")
        return redirect('accounts:list_accounts')

    # Get world server accounts that correspond to login server accounts
    world_server_account_ids = list(
        Account.objects.using('game_database').filter(
            lsaccount_id__in=user_ls_accounts
        ).values_list('lsaccount_id', flat=True)
    )

    # Find login server accounts that don't exist on world server yet
    orphaned_ls_accounts = set(user_ls_accounts) - set(world_server_account_ids)

    # Get current mule count and eligible accounts
    mule_count = Account.objects.using('game_database').filter(
        lsaccount_id__in=user_ls_accounts,
        mule=1
    ).count()

    user_account_ids = list(
        Account.objects.using('game_database').filter(
            lsaccount_id__in=user_ls_accounts
        ).values_list('id', flat=True)
    )

    accounts_with_chars = list(
        Characters.objects.filter(
            account_id__in=user_account_ids,
            is_deleted=0
        ).values_list('account_id', flat=True).distinct()
    )

    eligible_accounts = Account.objects.using('game_database').filter(
        lsaccount_id__in=user_ls_accounts,
        mule=0
    ).exclude(id__in=accounts_with_chars)

    trader_accounts = None
    if mule_count >= 2:
        trader_accounts = Account.objects.using('game_database').filter(
            lsaccount_id__in=user_ls_accounts,
            mule=1
        ).values('name', 'id')

    # Handle POST request (conversion)
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        confirmation = request.POST.get('confirmation')

        # Validation
        if not account_id:
            messages.error(request, "Please select an account to convert.")
            return redirect('accounts:convert_to_trader')

        if confirmation != 'CONVERT':
            messages.error(request, "Please type CONVERT to confirm the conversion.")
            return redirect('accounts:convert_to_trader')

        if mule_count >= 2:
            messages.error(request, "You already have the maximum number of trader accounts (2).")
            return redirect('accounts:convert_to_trader')

        # Verify account is still eligible
        try:
            account = Account.objects.using('game_database').get(
                id=account_id,
                lsaccount_id__in=user_ls_accounts,
                mule=0
            )
            if account.id in accounts_with_chars:
                messages.error(request, "This account is no longer eligible - it contains characters.")
                return redirect('accounts:convert_to_trader')

        except Account.DoesNotExist:
            messages.error(request, "Invalid account selection.")
            return redirect('accounts:convert_to_trader')

        account.mule = 1
        # Ensure suspendeduntil has a valid datetime (not None)
        if not account.suspendeduntil or account.suspendeduntil == datetime(1900, 1, 1):  # Handle potential null/invalid dates
            account.suspendeduntil = timezone.now()
        account.save(using='game_database')

        messages.success(request, f"Account '{account.name}' has been successfully converted to a trader account.")
        return redirect('accounts:list_accounts')

    # GET request - show interface
    context = {
        'mule_count': mule_count,
        'max_mules': 2,
        'eligible_accounts': eligible_accounts,
        'at_limit': mule_count >= 2,
        'no_eligible': not eligible_accounts.exists(),
        'trader_accounts': trader_accounts,
        'orphaned_count': len(orphaned_ls_accounts),
        'has_orphaned': len(orphaned_ls_accounts) > 0,
    }

    return render(request, 'accounts/convert_to_trader.html', context)

@login_required
def inventory_search(request):
    """Defines view for https://url.tld/accounts/inventory/search"""

    # Always provide context data for GET requests
    context = {
        "EQUIPMENT_SLOTS": EQUIPMENT_SLOTS,
        "PLAYER_CLASSES": PLAYER_CLASSES,
        "PLAYER_RACES": PLAYER_RACES,
        "ITEM_TYPES": ITEM_TYPES,
        "CONTAINER_TYPES": CONTAINER_TYPES,
        "ITEM_STATS": ITEM_STATS,
    }

    if request.method == "POST":
        if request.user.is_authenticated:
            item_name = request.POST.get("item_name")
            player_class = request.POST.get("player_class")
            player_race = request.POST.get("player_race")
            item_slot = request.POST.get("item_slot")
            item_type = request.POST.get("item_type")
            resists_type = request.POST.get("resists_type")
            resists_operator = request.POST.get("resists_operator")
            resists_value = request.POST.get("resists_value")
            stat1 = request.POST.get("stat1")
            stat1_operator = request.POST.get("stat1_operator")
            stat1_value = request.POST.get("stat1_value")
            stat2 = request.POST.get("stat2")
            stat2_operator = request.POST.get("stat2_operator")
            stat2_value = request.POST.get("stat2_value")
            item_effect = request.POST.get("item_effect")
            item_has_proc = request.POST.get("item_has_proc")
            item_has_click = request.POST.get("item_has_click")
            item_has_focus = request.POST.get("item_has_focus")
            item_has_worn = request.POST.get("item_has_worn")
            container_select = request.POST.get("container_select")
            container_slots = request.POST.get("container_slots")
            container_wr = request.POST.get("container_wr")

            # 1) Get a list of loginserver accounts associated with the currently logged in forum name
            forum_name = request.user.username

            cursor = connections['login_server_database'].cursor()
            cursor.execute("""
                           SELECT LoginServerID
                           FROM tblLoginServerAccounts
                           WHERE ForumName = %s""", [forum_name])
            ls_accounts_results = cursor.fetchall()

            if not ls_accounts_results:
                messages.info(request, "No login server accounts found for your forum account.")
                return render(request, "accounts/inventory_search.html", context)

            # 2) Build the inventory search query with filters
            params_list = []
            where_conditions = []

            base_query = """SELECT ci.itemid,
                              i.icon,
                              i.Name,
                              ci.slotid,
                              ci.charges,
                              i.maxcharges,
                              i.stackable,
                              i.stacksize,
                              cd.name
                       FROM account as acc
                                JOIN character_data as cd ON acc.id = cd.account_id
                                JOIN character_inventory as ci ON cd.id = ci.id
                                JOIN items as i ON i.id = ci.itemid"""

            # Add spell effect joins if needed
            if item_effect:
                base_query += """ LEFT JOIN spells_new AS proc_s ON i.proceffect = proc_s.id
                            LEFT JOIN spells_new AS worn_s ON i.worneffect = worn_s.id
                            LEFT JOIN spells_new AS focus_s ON i.focuseffect = focus_s.id
                            LEFT JOIN spells_new AS click_s ON i.clickeffect = click_s.id"""

            base_query += " WHERE acc.lsaccount_id IN %s"
            params_list.append(ls_accounts_results)

            if item_name:
                where_conditions.append("LOWER(i.Name) LIKE %s")
                params_list.append(f"%{item_name.lower()}%")

            try:
                player_class = int(player_class)
                if player_class != 0:
                    where_conditions.append("(((i.classes & %s) = %s) OR (i.classes = '32767'))")
                    player_class_bitmask = get_class_bitmask(player_class)
                    params_list.append(player_class_bitmask)
                    params_list.append(player_class_bitmask)
            except (ValueError, TypeError):
                if player_class and player_class != "0":
                    messages.error(request, "Invalid player class.")
                    return render(request, "accounts/inventory_search.html", context)

                # Player race filter
            try:
                player_race = int(player_race)
                if player_race != 0:
                    where_conditions.append("(((i.races & %s) = %s) OR (i.races = '16384'))")
                    player_race_bitmask = get_race_bitmask(player_race)
                    params_list.append(player_race_bitmask)
                    params_list.append(player_race_bitmask)
            except (ValueError, TypeError):
                if player_race and player_race != "0":
                    messages.error(request, "Invalid player race.")
                    return render(request, "accounts/inventory_search.html", context)

                # Item slot filter
            try:
                item_slot = int(item_slot)
                if item_slot != 0:
                    where_conditions.append("((i.slots & %s) = %s)")
                    params_list.append(item_slot)
                    params_list.append(item_slot)
            except (ValueError, TypeError):
                if item_slot and item_slot != "0":
                    messages.error(request, "Invalid item slot.")
                    return render(request, "accounts/inventory_search.html", context)

                # Item type filter
            try:
                item_type = int(item_type)
                if item_type != -1:
                    where_conditions.append("i.itemtype = %s")
                    params_list.append(item_type)
            except (ValueError, TypeError):
                if item_type and item_type != "-1":
                    messages.error(request, "Invalid item type.")
                    return render(request, "accounts/inventory_search.html", context)

                # Resist filters
            if resists_type and resists_type != 'Resist':
                try:
                    resists_value = int(resists_value)
                    allowed_resist_types = {'mr': 'mr', 'fr': 'fr', 'cr': 'cr', 'dr': 'dr', 'pr': 'pr'}
                    allowed_operators = {'>': '>', '>=': '>=', '=': '=', '<=': '<=', '<': '<'}

                    if resists_type in allowed_resist_types and resists_operator in allowed_operators:
                        if 0 <= resists_value <= 300:
                            where_conditions.append(f"i.{resists_type} {resists_operator} %s")
                            params_list.append(resists_value)
                        else:
                            messages.error(request,
                                           f"Invalid resist value, '{resists_value}'. Must be between 0 and 300.")
                            return render(request, "accounts/inventory_search.html", context)
                    else:
                        messages.error(request, "Invalid resist type or operator.")
                        return render(request, "accounts/inventory_search.html", context)
                except (ValueError, TypeError):
                    messages.error(request, "Invalid resist value. Must be an integer.")
                    return render(request, "accounts/inventory_search.html", context)

                # Stat filters (you'll need to implement build_stat_query function or inline the logic)
            if stat1 and stat1 != "stat1":
                try:
                    stat1_value = int(stat1_value) if stat1_value else 0
                    allowed_operators = {'>': '>', '>=': '>=', '=': '=', '<=': '<=', '<': '<'}
                    if stat1_operator in allowed_operators and stat1 in ITEM_STATS:
                        where_conditions.append(f"i.{stat1} {stat1_operator} %s")
                        params_list.append(stat1_value)
                    else:
                        messages.error(request, "Invalid stat1 or operator.")
                        return render(request, "accounts/inventory_search.html", context)
                except (ValueError, TypeError):
                    messages.error(request, "Invalid stat1 value.")
                    return render(request, "accounts/inventory_search.html", context)

            if stat2 and stat2 != "stat2":
                try:
                    stat2_value = int(stat2_value) if stat2_value else 0
                    allowed_operators = {'>': '>', '>=': '>=', '=': '=', '<=': '<=', '<': '<'}
                    if stat2_operator in allowed_operators and stat2 in ITEM_STATS:
                        where_conditions.append(f"i.{stat2} {stat2_operator} %s")
                        params_list.append(stat2_value)
                    else:
                        messages.error(request, "Invalid stat2 or operator.")
                except (ValueError, TypeError):
                    messages.error(request, "Invalid stat2 value.")
                    return render(request, "accounts/inventory_search.html", context)

                # Item effect filter
            if item_effect:
                where_conditions.append("""(proc_s.name LIKE %s
                                                      OR worn_s.name LIKE %s
                                                      OR focus_s.name LIKE %s
                                                      OR click_s.name LIKE %s)""")
                params_list.extend([f"%{item_effect}%", f"%{item_effect}%",
                                    f"%{item_effect}%", f"%{item_effect}%"])

                # Effect type filters
            if item_has_proc:
                where_conditions.append("(i.proceffect > 0 and i.proceffect < 4679)")
            if item_has_click:
                where_conditions.append("(i.clickeffect > 0 and i.clickeffect < 4679)")
            if item_has_focus:
                where_conditions.append("(i.focuseffect > 0 and i.focuseffect < 4679) AND i.bagtype = 0")
            if item_has_worn:
                where_conditions.append("(i.worneffect > 0 and i.worneffect < 4679)")

                # Container filters
            if container_select and container_select != "Container":
                where_conditions.append("i.bagtype = %s")
                params_list.append(container_select)
            if container_slots and container_slots != '0':
                try:
                    container_slots = int(container_slots)
                    where_conditions.append("i.bagslots >= %s")
                    params_list.append(container_slots)
                except (ValueError, TypeError):
                    messages.error(request, "Invalid container slots value.")
                    return render(request, "accounts/inventory_search.html", context)
            if container_wr and container_wr != '0':
                try:
                    container_wr = int(container_wr)
                    where_conditions.append("i.bagwr >= %s")
                    params_list.append(container_wr)
                except (ValueError, TypeError):
                    messages.error(request, "Invalid container weight reduction value.")
                    return render(request, "accounts/inventory_search.html", context)

            final_query = base_query
            # Add WHERE conditions to query
            if where_conditions:
                final_query += " AND " + " AND ".join(where_conditions)

            # Add limit to prevent huge result sets
            final_query += " LIMIT 200"

            cursor = connections['game_database'].cursor()
            cursor.execute(final_query, params_list)
            character_inventory_results = cursor.fetchall()

            if len(character_inventory_results) == 0:
                messages.info(request, "No search results found.")
            else:
                items = []
                Item = namedtuple('Item', ['itemid', 'icon', 'item_name', 'slot_id', 'charges', 'max_charges', 'stackable', 'stack_size',
                                           'char_name'])
                items = [Item(*row) for row in character_inventory_results]
                context["search_results"] = sorted(items)

            return render(request=request,
                          template_name="accounts/inventory_search.html",
                          context=context)

    return render(request=request,
                  template_name="accounts/inventory_search.html",
                  context=context
                  )
