import json
from dataclasses import asdict

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from characters.utils import get_character_keyring

from common.models.characters import Characters, CharacterAlternateAbility, CharacterSkills, CharacterInventory, CharacterCurrency
from common.models.guilds import GuildMembers
from common.models.items import Items
from common.utils import valid_game_account_owner

from .models import CharacterPermissions, WishlistEntry
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
    get_aa_description_by_name,
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
        if character_name:  # Only search if character_name is not empty
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
                    'name': item_data['name'],
                    'slot': slot_id,
                    'rows': calculate_bag_rows(item_data['bag_slots']),
                    'height': calculate_bag_height(item_data['bag_slots']),
                    'button_top': calculate_button_position(item_data['bag_slots']),
                    'slots': [{'number': i} for i in range(item_data['bag_slots'])],
                    'items': bag_contents
                }
                bags_data.append(bag_data)

    # Process bank bags and their contents
    bank_bags_data = []

    # Look for bags in bank slots 2000-2007
    for slot_id in range(2000, 2008):  # Bank slots 2000-2007 where bags can go
        if slot_id in all_items:
            item_data = all_items[slot_id]

            # Check if this item is a bag
            if item_data['bag_slots'] > 0:
                # Calculate where this bank bag's contents start
                bag_index = slot_id - 2000  # 0-7 for slots 2000-2007
                bag_start_slot = 2030 + (bag_index * 10)  # Bank bag content slots start at 2030

                # Collect items that belong in this bank bag
                bag_contents = []
                for i in range(item_data['bag_slots']):
                    check_slot = bag_start_slot + i
                    if check_slot in all_items:
                        bag_item = all_items[check_slot].copy()
                        bag_item['relative_slot'] = i  # Position within bag (0, 1, 2, etc.)
                        bag_contents.append(bag_item)

                # Create bank bag structure
                bank_bag_data = {
                    'name': item_data['name'],
                    'slot': slot_id,
                    'rows': calculate_bag_rows(item_data['bag_slots']),
                    'height': calculate_bag_height(item_data['bag_slots']),
                    'button_top': calculate_button_position(item_data['bag_slots']),
                    'slots': [{'number': i} for i in range(item_data['bag_slots'])],
                    'items': bag_contents
                }
                bank_bags_data.append(bank_bag_data)

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
        'bank_items': {
            'items': all_items,  # Same items dict, but filtered in template
            'bags': bank_bags_data,
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


@require_http_methods(["GET"])
def character_aas(request: HttpRequest, character_name: str) -> HttpResponse:
    """
    Display the character's Alternate Advancement information

   :param request: The HTTP request object
   :param character_name: The name of the EverQuest character
   :raises Http404: If no character exists with the given name
   :return: Rendered 'magelo/alternate_advancement.html' template with character and aas context data
    """
    boxes = []
    display = "block"  # First box visible, rest hidden
    spent_aa = 0

    character = Characters.objects.filter(name=character_name).first()
    if character is None:
        raise Http404("This character does not exist")

    char_aas = CharacterAlternateAbility.objects.filter(id=character.id)
    aa_map = {}

    for character_aa in char_aas:
        parent_id = character_aa.aa_id if character_aa.aa_value <= 1 else character_aa.aa_id - (character_aa.aa_value - 1)
        aa_map[parent_id] = character_aa.aa_value
        # $parent_id = $value["aa_value"] <= 1 ? $value["aa_id"]: $value["aa_id"] - ($value["aa_value"] - 1);
        # $aa_array[$parent_id] = $value["aa_value"];

    aa_tabs = {
        1: 'General',
        2: 'Archetype',
        3: 'Class',
        4: 'PoP Advance',
        5: 'PoP Ability',
    }

    # Create tabs structure for template
    tabs = [
        {'id': key, 'name': name, 'color': 'FFFFFF'}
        for key, name in aa_tabs.items()
    ]

    from django.db import connections
    db_connection = connections['game_database']
    with db_connection.cursor() as cursor:
        for key, value in aa_tabs.items():
            # Create box data
            box_data = {
                'id': key,
                'display': display,
                'aas': []
            }
            display = "none"  # All subsequent boxes hidden

            query = """
                    SELECT skill_id, name, cost, cost_inc, max_level
                    FROM altadv_vars
                    WHERE type = %s
                      AND (classes & 1 << %s) != 0
                      AND eqmacid not in (14, 22, 51, 54, 59, 83, 88, 91, 92, 93, 95, 96, 99, 105, 106, 145)
                    ORDER BY eqmacid
                    """
            cursor.execute(query, [key, character.class_name])
            results = cursor.fetchall()
            for row in results:
                skill_id, name, cost, cost_inc, max_level = row
                # Calculate spent AA for this skill
                current_level = aa_map.get(skill_id, 0)
                for i in range(1, current_level + 1):
                    spent_aa += cost + (cost_inc * (i - 1))

                # Calculate next level cost
                next_level_cost = ""
                if max_level > current_level:
                    next_level_cost = cost + cost_inc * current_level

                # Add AA data
                aa_data = {
                    'COLOR': '#CCCCCC' if next_level_cost == "" else '#FFFFFF',
                    'NAME': name,
                    'CUR': current_level,
                    'MAX': max_level,
                    'COST': next_level_cost
                }
                box_data['aas'].append(aa_data)
            boxes.append(box_data)

    context = {
        'character': character,
        'tabs': tabs,
        'boxes': boxes,
        'POINTS_SPENT': character.aa_points_spent,
        'AA_POINTS': character.aa_points,
    }
    return render(request=request, template_name='magelo/alternate_advancement.html', context=context)


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

@require_http_methods(["GET"])
def magelo_aa_description_api(request: HttpRequest, aa_name: str):
    """

    :param request:
    :return:
    """
    if not aa_name:
        return JsonResponse({'error': 'AA Name is required'}, status=400)

    ability = get_aa_description_by_name(aa_name)
    if ability:
        return JsonResponse(asdict(ability))

    return JsonResponse({'error': f'Ability "{aa_name}" not found'}, status=404)


# ---------------------------------------------------------------------------
# Wishlist views
# ---------------------------------------------------------------------------

@require_http_methods(["GET"])
def wishlist_view(request: HttpRequest, character_name: str) -> HttpResponse:
    """
    Display the gear wishlist for a character.

    Respects the character's wishlist_public permission. Owners always see
    their own wishlist; everyone else is subject to the visibility setting.

    :param request: The HTTP request object
    :param character_name: The EverQuest character name
    :return: Rendered 'magelo/wishlist.html'
    :raises Http404: If the character does not exist
    """
    character = Characters.objects.filter(name=character_name).first()
    if character is None:
        raise Http404("This character does not exist")

    is_owner = valid_game_account_owner(request.user.username, str(character.account_id)) if request.user.is_authenticated else False
    permissions = CharacterPermissions.get_or_create_permissions(character_name)

    if not permissions.wishlist_public and not is_owner:
        return render(request, 'magelo/wishlist.html', {
            'character': character,
            'is_owner': False,
            'wishlist_hidden': True,
            'entries': [],
        })

    entries = WishlistEntry.objects.filter(character_name=character_name)

    return render(request, 'magelo/wishlist.html', {
        'character': character,
        'is_owner': is_owner,
        'wishlist_hidden': False,
        'entries': entries,
        'wishlist_public': permissions.wishlist_public,
    })


@login_required
@require_http_methods(["GET", "POST"])
def wishlist_add(request: HttpRequest) -> HttpResponse:
    """
    Add an item to a character's wishlist.

    GET: Display a form to select the character and optionally add a note.
         Expects ?item_id=<int>&item_name=<str> query params.
    POST: Save the wishlist entry after verifying character ownership.

    :param request: The HTTP request object
    :return: Redirect to wishlist on success, or re-render form on error
    """
    from accounts.models import Account, LoginServerAccounts

    def get_user_characters(username):
        """Return character names/levels for the logged-in user across all their accounts.

        Each queryset is evaluated to a Python list before being passed to the next
        query — these span three separate databases and cannot be combined as subqueries.
        """
        ls_ids = list(LoginServerAccounts.objects.filter(
            ForumName=username
        ).values_list('LoginServerID', flat=True))

        account_ids = list(Account.objects.filter(
            lsaccount_id__in=ls_ids
        ).values_list('id', flat=True))

        return Characters.objects.filter(account_id__in=account_ids).values(
            'name', 'class_name', 'level'
        ).order_by('name')

    if request.method == "GET":
        item_id = request.GET.get('item_id', '')
        item_name = request.GET.get('item_name', '')
        if not item_id or not item_name:
            messages.error(request, "Invalid item.")
            return redirect('items:search')

        user_characters = get_user_characters(request.user.username)
        if not user_characters.exists():
            messages.error(request, "No characters found on your account.")
            return redirect('items:view', item_id=item_id)

        return render(request, 'magelo/wishlist_add.html', {
            'item_id': item_id,
            'item_name': item_name,
            'user_characters': user_characters,
        })

    # POST
    item_id_raw = request.POST.get('item_id', '').strip()
    item_name = request.POST.get('item_name', '').strip()
    character_name = request.POST.get('character_name', '').strip()
    note = request.POST.get('note', '').strip()

    # Validate item_id
    try:
        item_id = int(item_id_raw)
    except (ValueError, TypeError):
        messages.error(request, "Invalid item.")
        return redirect('items:search')

    if not character_name or not item_name:
        messages.error(request, "Missing required fields.")
        return redirect('items:search')

    # Verify character exists and belongs to this user
    character = Characters.objects.filter(name=character_name).first()
    if character is None:
        messages.error(request, "Character not found.")
        return redirect('items:search')

    if not valid_game_account_owner(request.user.username, str(character.account_id)):
        raise PermissionDenied("You don't own that character.")

    # Cap note length to prevent abuse
    note = note[:500]

    WishlistEntry.objects.get_or_create(
        character_name=character_name,
        item_id=item_id,
        defaults={'item_name': item_name, 'note': note},
    )

    messages.success(request, f"Added {item_name} to {character_name}'s wishlist.")
    return redirect('magelo:wishlist', character_name=character_name)


@login_required
@require_http_methods(["POST"])
def wishlist_remove(request: HttpRequest, entry_id: int) -> HttpResponse:
    """
    Remove an entry from a character's wishlist.

    Verifies that the requesting user owns the character before deleting.

    :param request: The HTTP request object
    :param entry_id: Primary key of the WishlistEntry to remove
    :return: Redirect back to the character's wishlist
    :raises Http404: If the entry does not exist
    :raises PermissionDenied: If the user does not own the character
    """
    entry = WishlistEntry.objects.filter(pk=entry_id).first()
    if entry is None:
        raise Http404("Wishlist entry not found.")

    character = Characters.objects.filter(name=entry.character_name).first()
    if character is None or not valid_game_account_owner(request.user.username, str(character.account_id)):
        raise PermissionDenied("You don't have permission to modify this wishlist.")

    item_name = entry.item_name
    character_name = entry.character_name
    entry.delete()

    messages.success(request, f"Removed {item_name} from {character_name}'s wishlist.")
    return redirect('magelo:wishlist', character_name=character_name)


# ---------------------------------------------------------------------------
# Planes of Power flags — each group maps to one or more zone IDs stored
# in the character_zone_flags table.  A character has the flag if any row
# exists for their character id with a matching zoneID.
# ---------------------------------------------------------------------------
POP_FLAG_GROUPS = [
    {'label': 'The Lair of Terris Thule',  'subtitle': 'Plane of Nightmare B', 'zone_ids': [221]},
    {'label': 'Drunder, Fortress of Zek',  'subtitle': 'Plane of Tactics',     'zone_ids': [214]},
    {'label': 'Ruins of Lxanvom',          'subtitle': 'Crypt of Decay',        'zone_ids': [200]},
    {'label': 'Plane of Valor',            'subtitle': '',                      'zone_ids': [208]},
    {'label': 'Plane of Storms',           'subtitle': '',                      'zone_ids': [210]},
    {'label': 'Halls of Honor',            'subtitle': '',                      'zone_ids': [211]},
    {'label': 'Bastion of Thunder',        'subtitle': '',                      'zone_ids': [209]},
    {'label': 'Temple of Marr',            'subtitle': 'Halls of Honor B',      'zone_ids': [220]},
    {'label': 'Plane of Torment',          'subtitle': '',                      'zone_ids': [207]},
    {'label': 'Tower of Solusek Ro',       'subtitle': '',                      'zone_ids': [212]},
    {'label': 'Plane of Fire',             'subtitle': '',                      'zone_ids': [217]},
    {'label': 'Plane of Air',              'subtitle': '',                      'zone_ids': [215]},
    {'label': 'Plane of Earth',            'subtitle': '',                      'zone_ids': [218, 222]},
    {'label': 'Plane of Water',            'subtitle': '',                      'zone_ids': [216]},
    {'label': 'Plane of Time',             'subtitle': '',                      'zone_ids': [223]},
]


@require_http_methods(["GET"])
def character_flags(request: HttpRequest, character_name: str) -> HttpResponse:
    """
    Display Planes of Power progression flags for a character.

    Reads character_zone_flags (game DB) and checks each PoP zone group.
    A group is considered flagged if any matching zoneID row exists for the character.

    :param request: The HTTP request object
    :param character_name: The name of the EverQuest character
    :return: Rendered 'magelo/character_flags.html' template
    :raises Http404: If no character exists with the given name
    """
    from django.db import connections

    character = Characters.objects.filter(name=character_name).first()
    if character is None:
        raise Http404("This character does not exist")

    is_character_owner = valid_game_account_owner(request.user.username, str(character.account_id))
    permissions = get_permissions(request.user, character_name, character.gm, character.anon)

    all_zone_ids = [zid for group in POP_FLAG_GROUPS for zid in group['zone_ids']]
    placeholders = ', '.join(['%s'] * len(all_zone_ids))

    with connections['game_database'].cursor() as cur:
        cur.execute(
            f"SELECT DISTINCT zoneID FROM character_zone_flags WHERE id = %s AND zoneID IN ({placeholders})",
            [character.id] + all_zone_ids,
        )
        flagged_zone_ids = {row[0] for row in cur.fetchall()}

    flag_groups = []
    for group in POP_FLAG_GROUPS:
        flag_groups.append({
            'label': group['label'],
            'subtitle': group['subtitle'],
            'flagged': bool(set(group['zone_ids']) & flagged_zone_ids),
        })

    flags_earned = sum(1 for g in flag_groups if g['flagged'])

    context = {
        'character': character,
        'character_name': character_name,
        'is_character_owner': is_character_owner,
        'permissions': permissions,
        'flag_groups': flag_groups,
        'flags_earned': flags_earned,
        'flags_total': len(flag_groups),
    }
    return render(request=request, template_name='magelo/character_flags.html', context=context)