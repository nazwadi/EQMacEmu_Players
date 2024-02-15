import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Characters
from .models import CharacterCurrency
from .models import CharacterKeyring
from .models import CharacterLanguages
from .models import CharacterSpells
from .models import CharacterSkills
from .models import Guilds
from .models import GuildMembers
from .models import SpellsNew
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

        character_currency = CharacterCurrency.objects.filter(id=character.id).first()
        character_skills_unfiltered = CharacterSkills.objects.filter(id=character.id)
        character_magic_songs = []
        character_skills = []
        for skill in character_skills_unfiltered:
            if skill.skill_id in [4, 5, 12, 13, 14, 18, 24, 31, 41, 43, 44, 45, 46, 47, 49, 54, 70]:
                character_magic_songs.append(skill)
            else:
                character_skills.append(skill)
        character_keyring = CharacterKeyring.objects.filter(id=character.id)
        character_languages = CharacterLanguages.objects.filter(id=character.id)
        scribed_spells = CharacterSpells.objects.filter(id=character.id)
        character_spells = list()
        for spell in scribed_spells:
            try:
                character_spells.append(spell.spell_id.id)
            except ObjectDoesNotExist:
                continue

        spell_list = None
        max_level = 60
        match character.class_name:
            case 1:  # Warrior - might remove, but disciplines are also spells
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes1__gte=1,
                                                       classes1__lte=max_level)
                              .annotate(level=F('classes1'))
                              .order_by('classes1', 'name'))
            case 2:  # Cleric
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes2__gte=1,
                                                       classes2__lte=max_level)
                              .annotate(level=F('classes2'))
                              .order_by('classes2', 'name'))
            case 3:  # Paladin
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes3__gte=1,
                                                       classes3__lte=max_level)
                              .annotate(level=F('classes3'))
                              .order_by('classes3', 'name'))
            case 4:  # Ranger
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes4__gte=1,
                                                       classes4__lte=max_level)
                              .annotate(level=F('classes4'))
                              .order_by('classes4', 'name'))
            case 5:  # Shadowknight
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes5__gte=1,
                                                       classes5__lte=max_level)
                              .annotate(level=F('classes5'))
                              .order_by('classes5', 'name'))
            case 6:  # Druid
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes6__gte=1,
                                                       classes6__lte=max_level)
                              .annotate(level=F('classes6'))
                              .order_by('classes6', 'name'))
            case 7:  # Monk
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes7__gte=1,
                                                       classes7__lte=max_level)
                              .annotate(level=F('classes7'))
                              .order_by('classes7', 'name'))
            case 8:  # Bard
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes8__gte=1,
                                                       classes8__lte=max_level)
                              .annotate(level=F('classes8'))
                              .order_by('classes8', 'name'))
            case 9:  # Rogue
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes9__gte=1,
                                                       classes9__lte=max_level)
                              .annotate(level=F('classes9'))
                              .order_by('classes9', 'name'))
            case 10: # Shaman
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes10__gte=1,
                                                       classes10__lte=max_level)
                              .annotate(level=F('classes10'))
                              .order_by('classes10', 'name'))
            case 11: # Necromancer
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes11__gte=1,
                                                       classes11__lte=max_level)
                              .annotate(level=F('classes11'))
                              .order_by('classes11', 'name'))
            case 12:  # Wizard
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes12__gte=1,
                                                       classes12__lte=max_level)
                              .annotate(level=F('classes12'))
                              .order_by('classes12', 'name'))
            case 13:  # Magician
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes13__gte=1,
                                                       classes13__lte=max_level)
                              .annotate(level=F('classes13'))
                              .order_by('classes13', 'name'))
            case 14:  # Enchanter
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes14__gte=1,
                                                       classes14__lte=max_level)
                              .annotate(level=F('classes14'))
                              .order_by('classes14', 'name'))
            case 15:  # Beastlord
                spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                       classes15__gte=1,
                                                       classes15__lte=max_level)
                              .annotate(level=F('classes15'))
                              .order_by('classes15', 'name'))
        # 0 - Unknown, 1 - Warrior, 7 - Monk, 9 - Rogue
        non_casters = [0, 1, 7, 9]
        guild_members = GuildMembers.objects.filter(char_id=character.id).first()
        if guild_members is not None:
            guild_id = guild_members.guild_id
            guild = Guilds.objects.filter(id=int(guild_id.id)).first()
            guild_members = GuildMembers.objects.filter(guild_id=guild.id)
        else:
            guild = None
        last_login = datetime.datetime.fromtimestamp(character.last_login)
        birthday = datetime.datetime.fromtimestamp(character.birthday)
        time_played = datetime.timedelta(seconds=character.time_played)
        face_image = "race_" + str(character.race) + "_gender_" + str(character.gender) + "_face_" + str(
            character.face) + ".png"
        return render(request=request, template_name="characters/view.html",
                      context={
                          "account": account,
                          "birthday": birthday,
                          "character": character,
                          "character_keyring": character_keyring,
                          "character_languages": character_languages,
                          "character_spells": character_spells,
                          "character_skills": character_skills,
                          "character_magic_songs": character_magic_songs,
                          "character_currency": character_currency,
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
