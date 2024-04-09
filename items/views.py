from django.shortcuts import render, redirect
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist

from common.models.items import Items
from common.models.spells import SpellsNew
from common.utils import calculate_item_price
from collections import namedtuple


def search(request):
    """
    Search for an item by name

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":
        return render(request=request,
                      template_name="items/search_item.html")

    if request.method == "POST":
        item_name = request.POST.get("item_name")
        search_results = Items.objects.filter(Name__icontains=item_name)

        return render(request=request,
                      template_name="items/search_item.html",
                      context={"search_results": search_results,
                               "level_range": range(100)})


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
                                                   "lte_multiplier", "lte_probability", "lde_chance"])
    for npc_id, npc_name, z_short_name, z_long_name, lte_multiplier, lte_probability, lde_chance in drops_from_result:
        if z_short_name not in drops_from:
            drops_from[z_short_name] = list()
        drops_from[z_short_name].append(DropsFromTuple(npc_id=npc_id, npc_name=npc_name, z_short_name=z_short_name,
                                                       z_long_name=z_long_name, lte_multiplier=lte_multiplier,
                                                       lte_probability=lte_probability, lde_chance=lde_chance))

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

    return render(request=request,
                  template_name="items/view_item.html",
                  context={
                      "item": item,
                      "drops_from": drops_from,
                      "effect_name": effect_name,
                      "created_by_these_tradeskill_recipes": created_by_these_tradeskill_recipes,
                      "used_in_these_tradeskill_recipes": used_in_these_tradeskill_recipes,
                      "sold_by": sold_by,
                  })
