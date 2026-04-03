import logging
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connections, transaction
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404

from items.models import BISEntry, BISRevision, ItemExpansion, SLOT_ORDER, ITEM_EXPANSION_CHOICES
from items.utils import get_class_bitmask
from items.utils import get_race_bitmask
from items.utils import build_stat_query
from items.utils import get_item_effect
from common.constants import PLAYER_CLASSES
from common.constants import PLAYER_RACES
from common.constants import EQUIPMENT_SLOTS
from common.constants import ITEM_TYPES
from common.constants import ITEM_STATS
from common.constants import CONTAINER_TYPES
from common.models.items import DiscoveredItems
from common.models.items import Items
from quests.models import Quests
from collections import namedtuple

logger = logging.getLogger(__name__)

def search(request):
    """
    Search for an item by name at url https://url.tld/items/search

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":
        return render(request=request,
                      context={
                          "IS_SEARCH": True,
                          "EQUIPMENT_SLOTS": EQUIPMENT_SLOTS,
                          "PLAYER_CLASSES": PLAYER_CLASSES,
                          "PLAYER_RACES": PLAYER_RACES,
                          "ITEM_TYPES": ITEM_TYPES,
                          "CONTAINER_TYPES": CONTAINER_TYPES,
                          "ITEM_STATS": ITEM_STATS,
                          "ITEM_EXPANSION_CHOICES": ITEM_EXPANSION_CHOICES,
                      },
                      template_name="items/search_item.html")

    if request.method == "POST":
        item_name = request.POST.get("item_name")
        item_slot = request.POST.get("item_slot", "0")
        item_type = request.POST.get("item_type", "-1")
        resists_type = request.POST.get("resists_type", "Resist")
        resists_operator = request.POST.get("resists_operator", ">")
        resists_value = request.POST.get("resists_value", "0")
        stat1 = request.POST.get("stat1", "stat1")
        stat1_operator = request.POST.get("stat1_operator", ">")
        stat1_value = request.POST.get("stat1_value", "0")
        stat2 = request.POST.get("stat2", "stat2")
        stat2_operator = request.POST.get("stat2_operator", ">")
        stat2_value = request.POST.get("stat2_value", "0")
        item_effect = request.POST.get("item_effect")
        item_has_proc = request.POST.get("item_has_proc")
        item_has_click = request.POST.get("item_has_click")
        item_has_focus = request.POST.get("item_has_focus")
        item_has_worn = request.POST.get("item_has_worn")
        player_class = request.POST.get("player_class", "0")
        player_race = request.POST.get("player_race", "0")
        container_select = request.POST.get("container_select", "Container")
        container_slots = request.POST.get("container_slots", "0")
        container_wr = request.POST.get("container_wr", "0")
        item_expansion = request.POST.get("item_expansion", "")
        query_limit = request.POST.get("query_limit", "50")

        params_list = []
        clause = ""

        # Begin building query
        query = "SELECT * FROM items"
        if item_effect:
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += """ LEFT JOIN spells_new AS proc_s ON proceffect = proc_s.id
                                        LEFT JOIN spells_new AS worn_s ON worneffect = worn_s.id
                                        LEFT JOIN spells_new AS focus_s ON focuseffect = focus_s.id
                                        LEFT JOIN spells_new AS click_s ON clickeffect = click_s.id
                                        WHERE (proc_s.name LIKE %s
                                            OR worn_s.name LIKE %s
                                            OR focus_s.name LIKE %s
                                            OR click_s.name LIKE %s)"""
            params_list.append(item_effect)
            params_list.append(item_effect)
            params_list.append(item_effect)
            params_list.append(item_effect)

        if item_name:
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} (LOWER(items.Name) LIKE %s)"
            params_list.append(f"%{item_name.lower()}%")

        try:
            player_class = int(player_class)
        except ValueError:
            messages.error(request, "Invalid player class.  Valid options are between 1 and 15.")
            return redirect("/items/search")
        if player_class != 0:  # zero means "any" class so no need to filter
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} (((classes & %s) = %s) OR (classes = '32767'))"
            player_class = get_class_bitmask(player_class)
            # yes, twice - there are two parameters above
            params_list.append(player_class)
            params_list.append(player_class)

        try:
            player_race = int(player_race)
        except ValueError:
            messages.error(request, "Invalid player race.")
            return redirect("/items/search")
        if player_race != 0:  # zero means "any" race so no need to filter
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} (((races & %s) = %s) OR (races = '16384'))"
            player_race = get_race_bitmask(player_race)
            # yes, twice - there are two parameters above
            params_list.append(player_race)
            params_list.append(player_race)

        try:
            item_slot = int(item_slot)
        except ValueError:
            messages.error(request, "Invalid item slot.")
            return redirect("/items/search")
        if item_slot != 0:  # zero means "any" slot so no need to filter
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} ((slots & %s) = %s)"
            # yes, twice - there are two parameters above
            params_list.append(item_slot)
            params_list.append(item_slot)

        try:
            item_type = int(item_type)
        except ValueError:
            messages.error(request, "Invalid item type.")
            return redirect("/items/search")
        if item_type != -1:
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} itemtype = %s"
            params_list.append(item_type)

        try:
            resists_value = int(resists_value)
        except ValueError:
            messages.error(request, "Invalid resist value. Must be an integer.")
            return redirect("/items/search")

        if resists_type != 'Resist':  # if no resist type was set, no need to filter
            allowed_resist_types = {'mr': 'mr', 'fr': 'fr', 'cr': 'cr', 'dr': 'dr', 'pr': 'pr'}
            if resists_type not in allowed_resist_types.keys():
                messages.error(request, "Invalid resist type.")
                return redirect("/items/search")
            else:
                resists_type = allowed_resist_types[resists_type]  # just an extra precaution
            allowed_resists_operators = {'>': '>', '>=': '>=', '=': '=', '<=': '<=', '<': '<'}
            if resists_operator not in allowed_resists_operators.keys():
                messages.error(request, "Invalid resist operator.")
                return redirect("/items/search")
            else:
                resists_operator = allowed_resists_operators[resists_operator]  # just an extra precaution
            if 0 <= resists_value <= 300:
                clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
                query += f" {clause} items.{resists_type} {resists_operator} %s"
                params_list.append(resists_value)
            else:
                messages.error(request, f"Invalid resist value, '{resists_value}'.  Must be between 0 and 300.")
                return redirect("/items/search")

        if stat1 != "stat1":  # if the field was not left blank
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            partial_query, error_messages = build_stat_query(clause, stat1, stat1_operator)
            if len(error_messages) == 0:
                query += partial_query
                params_list.append(stat1_value)
            else:
                error_message = "<br />".join(error_messages)
                messages.error(request, error_message)
                return redirect("/items/search")

        if stat2 != "stat2":  # if the field was not left blank
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            partial_query, error_messages = build_stat_query(clause, stat2, stat2_operator)
            if len(error_messages) == 0:
                query += partial_query
                params_list.append(stat2_value)
            else:
                error_message = "<br />".join(error_messages)
                messages.error(request, error_message)
                return redirect("/items/search")

        if container_select != "Container":
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} bagtype = %s"
            params_list.append(container_select)
        if container_slots != '0':
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} bagslots >= %s"
            params_list.append(container_slots)
        if container_wr != '0':
            clause = "AND" if clause == "WHERE" or clause == "AND" else "WHERE"
            query += f" {clause} bagwr >= %s"
            params_list.append(container_wr)

        if item_has_proc:
            query += " AND (proceffect > 0 and proceffect < 4679)"
        if item_has_click:
            query += " AND (clickeffect > 0 and clickeffect < 4679)"
        if item_has_focus:
            query += " AND (focuseffect > 0 and focuseffect < 4679) AND bagtype = 0"
        if item_has_worn:
            query += " AND (worneffect > 0 and worneffect < 4679)"

        if item_expansion != "":
            try:
                item_expansion = int(item_expansion)
            except ValueError:
                messages.error(request, "Invalid expansion value.")
                return redirect("/items/search")

            from django.core.cache import cache
            from django.db import connection as webdb_connection
            cache_key = f'item_search:expansion_ids:{item_expansion}'
            ids_str = cache.get(cache_key)
            if ids_str is None:
                with webdb_connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT item_id FROM items_itemexpansion WHERE expansion <= %s",
                        [item_expansion]
                    )
                    rows = cursor.fetchall()
                ids_str = ','.join(str(row[0]) for row in rows) if rows else ''
                if ids_str:
                    cache.set(cache_key, ids_str, timeout=60 * 60 * 24 * 7)

            if not ids_str:
                messages.info(request, "No items found for the selected expansion or earlier. "
                              "Try running compute_item_expansions to populate expansion data.")
                return render(request=request,
                              template_name="items/search_item.html",
                              context={
                                  "IS_SEARCH": True,
                                  "search_results": [],
                                  "EQUIPMENT_SLOTS": EQUIPMENT_SLOTS,
                                  "ITEM_TYPES": ITEM_TYPES,
                                  "CONTAINER_TYPES": CONTAINER_TYPES,
                                  "ITEM_STATS": ITEM_STATS,
                                  "PLAYER_CLASSES": PLAYER_CLASSES,
                                  "PLAYER_RACES": PLAYER_RACES,
                                  "ITEM_EXPANSION_CHOICES": ITEM_EXPANSION_CHOICES,
                                  "level_range": range(100),
                              })
            clause = "AND" if clause in ("WHERE", "AND") else "WHERE"
            query += f" {clause} items.id IN ({ids_str})"

        try:
            query_limit = int(query_limit)
        except ValueError:
            return redirect("/items/search")
        if query_limit < 0:
            query_limit = 0
        elif query_limit > 200:  # yes, this is an arbitrary limit on search results
            query_limit = 200
        query += " LIMIT %s"
        params_list.append(query_limit)

        search_results = Items.objects.raw(query, params_list)

        if len(search_results) == 0:
            messages.info(request, "No search results found.")

        return render(request=request,
                      template_name="items/search_item.html",
                      context={
                          "IS_SEARCH": True,
                          "search_results": search_results,
                          "EQUIPMENT_SLOTS": EQUIPMENT_SLOTS,
                          "ITEM_TYPES": ITEM_TYPES,
                          "CONTAINER_TYPES": CONTAINER_TYPES,
                          "ITEM_STATS": ITEM_STATS,
                          "PLAYER_CLASSES": PLAYER_CLASSES,
                          "PLAYER_RACES": PLAYER_RACES,
                          "ITEM_EXPANSION_CHOICES": ITEM_EXPANSION_CHOICES,
                          "level_range": range(100)})


def discovered_items(request):
    """
    Defines view for https://url.tld/items/discovered

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":
        recent_discoveries = DiscoveredItems.objects.all().order_by('-discovered_date')[:100]
        return render(request=request,
                      template_name="items/discovered_items.html",
                      context={"recent_discoveries": recent_discoveries})

    if request.method == "POST":
        item_name = request.POST.get("item_name")
        char_name = request.POST.get("char_name")
        query_limit = request.POST.get("query_limit")
        try:
            query_limit = int(query_limit)
        except ValueError:
            return redirect("/items/discovered")
        if query_limit < 0:
            query_limit = 0
        elif query_limit > 200:  # yes, this is an arbitrary limit on search results
            query_limit = 200

        recent_discoveries = None
        discovered_items_list = None
        if char_name and item_name:
            item_list = Items.objects.filter(Name__icontains=item_name)[:query_limit]
            item_id_list = [item.id for item in item_list]
            discovered_items_list = DiscoveredItems.objects.filter(item_id__in=item_id_list).filter(
                char_name__icontains=char_name).order_by(
                '-discovered_date')[:query_limit]
        elif item_name:
            item_list = Items.objects.filter(Name__icontains=item_name)[:query_limit]
            item_id_list = [item.id for item in item_list]
            discovered_items_list = DiscoveredItems.objects.filter(item_id__in=item_id_list).order_by(
                '-discovered_date')[:query_limit]
        elif char_name:
            discovered_items_list = DiscoveredItems.objects.filter(char_name__icontains=char_name).order_by(
                '-discovered_date')[:query_limit]
        else:
            recent_discoveries = DiscoveredItems.objects.all().order_by('-discovered_date')[:100]

        return render(request=request,
                      template_name="items/discovered_items.html",
                      context={"discovered_items_list": discovered_items_list,
                               "recent_discoveries": recent_discoveries})


def view_item(request, item_id):
    """
    Defines view for https://url.tld/items/view/<int:pk>

    :param request: Http request
    :param item_id: an Item id field unique identifier
    :return: Http response
    """
    item = Items.objects.filter(id=item_id).first()
    if item is None:
        raise Http404(f"The Item you requested, {item_id}, does not exist.")

    effect_name, effect_id, focus_effect_name = get_item_effect(item)

    cursor = connections['game_database'].cursor()
    cursor.execute("""SELECT tradeskill_recipe.id, tradeskill_recipe.name, tradeskill_recipe.tradeskill, 
                             tradeskill_recipe.trivial, tradeskill_recipe_entries.successcount
                      FROM tradeskill_recipe JOIN tradeskill_recipe_entries
                      ON tradeskill_recipe.id=tradeskill_recipe_entries.recipe_id
                      WHERE tradeskill_recipe_entries.item_id=%s
                        AND tradeskill_recipe_entries.successcount > 0
                      ORDER BY tradeskill_recipe.id""", [item_id])
    created_by_these_tradeskill_recipes_result = cursor.fetchall()
    created_by_these_tradeskill_recipes = dict()
    TradeskillRecipeCreatedByTuple = namedtuple('TradeskillRecipeCreatedByTuple', ['recipe_id',
                                                                                   'recipe_name', 'tradeskill',
                                                                                   'trivial', 'success_count'])
    for result in created_by_these_tradeskill_recipes_result:
        tr_tuple = TradeskillRecipeCreatedByTuple(*result)
        if tr_tuple.tradeskill not in created_by_these_tradeskill_recipes:
            created_by_these_tradeskill_recipes[tr_tuple.tradeskill] = list()
        created_by_these_tradeskill_recipes[tr_tuple.tradeskill].append(tr_tuple)

    cursor.execute("""SELECT tradeskill_recipe.id, tradeskill_recipe.name, tradeskill_recipe.tradeskill,
                           tradeskill_recipe.trivial
                      FROM tradeskill_recipe, tradeskill_recipe_entries
                      WHERE tradeskill_recipe.id=tradeskill_recipe_entries.recipe_id
                        AND tradeskill_recipe_entries.item_id=%s
                        AND tradeskill_recipe_entries.componentcount > 0
                      ORDER BY tradeskill_recipe.tradeskill""", [item_id])
    used_in_these_tradeskill_recipes_result = cursor.fetchall()
    used_in_these_tradeskill_recipes = dict()
    TradeskillRecipeUsedInTuple = namedtuple('TradeskillRecipeUsedInTuple',
                                             ['recipe_id', 'recipe_name', 'tradeskill', 'trivial'])
    for result in used_in_these_tradeskill_recipes_result:
        tr_tuple = TradeskillRecipeUsedInTuple(*result)
        if tr_tuple.tradeskill not in used_in_these_tradeskill_recipes:
            used_in_these_tradeskill_recipes[tr_tuple.tradeskill] = list()
        used_in_these_tradeskill_recipes[tr_tuple.tradeskill].append(tr_tuple)
    # Very Heavy Query
    cursor.execute("""SELECT DISTINCT npc_types.id, npc_types.name, spawn2.zone, zone.long_name,
                             loottable_entries.multiplier, loottable_entries.probability, lootdrop_entries.chance
                      FROM npc_types, spawn2, spawnentry, loottable_entries, lootdrop_entries, zone
                      WHERE npc_types.id=spawnentry.npcID
                            AND spawnentry.spawngroupID=spawn2.spawngroupID
                            AND npc_types.loottable_id=loottable_entries.loottable_id
                            AND loottable_entries.lootdrop_id=lootdrop_entries.lootdrop_id
                            AND lootdrop_entries.item_id=%s
                            AND zone.short_name=spawn2.zone""", [item_id])
    drops_from_result = cursor.fetchall()
    drops_from = dict()
    DropsFromTuple = namedtuple("DropsFromTuple", ["npc_id", "npc_name", "z_short_name", "z_long_name",
                                                   "lte_multiplier", "modified_drop_chance"])
    for npc_id, npc_name, z_short_name, z_long_name, lte_multiplier, lte_probability, lde_chance in drops_from_result:
        if z_short_name not in drops_from:
            drops_from[z_short_name] = list()
        drops_from[z_short_name].append(DropsFromTuple(npc_id=npc_id, npc_name=npc_name, z_short_name=z_short_name,
                                                       z_long_name=z_long_name, lte_multiplier=lte_multiplier,
                                                       modified_drop_chance=(lte_probability * lde_chance) / 100))

    # Run a quick sanity check before attempting a more compute-intensive query
    is_sold = cursor.execute("""SELECT item FROM merchantlist WHERE item=%s LIMIT 1""", [item_id])
    sold_by = None
    if is_sold:
        # If it exists, run the more intensive query
        cursor.execute("""SELECT npc_types.id, npc_types.name, spawn2.zone, zone.long_name, npc_types.class
                                            FROM npc_types, merchantlist, spawn2, zone, spawnentry
                                            WHERE merchantlist.item=%s
                                                AND npc_types.id=spawnentry.npcID
                                                AND spawnentry.spawngroupID=spawn2.spawngroupID
                                                AND merchantlist.merchantid=npc_types.merchant_id
                                                AND zone.short_name=spawn2.zone""", [[item_id]])
        sold_by_results = cursor.fetchall()
        SoldByTuple = namedtuple('SoldByTuple', ['npc_id', 'npc_name', 'z_short_name', 'z_long_name', 'npc_class'])
        sold_by = dict()
        for result in sold_by_results:
            result_tuple = SoldByTuple(*result)
            if result_tuple.z_short_name not in sold_by:
                sold_by[result_tuple.z_short_name] = list()
            sold_by[result_tuple.z_short_name].append(result_tuple)

    cursor.execute("""SELECT zone.short_name, zone.long_name, ground_spawns.max_x, ground_spawns.max_y, 
                        ground_spawns.max_z, ground_spawns.min_x, ground_spawns.min_y
                      FROM ground_spawns, zone
                      WHERE item=%s
                        AND ground_spawns.zoneid=zone.zoneidnumber""", [[item_id]])
    ground_spawns_results = cursor.fetchall()
    GroundSpawnsTuple = namedtuple('GroundSpawnsTuple', ['z_short_name', 'z_long_name', 'max_x',
                                                         'max_y', 'max_z', 'min_x', 'min_y'])
    ground_spawns = dict()
    for result in ground_spawns_results:
        result_tuple = GroundSpawnsTuple(*result)
        if result_tuple.z_short_name not in ground_spawns:
            ground_spawns[result_tuple.z_short_name] = list()
        ground_spawns[result_tuple.z_short_name].append(result_tuple)

    cursor.execute("""SELECT zone.short_name, zone.long_name, forage.id, forage.zoneid, forage.itemid, forage.level, forage.chance
                      FROM forage, zone
                      WHERE zone.zoneidnumber = forage.zoneid
                          AND itemid=%s""", [[item_id]])
    forage_results = cursor.fetchall()
    ForageTuple = namedtuple('ForageTuple', ['z_short_name', 'z_long_name', 'id', 'zone_id',
                                             'item_id', 'level', 'chance'])
    forage = dict()
    for result in forage_results:
        forage_tuple = ForageTuple(*result)
        if forage_tuple.z_short_name not in forage:
            forage[forage_tuple.z_short_name] = list()
        forage[forage_tuple.z_short_name].append(forage_tuple)

    obj_path = f"/static/models/equip/{item.idfile.lower()}{'.glb'}"

    related_quests = Quests.objects.filter(quest_items__item_id=item_id, status='published')

    return render(request=request,
                  template_name="items/view_item.html",
                  context={
                      "item": item,
                      "obj_path": obj_path,
                      "drops_from": drops_from,
                      "effect_name": effect_name,
                      "focus_effect_name": focus_effect_name,
                      "og_description": item.generate_og_description(effect_name, focus_effect_name),
                      "created_by_these_tradeskill_recipes": created_by_these_tradeskill_recipes,
                      "used_in_these_tradeskill_recipes": used_in_these_tradeskill_recipes,
                      "sold_by": sold_by,
                      "forage": forage,
                      "ground_spawns": ground_spawns,
                      "related_quests": related_quests,
                  })

@require_http_methods(["GET"])
def item_detail_api(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Useful for grabbing item stats when users hover their mouse over an item link

    :param request: The HTTP request object.
    :param item_id: An Item ID field unique identifier.
    :return: An HTTP response rendering the item stats template.
    """
    try:
        item = Items.objects.get(id=item_id)
        effect_name, effect_id, focus_effect_name = get_item_effect(item)
        response = render(
            request=request,
            template_name="items/item_stats_template.html",
            context={
                "effect_name": effect_name,
                "focus_effect_name": focus_effect_name,
                "item": item,
            }
        )
        return response

    except Items.DoesNotExist:
        logger.error(f"ERROR: Item {item_id} does not exist")
        return HttpResponse(f"Item {item_id} not found", status=404)
    except Exception as e:
        logger.error(f"ERROR in item_detail_api for item {item_id}: {e}", exc_info=True)
        return HttpResponse("Internal server error", status=500)


_BIS_EXPANSION_ORDER = [
    'vanilla-pre-planar', 'vanilla-planar', 'kunark',
    'velious-group', 'velious-raid',
    'luclin-group', 'luclin-raid',
    'pop-group', 'pop-raid',
]

# Maps class_id → first expansion that class was available.
# Classes not listed default to the very first expansion.
_BIS_CLASS_MIN_EXPANSION = {
    15: 'luclin-group',  # Beastlord introduced in Luclin
}

# Slots that only apply to specific classes (class_id set).
# Slots absent from this dict are shown for every class.
_BIS_SLOT_CLASS_RESTRICTIONS = {
    'Instrument':       frozenset([8]),                         # Bard only
    'Primary H2H':      frozenset([1, 7, 15]),                  # Warrior, Monk, Beastlord
    'Primary 2HS':      frozenset([1, 3, 4, 5]),                # Warrior, Paladin, Ranger, SK
    'Primary 1HS':      frozenset([1, 3, 4, 5, 8, 9, 15]),     # Melee + Bard + Rogue + Beastlord
    'Primary 1HB':      frozenset([1, 2, 3, 4, 5, 6, 7, 8,
                                   10, 11, 12, 13, 14, 15]),   # All except Rogue
    'Primary 2HB':      frozenset([1, 2, 3, 4, 5, 6, 10]),     # Heavy melee + Priests
    'Primary Piercing': frozenset([1, 3, 4, 5, 8, 9]),         # Melee + Bard + Rogue
}

_BIS_CLASS_ARCHETYPES = [
    ('Tanks',   [1, 3, 5]),           # Warrior, Paladin, Shadowknight
    ('Priests', [2, 6, 10]),          # Cleric, Druid, Shaman
    ('Melee',   [7, 9, 4, 8, 15]),    # Monk, Rogue, Ranger, Bard, Beastlord
    ('Casters', [11, 12, 13, 14]),    # Necromancer, Wizard, Magician, Enchanter
]


def _group_bis_entries(entries):
    """
    Group a flat list of BISEntry objects into an ordered dict:
        { expansion_slug: { slot_name: [BISEntry, ...] } }
    Slots within each expansion are sorted by the canonical SLOT_ORDER.
    """
    _slot_rank = {s: i for i, s in enumerate(SLOT_ORDER)}

    result = {slug: {} for slug in _BIS_EXPANSION_ORDER}
    for entry in entries:
        slot_map = result.setdefault(entry.expansion, {})
        slot_map.setdefault(entry.slot, []).append(entry)

    # Sort slots within each expansion by canonical order
    for slug in result:
        result[slug] = dict(
            sorted(result[slug].items(), key=lambda kv: _slot_rank.get(kv[0], 999))
        )
    return result


def best_in_slot(request: HttpRequest, class_id: int = None) -> HttpResponse:
    """
    Defines view for https://url.tld/items/bis/<int:class_id>

    :param request: The HTTP request object.
    :param class_id: a unique identifier for a playable class, usually between 1 - 16
    :return: an HTTP response rendering the best in slot template
    """
    class_archetypes = [
        (label, [(cid, PLAYER_CLASSES[cid]) for cid in ids if cid in PLAYER_CLASSES])
        for label, ids in _BIS_CLASS_ARCHETYPES
    ]

    if class_id is None or not 0 < class_id < 16:
        return render(request=request,
                      template_name="items/best_in_slot.html",
                      context={
                          "player_classes": PLAYER_CLASSES,
                          "class_archetypes": class_archetypes,
                          "class_id": None,
                      })

    selected_class = PLAYER_CLASSES.get(class_id, 0)
    min_exp = _BIS_CLASS_MIN_EXPANSION.get(class_id, 'vanilla-pre-planar')
    locked_expansions = set(_BIS_EXPANSION_ORDER[:_BIS_EXPANSION_ORDER.index(min_exp)])

    entries = BISEntry.objects.filter(class_id=class_id).order_by('expansion', 'slot', 'rank')
    bis_data = _group_bis_entries(entries)

    class_slot_order = [
        s for s in SLOT_ORDER
        if s not in _BIS_SLOT_CLASS_RESTRICTIONS
        or class_id in _BIS_SLOT_CLASS_RESTRICTIONS[s]
    ]

    return render(request=request,
                  template_name="items/best_in_slot.html",
                  context={
                      "player_classes": PLAYER_CLASSES,
                      "class_archetypes": class_archetypes,
                      "selected_class": selected_class,
                      "class_id": class_id,
                      "locked_expansions": locked_expansions,
                      "first_expansion": min_exp,
                      "bis_data": bis_data,
                      "expansion_order": _BIS_EXPANSION_ORDER,
                      "slot_order": class_slot_order,
                  })


@require_http_methods(["GET"])
def item_name_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    results = Items.objects.filter(Name__icontains=q).order_by('Name').values('id', 'Name')[:20]
    return JsonResponse({'results': [{'id': r['id'], 'name': r['Name']} for r in results]})


def _try_resolve_item_id(item_name):
    """Attempt to find a unique item ID for a given name."""
    hits = Items.objects.filter(Name=item_name)
    if hits.count() == 1:
        return hits.first().id
    return None


@login_required
@require_http_methods(["GET"])
def bis_slot_entries(request: HttpRequest, class_id: int, expansion: str, slot: str) -> JsonResponse:
    """Return the current entries for a slot as JSON (used to populate the editor fresh)."""
    if class_id not in PLAYER_CLASSES or class_id == 0:
        return JsonResponse({"ok": False, "error": "Invalid class."}, status=400)
    if expansion not in _BIS_EXPANSION_ORDER:
        return JsonResponse({"ok": False, "error": "Invalid expansion."}, status=400)
    entries = list(
        BISEntry.objects.filter(class_id=class_id, expansion=expansion, slot=slot).order_by('rank')
    )
    return JsonResponse({
        "ok": True,
        "entries": [
            {"item_name": e.item_name, "item_id": e.item_id, "rank": e.rank, "note": e.note}
            for e in entries
        ],
    })


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def bis_edit_slot(request: HttpRequest, class_id: int, expansion: str, slot: str) -> JsonResponse:
    """
    AJAX endpoint to replace all items in a slot.

    Accepts JSON body:
        {
            "items": [
                {"item_name": "...", "note": "..."},
                ...
            ],
            "edit_summary": "..."
        }

    Items are saved in the order provided (index = rank).
    Returns JSON {"ok": true} or {"ok": false, "error": "..."}.
    """
    if class_id not in PLAYER_CLASSES or class_id == 0:
        return JsonResponse({"ok": False, "error": "Invalid class."}, status=400)
    if expansion not in _BIS_EXPANSION_ORDER:
        return JsonResponse({"ok": False, "error": "Invalid expansion."}, status=400)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

    incoming = body.get("items", [])
    edit_summary = str(body.get("edit_summary", ""))[:200]

    if not isinstance(incoming, list):
        return JsonResponse({"ok": False, "error": "items must be a list."}, status=400)

    # Validate individual items
    cleaned = []
    for i, item in enumerate(incoming):
        name = str(item.get("item_name", "")).strip()[:128]
        note = str(item.get("note", "")).strip()[:150]
        if not name:
            continue
        cleaned.append({"item_name": name, "note": note, "rank": i})

    # Fetch current state for diffing
    existing = {
        e.item_name: e
        for e in BISEntry.objects.filter(class_id=class_id, expansion=expansion, slot=slot)
    }
    incoming_names = {c["item_name"] for c in cleaned}

    revisions = []

    # Removals
    for name, entry in existing.items():
        if name not in incoming_names:
            revisions.append(BISRevision(
                class_id=class_id, expansion=expansion, slot=slot,
                item_name=name, action=BISRevision.ACTION_REMOVE,
                changed_by=request.user, old_rank=entry.rank,
                edit_summary=edit_summary,
            ))
            entry.delete()

    # Additions and reorders
    for c in cleaned:
        name, rank, note = c["item_name"], c["rank"], c["note"]
        if name in existing:
            entry = existing[name]
            old_rank = entry.rank
            old_note = entry.note
            needs_save = False
            if old_rank != rank:
                revisions.append(BISRevision(
                    class_id=class_id, expansion=expansion, slot=slot,
                    item_name=name, action=BISRevision.ACTION_REORDER,
                    changed_by=request.user, old_rank=old_rank, new_rank=rank,
                    edit_summary=edit_summary,
                ))
                entry.rank = rank
                needs_save = True
            if old_note != note:
                revisions.append(BISRevision(
                    class_id=class_id, expansion=expansion, slot=slot,
                    item_name=name, action=BISRevision.ACTION_EDIT,
                    changed_by=request.user, old_note=old_note, new_note=note,
                    edit_summary=edit_summary,
                ))
                entry.note = note
                needs_save = True
            if needs_save:
                entry.save(update_fields=['rank', 'note'])
        else:
            item_id = _try_resolve_item_id(name)
            entry = BISEntry.objects.create(
                class_id=class_id, expansion=expansion, slot=slot,
                item_name=name, rank=rank, note=note, item_id=item_id,
            )
            revisions.append(BISRevision(
                class_id=class_id, expansion=expansion, slot=slot,
                item_name=name, action=BISRevision.ACTION_ADD,
                changed_by=request.user, new_rank=rank,
                edit_summary=edit_summary,
            ))

    BISRevision.objects.bulk_create(revisions)

    # Return the updated slot so the page can re-render it without a reload
    updated_entries = list(
        BISEntry.objects.filter(class_id=class_id, expansion=expansion, slot=slot)
                        .order_by('rank')
    )
    return JsonResponse({
        "ok": True,
        "entries": [
            {"item_name": e.item_name, "item_id": e.item_id, "rank": e.rank, "note": e.note}
            for e in updated_entries
        ],
    })


def bis_history(request: HttpRequest, class_id: int = None) -> HttpResponse:
    """
    Edit history for a class's BIS list, or global history if no class_id.
    """
    class_archetypes = [
        (label, [(cid, PLAYER_CLASSES[cid]) for cid in ids if cid in PLAYER_CLASSES])
        for label, ids in _BIS_CLASS_ARCHETYPES
    ]

    qs = BISRevision.objects.select_related('changed_by').order_by('-changed_at')
    if class_id and class_id in PLAYER_CLASSES:
        qs = qs.filter(class_id=class_id)
        selected_class = PLAYER_CLASSES[class_id]
    else:
        class_id = None
        selected_class = None

    revisions = qs[:200]

    return render(request, "items/bis_history.html", {
        "revisions": revisions,
        "class_id": class_id,
        "selected_class": selected_class,
        "player_classes": PLAYER_CLASSES,
        "class_archetypes": class_archetypes,
        "expansion_labels": dict(BISEntry.EXPANSION_CHOICES if hasattr(BISEntry, 'EXPANSION_CHOICES') else []),
    })
