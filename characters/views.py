import datetime

from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Characters
from .models import CharacterCurrency
from .models import GuildMembers
from accounts.models import Account

from characters.utils import valid_game_account_owner


def index_request(request):
    if request.method == "GET":
        return render(request=request, template_name="characters/index.html")
    return redirect("accounts:login")


@login_required
def list_characters(request, game_account_name):
    if request.method == "GET":

        forum_name = request.user.username
        if not valid_game_account_owner(forum_name, game_account_name):
            raise Http404("This account does not exist")

        game_account = Account.objects.filter(name=game_account_name)
        try:
            game_account_id = game_account.values('id')[0]
        except IndexError:
            raise Http404("This account does not exist")

        if game_account_id is not None:
            characters = Characters.objects.filter(account_id=game_account_id['id'])
            return render(request=request, template_name="characters/list.html",
                          context={"characters": characters, }
                          )
    return redirect("accounts:login")


@login_required
def view_character(request, character_name):
    if request.method == "GET":

        character = Characters.objects.filter(name=character_name).first()
        if character is None:
            raise Http404("This character does not exist")
        account = Account.objects.filter(id=character.account_id).first()

        forum_name = request.user.username
        if not valid_game_account_owner(forum_name, account.name):
            raise Http404("This account does not exist")

        currency = CharacterCurrency.objects.filter(id=character.id).first()
        # guild_members = GuildMembers.objects.filter(id=character.id).first()
        last_login = datetime.datetime.fromtimestamp(character.last_login)
        birthday = datetime.datetime.fromtimestamp(character.birthday)
        time_played = datetime.timedelta(seconds=character.time_played)
        return render(request=request, template_name="characters/view.html",
                      context={"character": character,
                               "account_name": account.name,
                               "currency": currency,
                               # "guild_members": guild_members,
                               "last_login": last_login,
                               "time_played": time_played,
                               "birthday": birthday,
                               "status": account.status,
                               }
                      )
    return redirect("accounts:login")
