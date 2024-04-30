from django.shortcuts import render, redirect
from django.db import connections

from common.models.items import DiscoveredItems
from common.models.items import Items
from common.models.spells import SpellsNew
from collections import namedtuple


def search(request):
    """
    Search for an item by name at url https://url.tld/items/search

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":
        return render(request=request,
                      template_name="items/search_item.html")

    if request.method == "POST":
        item_name = request.POST.get("item_name")
        query_limit = request.POST.get("query_limit")
        try:
            query_limit = int(query_limit)
        except ValueError:
            return redirect("/items/search")
        if query_limit < 0:
            query_limit = 0
        elif query_limit > 200:  # yes, this is an arbitrary limit on search results
            query_limit = 200
        search_results = Items.objects.filter(Name__icontains=item_name)[:query_limit]

        return render(request=request,
                      template_name="items/search_item.html",
                      context={"search_results": search_results,
                               "level_range": range(100)})


def discovered_items(request):
    """
    Defines view for https://url.tld/items/discovered

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":
        recent_discoveries = DiscoveredItems.objects.all().order_by('-discovered_date')[:10]
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
            recent_discoveries = DiscoveredItems.objects.all().order_by('-discovered_date')[:10]

        return render(request=request,
                      template_name="items/discovered_items.html",
                      context={"discovered_items_list": discovered_items_list,
                               "recent_discoveries": recent_discoveries})


def view_item(request, item_id):
    """
    Defines view for https://url.tld/items/view/<int:pk>

    :param request: Http request
    :param item_id: a NPCTypes id field unique identifier
    :return: Http response
    """
    item = Items.objects.filter(id=item_id).first()
    effect_name = None
    if item.click_effect > 0:
        effect = SpellsNew.objects.filter(id=item.click_effect).first()
        effect_name = effect.name
    elif item.worn_effect > 0:
        effect = SpellsNew.objects.filter(id=item.worn_effect).first()
        effect_name = effect.name
    elif item.proc_effect > 0:
        effect = SpellsNew.objects.filter(id=item.proc_effect).first()
        effect_name = effect.name
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

    return render(request=request,
                  template_name="items/view_item.html",
                  context={
                      "item": item,
                      "drops_from": drops_from,
                      "effect_name": effect_name,
                      "created_by_these_tradeskill_recipes": created_by_these_tradeskill_recipes,
                      "used_in_these_tradeskill_recipes": used_in_these_tradeskill_recipes,
                      "sold_by": sold_by,
                      "forage": forage,
                      "ground_spawns": ground_spawns,
                  })
