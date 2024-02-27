from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.shortcuts import render, redirect
from accounts.models import Account
from accounts.models import LoginServerAccounts

from character_transfer.utils import valid_game_account_owner
from character_transfer.utils import valid_character_ownership


@login_required
def index(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            forum_name = request.user.username
            ls_accounts = LoginServerAccounts.objects.filter(ForumName=forum_name)
            game_accounts = [Account.objects.filter(lsaccount_id=account.LoginServerID) for account in ls_accounts]
            characters = list()
            accounts = list()
            for account in game_accounts:
                try:
                    accounts.append(account.values('id', 'name')[0])
                    game_account_id = account.values('id')[0]['id']
                except IndexError:
                    continue
                if game_account_id is not None:
                    cursor = connections['game_database'].cursor()
                    cursor.execute(
                        """SELECT cd.id, cd.name, a.id, a.Name 
                           FROM character_data as cd LEFT OUTER JOIN account as a ON cd.account_id = a.id 
                           WHERE cd.account_id  = '%s' 
                           ORDER BY cd.name;""", [game_account_id])
                    result = cursor.fetchall()

                    for character in result:
                        characters.append(character)

            return render(request=request,
                          template_name="character_transfer/index.html",
                          context={"characters": characters,
                                   "accounts": accounts, })
    if request.method == "POST":
        if request.user.is_authenticated:
            forum_name = request.user.username
            account_id = request.POST.get("account")
            character_id = request.POST.get("character")
            if (not valid_game_account_owner(forum_name, account_id) or
                    not valid_character_ownership(forum_name, character_id)):
                messages.error(request,
                               "Unsuccessful character transfer attempt. \
                               The target account either does not exist or doesn't belong to you.")
                return redirect("character_transfer:index")
            cursor = connections['game_database'].cursor()
            account_id = request.POST.get("account")
            character_id = request.POST.get("character")
            query = "UPDATE character_data SET account_id = %s WHERE id = %s;"
            cursor.execute(query, [account_id, character_id])
            messages.success(request, "Character transfer successful.")
            return redirect("character_transfer:index")

    return redirect("accounts:login")
