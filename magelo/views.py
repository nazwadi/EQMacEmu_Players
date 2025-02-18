from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from .models import CharacterPermissions
from .validators import PermissionValidator
from .utils import level_regen
from .utils import calc_hp_regen_cap

import json

from common.utils import valid_game_account_owner

from common.models.characters import Characters
from common.models.characters import CharacterInventory
from common.models.characters import CharacterCurrency
from common.models.guilds import GuildMembers
from common.models.items import Items

from enum import Enum

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

def character_profile(request, character_name):
    character = Characters.objects.filter(name=character_name).first()
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
        'fr': item_stats.stat_bonuses['fr'],
        'cr': item_stats.stat_bonuses['cr'],
        'mr': item_stats.stat_bonuses['mr'],
        'dr': item_stats.stat_bonuses['dr'],
        'pr': item_stats.stat_bonuses['pr'],
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
            'mana': character.mana,
            'hp_regen_cap': hp_regen_cap,
            'hp_regen': hp_regen,
        },
        'magelo': True,
        'guild': guild_info,
        'inventory_items': all_items,
        'currency': character_currency,
        'permissions': permissions,
        'item_stats': item_stats,
    }

    return render(request=request, template_name='magelo/character_profile.html', context=context)


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
