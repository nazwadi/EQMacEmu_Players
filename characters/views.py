import datetime
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connections

from common.models.characters import Characters
from common.models.characters import CharacterCurrency
from common.models.characters import CharacterLanguages
from common.models.items import DiscoveredItems
from common.utils import valid_game_account_owner
from common.constants import PLAYER_RACIAL_EXP_MODIFIERS

from accounts.models import Account

from characters.utils import get_character_keyring
from characters.utils import get_character_inventory
from characters.utils import get_faction_information
from characters.utils import get_guild_information
from characters.utils import get_skill_information
from characters.utils import get_spell_information
from characters.utils import get_owned_characters
from characters.utils import get_exp_for_level
from characters.utils import get_consider_levels
from characters.utils import rule_of_six


def index_request(request):
    if request.method == "GET":
        return render(request=request, template_name="characters/index.html")
    return redirect("accounts:login")

def experience(request, race_id=None):
    if race_id is not None:
        cursor = connections['game_database'].cursor()
        cursor.execute("""SELECT level, exp_mod, aa_exp_mod FROM level_exp_mods""")
        exp_mod = cursor.fetchall()
        level_data = []
        prev_xp =  0

        for level in range(1, 66): # levels 1 through 65 (non-inclusive of last value)
            current_xp = get_exp_for_level(level, race_id)
            difference = current_xp - prev_xp
            consider_levels = get_consider_levels(level)
            six_rule = rule_of_six(level)
            level_data.append({
                'level': level,
                'experience': current_xp,
                'difference': difference,
                'con_levels': consider_levels,
                'exp_mod': exp_mod[level-1][1],
                'six_rule': six_rule
            })
            prev_xp = current_xp
        selected_race, racial_modifier = PLAYER_RACIAL_EXP_MODIFIERS.get(race_id, 0)

        return render(request=request, template_name="characters/exp.html",
                      context={"PLAYER_RACIAL_EXP_MODIFIERS": PLAYER_RACIAL_EXP_MODIFIERS,
                               "level_data": level_data,
                               "selected_race": selected_race,
                               "racial_modifier": racial_modifier,
                               "race": race_id})
    else:
        return render(request=request, template_name="characters/exp.html",
                      context={"PLAYER_RACIAL_EXP_MODIFIERS": PLAYER_RACIAL_EXP_MODIFIERS,})

@login_required
def list_characters(request, game_account_name):
    """
    Defines view for https://url.tld/characters/list/<str:game_account_name>

    :param request:
    :param game_account_name:
    :return:
    """
    if request.method == "GET":

        forum_name = request.user.username
        game_account = Account.objects.filter(name__iexact=game_account_name).first()
        if game_account is None:
            messages.error(request, "The world server has not seen this account. If this account is new, "
                                    "please log in to character select first.")
            return redirect("accounts:list_accounts")
        if not valid_game_account_owner(forum_name, str(game_account.id)):
            raise Http404("Either this account does not exist or does not belong to you.  If you have registered this "
                          "account with the login server, you must log in to the game server at least once before "
                          "attempting to view this page.")

        if game_account.id is not None:
            characters = Characters.objects.filter(account_id=game_account.id)
            return render(request=request, template_name="characters/list.html",
                          context={"characters": characters,
                                   "game_account_name": game_account.name, }
                          )
    return redirect("accounts:login")


@login_required
def view_character(request, character_name):
    """
    Defines view for https://url.tld/characters/view/<str:character_name>

    :param request:
    :param character_name:
    :return:
    """
    if request.method == "GET":

        character = Characters.objects.filter(name=character_name).first()
        if character is None:
            raise Http404("This character does not exist")

        account = Account.objects.filter(id=character.account_id).first()

        forum_name = request.user.username
        if not valid_game_account_owner(forum_name, str(account.id)):
            raise Http404("This account does not exist")

        character_currency = CharacterCurrency.objects.filter(id=character.id).first()

        character_magic_songs, character_skills = get_skill_information(character_id=character.id)

        character_keyring = get_character_keyring(character_id=character.id)

        character_languages = CharacterLanguages.objects.filter(id=character.id)

        character_faction_values = get_faction_information(character_id=character.id,
                                                           race_id=character.race,
                                                           class_id=character.class_name,
                                                           deity_id=character.deity)

        character_spells, spell_list = get_spell_information(character_id=character.id,
                                                             class_id=character.class_name)

        discovered_items = DiscoveredItems.objects.filter(char_name=character.name)

        # 0 - Unknown, 1 - Warrior, 7 - Monk, 9 - Rogue
        non_casters = [0, 1, 7, 9]

        guild, guild_members = get_guild_information(character_id=character.id)

        character_inventory = get_character_inventory(character_id=character.id)

        character_list = get_owned_characters(forum_name=request.user.username)

        last_login = datetime.datetime.fromtimestamp(character.last_login)
        birthday = datetime.datetime.fromtimestamp(character.birthday)
        time_played = datetime.timedelta(seconds=character.time_played)
        face_image = ''.join(["race_", str(character.race), "_gender_",
                              str(character.gender), "_face_", str(character.face), ".png"])
        return render(request=request, template_name="characters/view.html",
                      context={
                          "account": account,
                          "birthday": birthday,
                          "character": character,
                          "character_currency": character_currency,
                          "character_faction_values": character_faction_values,
                          "character_inventory": character_inventory,
                          "character_keyring": character_keyring,
                          "character_languages": character_languages,
                          "character_list": character_list,
                          "character_magic_songs": character_magic_songs,
                          "character_skills": character_skills,
                          "character_spells": character_spells,
                          "discovered_items": discovered_items,
                          "face_image": face_image,
                          "guild": guild,
                          "guild_members": guild_members,
                          "last_login": last_login,
                          "non_casters": non_casters,
                          "time_played": time_played,
                          "spell_list": spell_list,
                      }
                      )

    return redirect("accounts:login")
