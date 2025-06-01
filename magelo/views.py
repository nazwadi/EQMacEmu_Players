from enum import IntEnum
from enum import Enum
from typing import Union
import math
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404
from django.http import JsonResponse
from django.http import HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.core.cache import cache

from .models import CharacterPermissions
from .validators import PermissionValidator
from .utils import level_regen
from .utils import calc_hp_regen_cap

from common.utils import valid_game_account_owner
from common.models.characters import Characters, CharacterSkills
from common.models.characters import CharacterInventory
from common.models.characters import CharacterCurrency
from common.models.guilds import GuildMembers
from common.models.items import Items

from characters.utils import get_character_keyring


class FlowingThoughtEffects(Enum):
    """Spell IDs for all known item-based Flowing Thought Spell Effects"""
    FLOWING_THOUGHT_I = 1298
    FLOWING_THOUGHT_II = 1299
    FLOWING_THOUGHT_III = 1300
    FLOWING_THOUGHT_IV = 1301
    FLOWING_THOUGHT_V = 1302
    FLOWING_THOUGHT_VI = 1303
    FLOWING_THOUGHT_VII = 1304
    FLOWING_THOUGHT_VIII = 1305
    FLOWING_THOUGHT_IX = 1306
    FLOWING_THOUGHT_X = 1307

    @classmethod
    def has_value(cls, value):
        return value in [e.value for e in cls]

    @classmethod
    def get_tier(cls, spell_id):
        """Convert spell ID to its tier (1-9)"""
        return {
            cls.FLOWING_THOUGHT_I.value: 1,
            cls.FLOWING_THOUGHT_II.value: 2,
            cls.FLOWING_THOUGHT_III.value: 3,
            cls.FLOWING_THOUGHT_IV.value: 4,
            cls.FLOWING_THOUGHT_V.value: 5,
            cls.FLOWING_THOUGHT_VI.value: 6,
            cls.FLOWING_THOUGHT_VII.value: 7,
            cls.FLOWING_THOUGHT_VIII.value: 8,
            cls.FLOWING_THOUGHT_IX.value: 9,
            cls.FLOWING_THOUGHT_X.value: 10,
        }.get(spell_id)


class ItemStats:
    """Helper class to track item statistics and bonuses"""

    def __init__(self):
        self.items = []
        self.total_weight = 0
        self.total_ac = 0
        self.total_hp = 0
        self.total_mana = 0
        self.stat_bonuses = {
            'str': 0, 'sta': 0, 'agi': 0, 'dex': 0,
            'int': 0, 'wis': 0, 'cha': 0,
            'fr': 0, 'cr': 0, 'mr': 0, 'dr': 0, 'pr': 0
        }
        self.str_cap = 255
        self.sta_cap = 255
        self.agi_cap = 255
        self.dex_cap = 255
        self.int_cap = 255
        self.wis_cap = 255
        self.cha_cap = 255
        self.fr_cap = 300
        self.cr_cap = 300
        self.mr_cap = 300
        self.dr_cap = 300
        self.pr_cap = 300
        self.ft_cap = 15
        self.atk_cap = 250
        self.ds = 0
        self.haste = 0
        self.haste_cap = 100
        self.regen = 0
        self.ft = 0
        self.atk = 0

    def add_item(self, item):
        """Add item and accumulate its stats"""
        self.items.append(item)
        self.total_weight += item.weight
        self.total_ac += item.ac
        self.total_hp += item.hp
        self.total_mana += item.mana

        if item.worn_effect == 998: # Haste
            self.haste += item.worn_level + 1

        if FlowingThoughtEffects.has_value(item.worn_effect):
            self.ft += FlowingThoughtEffects.get_tier(item.worn_effect)

        # Add stat bonuses
        self.stat_bonuses['str'] += item.astr
        self.stat_bonuses['sta'] += item.asta
        self.stat_bonuses['agi'] += item.aagi
        self.stat_bonuses['dex'] += item.adex
        self.stat_bonuses['int'] += item.aint
        self.stat_bonuses['wis'] += item.awis
        self.stat_bonuses['cha'] += item.acha
        self.stat_bonuses['fr'] += item.fr
        self.stat_bonuses['cr'] += item.cr
        self.stat_bonuses['mr'] += item.mr
        self.stat_bonuses['dr'] += item.dr
        self.stat_bonuses['pr'] += item.pr


def get_permissions(user, character_name, gm_level, anon_level):
    """
    Calculate viewing permissions based on stored user permissions, GM level, and anonymity level

    Args:
        user: The Django user object
        character_name: The name of the character
        gm_level: Integer representing GM level
        anon_level: Integer representing anonymity level

    Returns:
        dict: Permission states for various features
    """
    # Start with default false permissions
    base_permissions = {
        'inventory': False,
        'bags': False,
        'bank': False,
        'coin_inventory': False,
        'coin_bank': False
    }

    try:
        # Get user's stored permissions
        character_permissions = CharacterPermissions.get_or_create_permissions(character_name)

        # Update base permissions with stored permissions
        for permission in base_permissions.keys():
            base_permissions[permission] = getattr(character_permissions, permission, False)

        # If user is GM or anonymous, override permissions
        if gm_level > 0 or anon_level > 0:
            return base_permissions

        # For normal users (non-GM, non-anonymous), use their stored permissions
        return base_permissions

    except Exception as e:
        # Log the error and return base permissions if something goes wrong
        print(f"Error getting permissions for user {user}: {str(e)}")
        return base_permissions


@require_http_methods(["GET", "POST"])
def search(request):
    if request.method == "GET":
        return render(request=request,
                      context={
                      },
                      template_name="magelo/search.html")
    if request.method == "POST":
        character_name = request.POST.get("character_name")
        search_results = Characters.objects.filter(name__icontains=character_name)[:50]
        return render(request=request,
                      context={
                          "search_results": search_results
                      },
                      template_name="magelo/search.html")
    return HttpResponseNotAllowed(['GET', 'POST']) # This will never be reached due to the decorator

def character_profile(request, character_name):
    character = Characters.objects.filter(name=character_name).first()
    if character is None:
        raise Http404("This character does not exist")

    character_stats = CharacterSkills.objects.filter(id=character.id)
    defense = character_stats.filter(skill_id=15).first()
    offense = character_stats.filter(skill_id=33).first()
    if character is None:
        raise Http404

    is_character_owner = valid_game_account_owner(request.user.username, str(character.account_id))

    # Get permissions
    permissions = get_permissions(request.user, character_name, character.gm, character.anon)

    # Block view if user doesn't have permission
    # if not permissions['inventory'] and not request.user.is_staff:
    #     raise Http404("You don't have permission to view this inventory")

    character_currency = CharacterCurrency.objects.filter(id=character.id).first()

    # Get guild info using proper model relationships
    try:
        guild_member = GuildMembers.objects.select_related('guild_id').get(char_id=character)
        guild_info = {
            'name': guild_member.guild_id.name,
            'rank': guild_member.rank
        }
    except GuildMembers.DoesNotExist:
        guild_info = {'name': '', 'rank': None}

    # Initialize stats tracking
    item_stats = ItemStats()

    # Get inventory items with related Items data
    inventory_items = CharacterInventory.objects.filter(
        id=character.id
    ).values('slot_id', 'item_id', 'charges')

    # Process items and build all_items dictionary
    all_items = {}
    item_objects = {item.id: item for item in Items.objects.filter(
        id__in=[inv['item_id'] for inv in inventory_items]
    )}

    for inv_item in inventory_items:
        item = item_objects.get(inv_item['item_id'])
        if item:
            item_data = {
                'slot': inv_item['slot_id'],
                'id': item.id,
                'name': item.Name,
                'icon': item.icon,
                'icon_url': f"/static/magelo/items/item_{item.icon}.png",
                'slots': item.slots,
                'weight': item.weight,
                'charges': inv_item['charges'],
                'bag_slots': item.bag_slots,
                'lore': item.lore,
                'no_drop': item.no_drop,
                'no_rent': item.no_rent,
                'magic': item.magic,
                'stackable': item.stackable,
            }

            # Add to all_items dictionary
            all_items[inv_item['slot_id']] = item_data

            # Update stats if equipment slot
            if inv_item['slot_id'] < 22:  # Equipment slots
                item_stats.add_item(item)

    # Calculate total stats including items
    total_stats = {
        'str': character.str + item_stats.stat_bonuses['str'],
        'sta': character.sta + item_stats.stat_bonuses['sta'],
        'agi': character.agi + item_stats.stat_bonuses['agi'],
        'dex': character.dex + item_stats.stat_bonuses['dex'],
        'int': character.int_stat + item_stats.stat_bonuses['int'],
        'wis': character.wis + item_stats.stat_bonuses['wis'],
        'cha': character.cha + item_stats.stat_bonuses['cha'],
        'fr': fr_by_race(character.race) + fr_by_class(character.class_name, character.level) + item_stats.stat_bonuses['fr'],
        'cr': cr_by_race(character.race) + cr_by_class(character.class_name, character.level) + item_stats.stat_bonuses['cr'],
        'mr': mr_by_race(character.race) + mr_by_class(character.class_name, character.level) + item_stats.stat_bonuses['mr'],
        'dr': dr_by_race(character.race) + dr_by_class(character.class_name, character.level) + item_stats.stat_bonuses['dr'],
        'pr': pr_by_race(character.race) + pr_by_class(character.class_name, character.level) + item_stats.stat_bonuses['pr'],
    }
    troll = 9
    iksar = 128
    has_racial_regen_bonus = True if character.race in [troll, iksar] else False
    hp_regen = level_regen(level=character.level,
                            is_sitting=False,
                            is_resting=False,
                            is_feigned=False,
                            is_famished=False,
                            has_racial_regen_bonus=has_racial_regen_bonus)
    hp_regen_cap = calc_hp_regen_cap(character.level)
    ac = get_max_ac(character.agi, character.level, defense.value, character.class_name, item_stats.total_ac,
                     character.race)
    atk = get_max_attack(item_stats.atk, character.str + item_stats.stat_bonuses['str'], offense.value)
    print(character.class_name)
    mana = get_max_mana(character.level, character.class_name, character.int_stat, character.wis, item_stats.total_mana)

    # Build context
    context = {
        'is_character_owner': is_character_owner,
        'character': {
            'name': character.name,
            'last_name': character.last_name,
            'title': character.title,
            'level': character.level,
            'class_name': character.class_name,
            'race_name': character.race,
            'deity': character.deity,
            'base_stats': {
                'str': character.str,
                'sta': character.sta,
                'cha': character.cha,
                'dex': character.dex,
                'int': character.int_stat,
                'agi': character.agi,
                'wis': character.wis,
            },
            'total_stats': total_stats,
            'cur_hp': character.cur_hp,
            'mana': mana,
            'hp_regen_cap': hp_regen_cap,
            'hp_regen': hp_regen,
            'ac' : ac,
            'atk': atk,
        },
        'magelo': True, # just a variable to let the templates know this is the magelo page
        'guild': guild_info,
        'inventory_items': all_items,
        'currency': character_currency,
        'permissions': permissions,
        'item_stats': item_stats,
    }

    return render(request=request, template_name='magelo/character_profile.html', context=context)

def character_keys(request, character_name):
    character = Characters.objects.filter(name=character_name).first()
    if character is None:
        raise Http404("This character does not exist")
    character_keyring = get_character_keyring(character_id=character.id)
    context = {
        'character': character,
        'keys': character_keyring
    }
    return render(request=request, template_name='magelo/character_keys.html', context=context)


def get_max_mana(level, class_type, int_stat, wis_stat, imana):
    """
    Calculate maximum mana for a character.
    Modified from the https://github.com/EQMacEmu/magelo/blob/5289e3256c2f8d23f8a5434219fdfcb7a14ebd1c/include/calculatestats.php#L821

    Args:
        level: Character level
        class_type: Character class
        int_stat: Intelligence stat
        wis_stat: Wisdom stat
        imana: Additional mana modifier

    Returns:
        Maximum mana as an integer
    """
    # The next two lines should be updated when AAs lift the stat cap.
    int_stat = min(255, int_stat)
    wis_stat = min(255, wis_stat)

    wis_int = 0
    mind_lesser_factor = 0
    mind_factor = 0
    max_m = 0
    wisint_mana = 0
    base_mana = 3.8505 * level + 0.1869 * level * min(200, int_stat) + 0.0907 * level * (max(200, int_stat) - 200)
    converted_wis_int = 0

    caster_class = get_caster_class(class_type)

    if caster_class == 'I':
        wis_int = int_stat
        if wis_int > 100:
            converted_wis_int = (((wis_int - 100) * 5 / 2) + 100)
            if wis_int > 201:
                converted_wis_int -= ((wis_int - 201) * 5 / 4)
        else:
            converted_wis_int = wis_int

        if level < 41:
            wisint_mana = (level * 75 * converted_wis_int / 1000)
            base_mana = (level * 15)
        elif level < 81:
            wisint_mana = ((3 * converted_wis_int) + ((level - 40) * 15 * converted_wis_int / 100))
            base_mana = (600 + ((level - 40) * 30))
        else:
            wisint_mana = (9 * converted_wis_int)
            base_mana = (1800 + ((level - 80) * 18))

        max_mana = base_mana + wisint_mana
        max_mana += imana

    elif caster_class == 'W':
        wis_int = wis_stat
        if wis_int > 100:
            converted_wis_int = (((wis_int - 100) * 5 / 2) + 100)
            if wis_int > 201:
                converted_wis_int -= ((wis_int - 201) * 5 / 4)
        else:
            converted_wis_int = wis_int

        if level < 41:
            wisint_mana = (level * 75 * converted_wis_int / 1000)
            base_mana = (level * 15)
        elif level < 81:
            wisint_mana = ((3 * converted_wis_int) + ((level - 40) * 15 * converted_wis_int / 100))
            base_mana = (600 + ((level - 40) * 30))
        else:
            wisint_mana = (9 * converted_wis_int)
            base_mana = (1800 + ((level - 80) * 18))

        max_mana = base_mana + wisint_mana
        max_mana += imana

    elif caster_class == 'N':
        max_mana = 0
    else:
        max_mana = 0

    return int(max_mana)


def get_caster_class(class_id):
    """
    Determine caster type based on class ID.
    Function copied/converted from EQEMU sourcecode may 2, 2009
    """
    # Class constants
    WARRIOR = 1
    CLERIC = 2
    PALADIN = 3
    RANGER = 4
    SHADOWKNIGHT = 5
    DRUID = 6
    MONK = 7
    BARD = 8
    ROGUE = 9
    SHAMAN = 10
    NECROMANCER = 11
    WIZARD = 12
    MAGICIAN = 13
    ENCHANTER = 14
    BEASTLORD = 15
    BERSERKER = 16

    caster_types = {
        # Wisdom-based casters
        CLERIC: 'W',
        PALADIN: 'W',
        RANGER: 'W',
        DRUID: 'W',
        SHAMAN: 'W',
        BEASTLORD: 'W',

        # Intelligence-based casters
        SHADOWKNIGHT: 'I',
        BARD: 'I',
        NECROMANCER: 'I',
        WIZARD: 'I',
        MAGICIAN: 'I',
        ENCHANTER: 'I',
    }

    return caster_types.get(class_id, 'N')  # Default to 'N' for non-casters


def rate_limit_by_user(user_id, key_prefix, max_requests=5, time_window=60):
    cache_key = f"rate_limit:{key_prefix}:{user_id}"
    requests = cache.get(cache_key, 0)
    if requests >= max_requests:
        raise PermissionDenied("Too many requests. Please try again later.")
    cache.set(cache_key, requests + 1, time_window)

@login_required
@require_http_methods(["POST"])
def update_permission(request):
    try:
        rate_limit_by_user(request.user.id, "update_permission")

        content_length = int(request.headers.get('Content-Length', 0))
        if content_length > 1024:  # 1KB limit
            raise PermissionDenied("Request too large")

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        try:
            validated_data = PermissionValidator.validate_permission_data(data)
            permission = validated_data['permission']
            value = validated_data['value']
            character_name = data.get('character_name')

            if not character_name:
                return JsonResponse(
                    {'success': False, 'error': 'character_name is required'},
                    status=400
                )

        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        # Verify character ownership
        character = Characters.objects.filter(name=character_name).first()
        if not character:
            return JsonResponse({'success': False, 'error': 'Character not found'}, status=404)

        if not valid_game_account_owner(request.user.username, str(character.account_id)):
            raise PermissionDenied("You don't have permission to modify this character")

        # Get or create character permissions
        character_permissions = CharacterPermissions.get_or_create_permissions(character_name)

        # Add audit logging
        from django.contrib.admin.models import LogEntry, CHANGE
        from django.contrib.contenttypes.models import ContentType
        LogEntry.objects.create(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(CharacterPermissions).id,
            object_id=character_permissions.id,
            object_repr=character_name,
            action_flag=CHANGE,
            change_message=f"Changed {permission} to {value}"
        )

        # Update the permission with transaction
        from django.db import transaction
        with transaction.atomic():
            setattr(character_permissions, permission, value)
            character_permissions.save()

        return JsonResponse({
            'success': True,
            'message': f'{permission.replace("_", " ").title()} {"enabled" if value else "disabled"} for {character_name}'
        })

    except PermissionDenied as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        # Log the error but don't expose details to client
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in update_permission: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'{str(e)} An error occurred processing your request'
        }, status=500)

class CharacterClass(IntEnum):
    """Character class constants using IntEnum for better type safety"""
    WARRIOR = 1
    CLERIC = 2
    PALADIN = 3
    RANGER = 4
    SHADOWKNIGHT = 5
    DRUID = 6
    MONK = 7
    BARD = 8
    ROGUE = 9
    SHAMAN = 10
    NECROMANCER = 11
    WIZARD = 12
    MAGICIAN = 13
    ENCHANTER = 14
    BEASTLORD = 15
    BERSERKER = 16

class Race(IntEnum):
    """Race constants"""
    HUMAN = 1
    BARBARIAN = 2
    ERUDITE = 3
    DWARF = 8
    TROLL = 9
    HALFLING = 11
    IKSAR = 128

def pr_by_race(race):
    """Calculate Poison Resistance by race"""
    if race in (Race.DWARF, Race.HALFLING):
        return 20
    return 15

def mr_by_race(race):
    """Calculate Magic Resistance by race"""
    if race in (Race.ERUDITE, Race.DWARF):
        return 30
    return 25

def dr_by_race(race):
    """Calculate Disease Resistance by race"""
    if race == Race.ERUDITE:
        return 10
    elif race == Race.HALFLING:
        return 20
    return 15

def fr_by_race(race):
    """Calculate Fire Resistance by race"""
    if race == Race.TROLL:
        return 5
    elif race == Race.IKSAR:
        return 30
    return 25

def cr_by_race(race):
    """Calculate Cold Resistance by race"""
    if race == Race.BARBARIAN:
        return 35
    elif race == Race.IKSAR:
        return 15
    return 25

def pr_by_class(char_class, char_level):
    """Calculate Poison Resistance by class and level"""
    if char_class == CharacterClass.SHADOWKNIGHT:
        return (char_level - 49) + 4 if char_level >= 50 else 4
    elif char_class == CharacterClass.ROGUE:
        return (char_level - 49) + 8 if char_level >= 50 else 8
    return 0

def mr_by_class(char_class, char_level):
    """Calculate Magic Resistance by class and level"""
    if char_class == CharacterClass.WARRIOR:
        return char_level // 2
    return 0

def dr_by_class(char_class, char_level):
    """Calculate Disease Resistance by class and level"""
    if char_class == CharacterClass.PALADIN:
        return (char_level - 49) + 8 if char_level >= 50 else 8
    elif char_class in (CharacterClass.SHADOWKNIGHT, CharacterClass.BEASTLORD):
        return (char_level - 49) + 4 if char_level >= 50 else 4
    return 0

def fr_by_class(char_class, char_level):
    """Calculate Fire Resistance by class and level"""
    if char_class == CharacterClass.RANGER:
        return (char_level - 49) + 4 if char_level >= 50 else 4
    elif char_class == CharacterClass.MONK:
        return (char_level - 49) + 8 if char_level >= 50 else 8
    return 0

def cr_by_class(char_class, char_level):
    """Calculate Cold Resistance by class and level"""
    if char_class in (CharacterClass.RANGER, CharacterClass.BEASTLORD):
        return (char_level - 49) + 4 if char_level >= 50 else 4
    return 0

def get_max_ac(agility: int, level: int, defense: int,
               char_class: Union[int, CharacterClass],
               iac: int, race: Union[int, Race]) -> int:
    """
    Calculate maximum AC for a character.

    Args:
        agility: Character's agility stat
        level: Character level
        defense: Defense skill value
        char_class: Character class (int or CharacterClass enum)
        iac: Item AC value
        race: Character race (int or Race enum)

    Returns:
        Maximum AC value (floored)
    """
    # Calculate avoidance component
    avoidance = max(0, acmod(agility, level) + (defense * 16 / 9))

    # Calculate mitigation based on class
    caster_classes = {CharacterClass.WIZARD, CharacterClass.MAGICIAN,
                      CharacterClass.NECROMANCER, CharacterClass.ENCHANTER}

    if char_class in caster_classes:
        mitigation = defense / 4 + (iac + 1) - 4
    else:
        mitigation = defense / 3 + (iac * 4 / 3)
        if char_class == CharacterClass.MONK:
            mitigation += level * 1.3  # More readable than 13/10

    # Calculate natural AC
    natural_ac = (avoidance + mitigation) * 1000 / 847

    # Apply racial bonuses
    if race == Race.IKSAR:
        natural_ac += 12
        # Iksar level bonus (capped at 25 levels above 10)
        iksar_bonus_levels = min(25, max(0, level - 10))
        natural_ac += iksar_bonus_levels * 1.2  # More readable than 12/10

    return math.floor(natural_ac)

def acmod(agility: int, level: int) -> float:
    """
    Calculate agility modifier for AC based on agility and level.

    This function implements complex game logic for calculating AC modifiers
    based on character agility and level ranges.

    Args:
        agility: Character's agility stat
        level: Character level

    Returns:
        Agility modifier value for AC calculation
    """
    if agility < 1 or level < 1:
        return 0

    # Define lookup tables for cleaner code
    low_agility_map = {
        1: -24, 2: -23, 3: -23, 4: -22, 5: -21, 6: -21,
        7: -20, 8: -20, 9: -19, 10: -18, 11: -18, 12: -17,
        13: -16, 14: -16, 15: -15, 16: -15, 17: -14, 18: -13,
        19: -13, 20: -12, 21: -11, 22: -11, 23: -10, 24: -10,
        25: -9, 26: -8, 27: -8, 28: -7, 29: -6, 30: -6,
        31: -5, 32: -5, 33: -4, 34: -3, 35: -3, 36: -2,
        37: -1, 38: -1
    }

    # Handle low agility values (1-74)
    if agility <= 74:
        if agility in low_agility_map:
            return low_agility_map[agility]
        elif agility <= 65:
            return 0  # 39-65
        elif agility <= 70:
            return 1  # 66-70
        else:
            return 5  # 71-74

    # Handle medium agility values (75-137)
    elif agility <= 137:
        return _calculate_medium_agility_modifier(agility, level)

    # Handle high agility values (138-300)
    elif agility <= 300:
        return _calculate_high_agility_modifier(agility, level)

    # Handle very high agility (300+)
    else:
        return 65 + ((agility - 300) / 21)

    return 0

def _calculate_medium_agility_modifier(agility: int, level: int) -> int:
    """Helper function for agility 75-137 range."""
    # Define level-based modifier tables
    level_modifiers = {
        (75, 75): [9, 23, 33, 39],
        (76, 79): [10, 23, 33, 40],
        (80, 80): [11, 24, 34, 41],
        (81, 85): [12, 25, 35, 42],
        (86, 90): [12, 26, 36, 42],
        (91, 95): [13, 26, 36, 43],
        (96, 99): [14, 27, 37, 44],
        (100, 100): [None, 28, 38, 45],  # Special case for level <= 6
        (101, 105): [15, 29, 39, 45],
        (106, 110): [15, 29, 39, 46],
        (111, 115): [15, 30, 40, 47],
        (116, 119): [15, 31, 41, 47],
        (120, 120): [15, 32, 42, 48],
        (121, 125): [15, 32, 42, 49],
        (126, 135): [15, 32, 42, 50],
        (136, 137): [15, 32, 42, 51],
    }

    # Determine level bracket (0: <=6, 1: <=19, 2: <=39, 3: >=40)
    level_bracket = 0 if level <= 6 else (1 if level <= 19 else (2 if level <= 39 else 3))

    for (min_agi, max_agi), modifiers in level_modifiers.items():
        if min_agi <= agility <= max_agi:
            if agility == 100 and level <= 6:
                return 15  # Special case
            elif agility == 100 and level < 7:
                return 15
            return modifiers[level_bracket]

    return 0

def _calculate_high_agility_modifier(agility: int, level: int) -> int:
    """Helper function for agility 138-300 range."""
    # Define agility breakpoints and their corresponding modifiers
    agility_breakpoints = [
        (139, [21, 34, 44, 51]),
        (140, [22, 35, 45, 52]),
        (145, [23, 36, 46, 53]),
        (150, [23, 37, 47, 53]),
        (155, [24, 37, 47, 54]),
        (159, [25, 38, 48, 55]),
        (160, [26, 39, 49, 56]),
        (165, [26, 40, 50, 56]),
        (170, [27, 40, 50, 57]),
        (175, [28, 41, 51, 58]),
        (179, [28, 42, 52, 58]),
        (180, [29, 43, 53, 59]),
        (185, [30, 43, 53, 60]),
        (190, [31, 44, 54, 61]),
        (195, [31, 45, 55, 61]),
        (199, [32, 45, 55, 62]),
        (219, [33, 46, 56, 63]),
        (239, [34, 47, 57, 64]),
        (300, [35, 48, 58, 65]),
    ]

    # Determine level bracket (0: <=6, 1: <=19, 2: <=39, 3: >=40)
    level_bracket = 0 if level <= 6 else (1 if level <= 19 else (2 if level <= 39 else 3))

    for max_agi, modifiers in agility_breakpoints:
        if agility <= max_agi:
            return modifiers[level_bracket]

    return 0


# Pythonic version with type hints and improved documentation
def get_max_attack(item_atk: int, strength: int, offense: int) -> int:
    """
    Calculate maximum ATK value for a character.

    This function combines item attack with character stats to determine
    the total attack value using the game's formula.

    Args:
        item_atk: Base attack value from equipped items
        strength: Character's strength stat (base + items)
        offense: Character's offense skill level

    Returns:
        Total maximum attack value (floored to integer)

    Formula:
        max_attack = item_attack + ((strength + offense) * 0.9)
    """
    stat_bonus = (strength + offense) * 0.9
    total_attack = item_atk + stat_bonus
    return math.floor(total_attack)
