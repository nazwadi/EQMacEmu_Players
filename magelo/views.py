import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from characters.utils import get_character_keyring

from common.models.characters import Characters, CharacterSkills, CharacterInventory, CharacterCurrency
from common.models.guilds import GuildMembers
from common.models.items import Items
from common.utils import valid_game_account_owner

from .models import CharacterPermissions
from .utils import (
    ItemStats,
    calc_hp_regen_cap,
    calc_max_mana,
    cr_by_class,
    cr_by_race,
    dr_by_class,
    dr_by_race,
    fr_by_class,
    fr_by_race,
    get_max_ac,
    get_max_attack,
    get_max_hp,
    get_permissions,
    level_regen,
    mr_by_class,
    mr_by_race,
    pr_by_class,
    pr_by_race,
    rate_limit_by_user,
)
from .validators import PermissionValidator

@require_http_methods(["GET", "POST"])
def search(request: HttpRequest) -> HttpResponse:
    """
    Handle EverQuest character profile searches by name.

    Supports GET to display the search form and POST to return up to 50 matching characters using case-insensitive
    partial name matching.

    :param request: The HTTP request object
    :return: Rendered 'magelo/search.html' template with search form and
             results (if POST with matches)

    Context variables:
        - search_results: QuerySet of Characters (POST only, limited to 50 results)

    Form fields (POST):
        - character_name: Required text field for character name search

    Notes:
        - Public view with no authentication required
        - Results limited to 50 for performance
    """
    context = {}

    if request.method == "POST":
        character_name = request.POST.get("character_name")
        if character_name: # Only search if character_name is not empty
            search_results = Characters.objects.filter(name__icontains=character_name)[:50]
            context["search_results"] = search_results

    return render(request=request, template_name="magelo/search.html", context=context)

@require_http_methods(["GET"])
def character_profile(request: HttpRequest, character_name: str) -> HttpResponse:
    """
     Display comprehensive EverQuest character profile with stats, inventory, and equipment.

    Shows character's base stats, equipment bonuses, calculated totals (HP, mana, AC, attack),
    guild information, inventory items, and currency. Includes ownership verification and
    privacy permission checks based on character's GM level, anonymity settings, and stored
    character permissions.

    Calculates derived stats including:
    - Total stats (base + equipment bonuses with caps)
    - AC from agility, level, defense skill, class, and equipment
    - Attack from equipment, strength, and offense skill
    - HP/mana totals with equipment bonuses
    - HP regeneration with racial bonuses (Troll/Iksar)
    - Resistance totals (fire, cold, magic, disease, poison) by race/class/equipment
    - Special effects like haste and flowing thought from worn items

    :param request: The HTTP request object
    :param character_name: The name of the EverQuest character to display
    :return: Rendered 'magelo/character_profile.html' template with character data
    :raises Http404: If character doesn't exist or required skills (defense/offense) missing

    Context variables:
        - character: Dict with character info, base/total stats, and calculated values
        - is_character_owner: Boolean indicating if current user owns this character's account
        - guild: Dict with guild name and member rank (empty if not in guild)
        - inventory_items: Dict of items by slot ID (0-21: equipment, 22+: bags/bank/inventory)
        - currency: CharacterCurrency object with character's money
        - permissions: Dict of viewing permissions (inventory, bags, bank, coin_inventory, coin_bank)
        - item_stats: ItemStats object tracking equipment bonuses, totals, and special effects
        - magelo: Boolean flag for template identification

    Permission system:
        - GM characters (gm > 0) and anonymous characters (anon > 0) use stored permissions
        - Normal characters use their CharacterPermissions settings
        - Character ownership is verified via game account matching

    Notes:
        - Only equipment slots (0-21) contribute to stat calculations
        - ItemStats applies stat caps (255 for base stats, 300 for resists, etc.)
        - Special worn effects like haste (998) and flowing thought are tracked separately
    """
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
                'is_bag': item.bag_slots > 0,
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

    def calculate_bag_rows(bag_slots):
        """Calculate number of rows for bag display"""
        if bag_slots <= 4:
            return 1
        elif bag_slots <= 8:
            return 2
        elif bag_slots <= 12:
            return 3
        else:
            return 4

    def calculate_bag_height(bag_slots):
        """Calculate bag height based on number of slots"""
        rows = calculate_bag_rows(bag_slots)
        base_height = 60  # Base height for title, padding, etc.
        row_height = 43  # Height per row of slots
        button_height = 36  # Height of the button itself
        button_margin = 65  # Margin between last slot row and button
        return base_height + (rows * row_height) + button_margin + button_height

    def calculate_button_position(bag_slots):
        """Calculate button top position based on number of slots"""
        rows = calculate_bag_rows(bag_slots)
        base_top = 20 + 60  # Starting position of first slot row
        row_height = 43  # Height per row
        button_margin = 25  # Space between last slot and button

        return base_top + (rows * row_height) + button_margin

    # Process bags and their contents
    bags_data = []

    # Look for bags in inventory slots 22-29
    for slot_id in range(22, 30):  # Slots 22-29 are general inventory where bags go
        if slot_id in all_items:
            item_data = all_items[slot_id]

            # Check if this item is a bag
            if item_data['bag_slots'] > 0:
                # Calculate where this bag's contents start
                bag_index = slot_id - 22  # 0-7 for slots 22-29
                bag_start_slot = 250 + (bag_index * 10)  # EQ bag content slots

                # Collect items that belong in this bag
                bag_contents = []
                for i in range(item_data['bag_slots']):
                    check_slot = bag_start_slot + i
                    if check_slot in all_items:
                        bag_item = all_items[check_slot].copy()
                        bag_item['relative_slot'] = i  # Position within bag (0, 1, 2, etc.)
                        bag_contents.append(bag_item)

                # Create bag structure
                bag_data = {
                    'slot': slot_id,
                    'rows': calculate_bag_rows(item_data['bag_slots']),
                    'height': calculate_bag_height(item_data['bag_slots']),
                    'button_top': calculate_button_position(item_data['bag_slots']),
                    'slots': [{'number': i} for i in range(item_data['bag_slots'])],
                    'items': bag_contents
                }
                bags_data.append(bag_data)

    # Calculate total stats including items
    total_stats = {
        'str': character.str + item_stats.stat_bonuses['str'],
        'sta': character.sta + item_stats.stat_bonuses['sta'],
        'agi': character.agi + item_stats.stat_bonuses['agi'],
        'dex': character.dex + item_stats.stat_bonuses['dex'],
        'int': character.int_stat + item_stats.stat_bonuses['int'],
        'wis': character.wis + item_stats.stat_bonuses['wis'],
        'cha': character.cha + item_stats.stat_bonuses['cha'],
        'fr': fr_by_race(character.race) + fr_by_class(character.class_name, character.level) + item_stats.stat_bonuses[
            'fr'],
        'cr': cr_by_race(character.race) + cr_by_class(character.class_name, character.level) + item_stats.stat_bonuses[
            'cr'],
        'mr': mr_by_race(character.race) + mr_by_class(character.class_name, character.level) + item_stats.stat_bonuses[
            'mr'],
        'dr': dr_by_race(character.race) + dr_by_class(character.class_name, character.level) + item_stats.stat_bonuses[
            'dr'],
        'pr': pr_by_race(character.race) + pr_by_class(character.class_name, character.level) + item_stats.stat_bonuses[
            'pr'],
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
    if defense is None:
        defense_value = 0
    else:
        defense_value = defense.value
    ac = get_max_ac(character.agi, character.level, defense_value, character.class_name, item_stats.total_ac,
                    character.race)
    if offense is None:
        offense_value = 0
    else:
        offense_value = offense.value
    atk = get_max_attack(item_stats.atk, character.str + item_stats.stat_bonuses['str'], offense_value)

    total_int = character.int_stat + item_stats.stat_bonuses['int']
    total_wis = character.wis + item_stats.stat_bonuses['wis']
    max_mana, current_mana = calc_max_mana(character.class_name, total_int, total_wis, character.level,
                                           item_stats.total_mana, 0, character.mana)

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
            'max_hp': get_max_hp(level=character.level,
                                 character_class=character.class_name,
                                 stamina=character.sta + item_stats.stat_bonuses['sta'],
                                 item_hp_bonus=item_stats.total_hp,
                                 stat_cap=255),
            'cur_hp': character.cur_hp,
            'max_mana': max_mana,
            'current_mana': current_mana,
            'hp_regen_cap': hp_regen_cap,
            'hp_regen': hp_regen,
            'ac': ac,
            'atk': atk,
        },
        'magelo': True,  # just a variable to let the templates know this is the magelo page
        'guild': guild_info,
        'inventory_items': {
            'items': all_items,
            'bags': bags_data,
        },
        'currency': character_currency,
        'permissions': permissions,
        'item_stats': item_stats,
    }

    return render(request=request, template_name='magelo/character_profile.html', context=context)

@require_http_methods(["GET"])
def character_keys(request: HttpRequest, character_name: str) -> HttpResponse:
    """
    Display all in-game keys acquired by an EverQuest character.

    This public view shows the keyring for a specific EverQuest character,
    displaying all keys (items) the character has collected in-game. Keys are
    sorted alphabetically by item name.

   :param request: The HTTP request object
   :param character_name: The name of the EverQuest character
   :return: Rendered 'magelo/character_keys.html' template with character
            and keys context data
   :raises Http404: If no character exists with the given name

   Context variables:
       - character: The Characters model instance
       - keys: Tuple of (item_id, item_name) pairs from character's keyring

   Note:
       This is a public view with no authentication or authorization required.
    """
    character = Characters.objects.filter(name=character_name).first()
    if character is None:
        raise Http404("This character does not exist")
    character_keyring = get_character_keyring(character_id=character.id)
    context = {
        'character': character,
        'keys': character_keyring
    }
    return render(request=request, template_name='magelo/character_keys.html', context=context)

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
