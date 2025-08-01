from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import BadHeaderError, send_mail
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import redirect, render

from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport

from common.constants import (
    CONTAINER_TYPES,
    EQUIPMENT_SLOTS,
    ITEM_STATS,
    ITEM_TYPES,
    PLAYER_CLASSES,
    PLAYER_RACES,
)
from items.utils import build_stat_query, get_class_bitmask, get_item_effect, get_race_bitmask

from .forms import ContactForm, NewLSAccountForm, NewUserForm, UpdateLSAccountForm
from .models import Account, LoginServerAccounts, WorldServerRegistration
from .tables import LoginServerAccountTable
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


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("accounts:list_accounts")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="accounts/login.html", context={"login_form": form})


@login_required
def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("accounts:index")


def register_request(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("accounts:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render(request, "accounts/register.html", {'form': form})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry"
            body = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email_address'],
                'message': form.cleaned_data['message'],
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, 'admin@example.com', ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("accounts:index")

    form = ContactForm()
    return render(request, "accounts/contact.html", {'form': form})


@login_required
def accounts(request):
    table = LoginServerAccountTable(LoginServerAccounts.objects.filter(ForumName=request.user.username))

    RequestConfig(request).configure(table)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table)
        return exporter.response(f"table.{export_format}")

    return render(request,
                  "accounts/list_accounts.html",
                  {"table": table})


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
    queryset = LoginServerAccounts.objects.filter(LoginServerID=pk)
    data = queryset.values()[0]
    if queryset.values() and request.user.username == queryset.values().first()['ForumName']:
        if request.method == 'POST':
            form = UpdateLSAccountForm(request.POST)
            if form.is_valid():
                queryset.update(AccountPassword=sha1_password(form.cleaned_data['AccountPassword']),
                                AccountEmail=form.cleaned_data['AccountEmail'],
                                LastIPAddress=get_client_ip(request))
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


@login_required
def delete_account(request, pk):
    """Defines view for https://url.tld/accounts/delete/<int:pk>"""
    account = LoginServerAccounts.objects.filter(LoginServerID=pk)
    if account.values() and request.user.username == account.values().first()['ForumName']:
        account.delete()
        messages.success(request, "Account deleted successfully.")
        return redirect("accounts:list_accounts")

    messages.error(request,
                   "Unsuccessful delete attempt. The target account either does not exist or doesn't belong to you.")
    return redirect("accounts:list_accounts")


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

            context["search_results"] = character_inventory_results

            return render(request=request,
                          template_name="accounts/inventory_search.html",
                          context=context)

    return render(request=request,
                  template_name="accounts/inventory_search.html",
                  context=context
                  )
