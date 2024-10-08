from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.shortcuts import render, redirect

from .models import Account
from .models import LoginServerAccounts
from .models import WorldServerRegistration
from .tables import LoginServerAccountTable

from .forms import ContactForm, NewUserForm, NewLSAccountForm, UpdateLSAccountForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse

from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport

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
    if request.method == "POST":
        if request.user.is_authenticated:
            # 1) Get a list of loginserver accounts associated with the currently logged in forum name
            forum_name = request.user.username

            cursor = connections['login_server_database'].cursor()
            cursor.execute("""
                SELECT LoginServerID
                FROM tblLoginServerAccounts
                WHERE ForumName = %s""", [forum_name])
            ls_accounts_results = cursor.fetchall()

            # 2) For each login server account this user has, get all characters. For each character,
            # show results where the item_name occurs in their inventory
            cursor = connections['game_database'].cursor()
            item_name = request.POST.get("item_name")
            cursor.execute("""SELECT 
                                ci.itemid, 
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
                                JOIN items as i ON i.id = ci.itemid
                              WHERE 
                                acc.lsaccount_id IN %s 
                                AND i.Name LIKE %s""",
                           [ls_accounts_results, "%"+item_name.lower()+"%"])
            character_inventory_results = cursor.fetchall()

            return render(request=request,
                          template_name="accounts/inventory_search.html",
                          context={"search_results": character_inventory_results}
                          )

    return render(request=request,
                  template_name="accounts/inventory_search.html",
                  context={
                  }
                  )
