from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404

# Create your views here.
from common.models.characters import Characters
from common.models.characters import CharacterInventory
from common.models.characters import CharacterCurrency
from common.models.guilds import GuildMembers
from common.models.items import Items

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

    def add_item(self, item):
        """Add item and accumulate its stats"""
        self.items.append(item)
        self.total_weight += item.weight
        self.total_ac += item.ac
        self.total_hp += item.hp
        self.total_mana += item.mana

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


def get_permissions(gm_level, anon_level):
    """Calculate viewing permissions based on GM and anonymity levels"""
    permissions = {
        'inventory': False,
        'bags': False,
        'bank': False,
        'coininventory': False,
        'coinbank': False
    }

    # Only show inventory if character isn't anonymous and isn't a GM
    if anon_level == 0 and gm_level == 0:
        permissions['inventory'] = True
        permissions['bags'] = True
        permissions['bank'] = True
        permissions['coininventory'] = True
        permissions['coinbank'] = True

    return permissions


@staff_member_required
@login_required
def character_profile(request, character_name):
    # Get character or 404
    character = Characters.objects.filter(name=character_name).first()
    character_currency = CharacterCurrency.objects.filter(id=character.id).first()

    # Get permissions
    permissions = get_permissions(character.gm, character.anon)

    # Block view if user doesn't have permission
    if not permissions['inventory'] and not request.user.is_staff:
        raise Http404("You don't have permission to view this inventory")

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
                'stackable': item.stackable
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

    # Build context
    context = {
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
        },
        'magelo': True,
        'guild': guild_info,
        'inventory_items': all_items,
        'currency': character_currency,
        'permissions': permissions,
        'item_stats': item_stats,
    }

    return render(request, 'magelo/character_profile.html', context)
