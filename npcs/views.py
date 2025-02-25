import json
import logging

from django.shortcuts import render, redirect
from django.db import connections
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from dataclasses import asdict
from collections import namedtuple
from django.views.decorators.http import require_http_methods

from npcs.models import NpcPage
from common.models.loot import LootTable, LootDropEntries
from common.models.loot import LootTableEntries
from common.models.npcs import NPCTypes
from common.models.npcs import MerchantList
from common.models.spawns import SpawnEntry
from common.models.spawns import Spawn2
from common.models.spawns import SpawnGroup
from common.utils import calculate_item_price
from quests.models import Quests
from .abilities.special_abilities import get_ability_by_name, get_ability_by_id

logger = logging.getLogger(__name__)


def index_request(request):
    """
    This will likely become a search page

    :param request: Http request
    :return: Http response
    """
    return redirect("/npcs/search")


def search(request):
    """
    Search for a npc by name

    :param request: Http request
    :return: Http response
    """
    filename = f'static/npcs/npc_body_types.json'
    with open(filename, 'r') as json_file:
        npc_body_types = json.load(json_file)

    filename = f'static/npcs/npc_races.json'
    with open(filename, 'r') as json_file:
        npc_races = json.load(json_file)

    filename = f'static/npcs/npc_classes.json'
    with open(filename, 'r') as json_file:
        npc_classes = json.load(json_file)

    filename = f'static/common/expansions.json'
    with open(filename, 'r') as json_file:
        expansions = json.load(json_file)

    if request.method == "GET":
        return render(request=request,
                      context={
                          'expansions': expansions['expansions'],
                          'npc_body_types': npc_body_types['npc_body_types'],
                          'npc_races': npc_races['npc_races'],
                          'npc_classes': npc_classes['npc_classes'],
                      },
                      template_name="npcs/search_npc.html")
    if request.method == "POST":
        body_type = request.POST.get("select_npc_body_type")
        expansion = request.POST.get("select_expansion")
        npc_name = request.POST.get("npc_name")
        npc_name = npc_name.replace(' ', '_')
        min_level = request.POST.get("min_level")
        max_level = request.POST.get("max_level")
        npc_race = request.POST.get("select_npc_race")
        npc_class = request.POST.get("select_npc_class")
        query_limit = request.POST.get("query_limit")
        exclude_merchants = request.POST.get("exclude_merchants")
        try:
            query_limit = int(query_limit)
        except ValueError:
            return redirect("/npcs/search")
        if query_limit < 0:
            query_limit = 0
        elif query_limit > 200:  # yes, this is an arbitrary limit on search results
            query_limit = 200
        try:
            cursor = connections['game_database'].cursor()
            query = """SELECT DISTINCT
                                nt.id,
                                nt.NAME,
                                s.min_expansion,
                                z.long_name,
                                z.short_name,
                                nt.LEVEL,
                                nt.maxlevel,
                                nt.race,
                                nt.class,
                                nt.gender,
                                nt.hp,
                                nt.MR,
                                nt.CR,
                                nt.FR, 
                                nt.DR,
                                nt.PR
                             FROM
                                npc_types AS nt
                                LEFT JOIN spawnentry AS se ON nt.id = se.npcID
                                LEFT JOIN spawn2 AS s ON se.spawngroupID = s.spawngroupID
                                LEFT JOIN zone AS z ON s.zone = z.short_name 
                            WHERE
                                nt.NAME LIKE %s
                                AND nt.LEVEL >= %s
                                AND nt.maxlevel <= %s
            """
            if exclude_merchants is not None:
                query += " AND nt.merchant_id = 0"
            query_list = ['%' + npc_name + '%', min_level, max_level]
            if expansion != "-1":  # any
                query += """ AND s.min_expansion = %s"""
                query_list.append(expansion)
            if body_type != "-1":  # any
                query += """ AND nt.bodytype = %s"""
                query_list.append(body_type)
            if npc_race != "-1":  # any
                query += """ AND nt.race = %s"""
                query_list.append(npc_race)
            if npc_class != "-1":  # any
                query += """ AND nt.class = %s"""
                query_list.append(npc_class)
            query += """ LIMIT %s"""
            query_list.append(int(query_limit))
            cursor.execute(query, query_list)
            results = cursor.fetchall()
        except Exception as e:
            logger.error(f"Error executing NPC search query: {e}", exc_info=True)
            results = []

        search_results = list()
        if results:
            for result in results:
                NpcTuple = namedtuple("NpcTuple", ["id", "name", "min_expansion", "long_name",
                                                   "short_name", "level", "maxlevel", "race", "class_name", "gender",
                                                   "hp", "MR", "CR", "FR", "DR", "PR"])
                search_results.append(NpcTuple(*result))

        return render(request=request,
                      template_name="npcs/search_npc.html",
                      context={
                          'expansions': expansions['expansions'],
                          "level_range": range(100),
                          'npc_body_types': npc_body_types['npc_body_types'],
                          'npc_races': npc_races['npc_races'],
                          'npc_classes': npc_classes['npc_classes'],
                          "search_results": search_results,
                      })


def view_npc(request, npc_id):
    """
    Defines view for https://url.tld/npcs/view/<int:pk>

    :param request: Http request
    :param npc_id: a NPCTypes id field unique identifier
    :return: Http response
    """
    npc_data = NPCTypes.objects.filter(id=npc_id).first()
    npc_page_text = NpcPage.objects.filter(npc_id=npc_id).first()
    if npc_data is None:
        return redirect("accounts:index")
    cursor = connections['game_database'].cursor()

    try:
        cursor.execute("""SELECT DISTINCT
                            sn.custom_icon,
                            sn.name,
                            sn.id
                          FROM
                            npc_spells_entries nse
                            JOIN npc_types nt ON nse.npc_spells_id = nt.npc_spells_id
                            JOIN spells_new sn ON nse.spellid = sn.id 
                          WHERE
                            nse.npc_spells_id=%s;
        """, [npc_data.npc_spells_id])
        npc_spells_entries = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching spell entries for NPC {npc_id}: {e}", exc_info=True)
        npc_spells_entries = []

    try:
        cursor.execute("""SELECT DISTINCT
                            sn.NAME,
                            sn.custom_icon,
                            ns.attack_proc,
                            ns.proc_chance 
                          FROM
                            spells_new sn
                            JOIN npc_spells ns ON ns.attack_proc = sn.id 
                          WHERE
                            ns.id=%s;
        """, [npc_data.npc_spells_id])
        npc_spell_proc_data = cursor.fetchone()
    except Exception as e:
        logger.error(f"Error fetching spell proc data for NPC {npc_id}: {e}", exc_info=True)
        npc_spell_proc_data = []

    if npc_spell_proc_data:
        ProcData = namedtuple('ProcData', ['spell_name', 'custom_icon', 'proc', 'proc_chance'])
        npc_spell_proc_data = ProcData(*npc_spell_proc_data)
    else:
        npc_spell_proc_data = None

    try:
        cursor.execute("""SELECT 
                                z.long_name,
                                z.short_name,
                                s.x,
                                s.y,
                                s.z,
                                s.respawntime,
                                s.variance,
                                s.min_expansion,
                                s.max_expansion
                            FROM
                                npc_types AS n
                                JOIN spawnentry AS se ON n.id = se.npcID
                                JOIN spawn2 AS s ON se.spawngroupID = s.spawngroupID
                                JOIN zone AS z ON s.zone = z.short_name 
                            WHERE
                                n.id=%s
                                AND race != '127' 
                                AND race != '240' 
                                AND z.min_status = 0;
        """, [npc_data.id])
        spawn_data = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching spawn data for NPC {npc_id}: {e}", exc_info=True)
        spawn_data = []

    spawn_point_list = []
    if spawn_data:
        for spawn in spawn_data:
            SpawnData = namedtuple("SpawnData", ["long_name", "short_name", "x", "y", "z",
                                                 "respawntime", "variance", "min_expansion", "max_expansion"])
            spawn_point_list.append(SpawnData(*spawn))

    try:
        expansion = spawn_point_list[0].min_expansion
    except IndexError:
        expansion = None
    ZoneTuple = namedtuple("Zone", ["long_name", "short_name"])
    try:
        zone = ZoneTuple(spawn_point_list[0].long_name, spawn_point_list[0].short_name)
    except IndexError:
        zone = ZoneTuple(None, None)

    spawn_entries_spawngroup_result = SpawnEntry.objects.filter(npcID=npc_data.id).order_by("-spawngroupID")
    spawn_groups = {}
    for spawn_entry in spawn_entries_spawngroup_result:
        spawn_entries_result = SpawnEntry.objects.filter(spawngroupID=spawn_entry.spawngroupID)
        spawn_points_result = Spawn2.objects.filter(spawngroupID=spawn_entry.spawngroupID)
        spawn_groups[spawn_entry.spawngroupID] = spawn_entries_result, spawn_points_result

    try:
        cursor.execute("""SELECT
                            fl.id,
                            fl.NAME,
                            nfe.value,
                            nfe.npc_value
                        FROM
                            npc_faction_entries nfe
                            JOIN faction_list fl ON nfe.faction_id = fl.id 
                        WHERE
                            nfe.npc_faction_id=%s;
                        """, [npc_data.npc_faction_id])
        npc_faction_entries = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching npc faction entries for NPC {npc_id}: {e}", exc_info=True)
        npc_faction_entries = []

    factions = []
    opposing_factions = []
    for fid, name, value, npc_value in npc_faction_entries:
        if value > 0:
            opposing_factions.append((name, value, npc_value))
        else:
            factions.append((name, value, npc_value))

    merchant_list_result = MerchantList.objects.filter(merchant_id=npc_data.merchant_id)
    MerchantListTuple = namedtuple('MerchantList', ['id', 'name', 'icon', 'platinum', 'gold',
                                                    'silver', 'copper', 'charges', 'quantity'])
    merchant_list = []
    for item in merchant_list_result:
        platinum, gold, silver, copper = calculate_item_price(item.item.price)
        merchant_list.append(MerchantListTuple(id=item.item.id,
                                               name=item.item.Name,
                                               icon=item.item.icon,
                                               platinum=platinum,
                                               gold=gold,
                                               silver=silver,
                                               copper=copper,
                                               charges=-1,
                                               quantity=-1))

    try:
        loottable = LootTable.objects.get(id=npc_data.loottable_id)
    except ObjectDoesNotExist:
        loottable = None
    if loottable:
        loottable_entries = LootTableEntries.objects.filter(loottable_id=loottable.id)
        loot_tables = {}
        for lootdrop_table in loottable_entries:
            try:
                ld_entries = LootDropEntries.objects.filter(lootdrop_id=lootdrop_table.lootdrop_id.id)
                loot_tables[lootdrop_table.lootdrop_id] = lootdrop_table, ld_entries
            except ObjectDoesNotExist:
                continue
    else:
        loot_tables = {}

    paths_query = """SELECT 
                        zone.zoneidnumber, 
                        zone.long_name, 
                        zone.short_name,
                        spawn2.pathgrid,
                        spawngroup.wp_spawns,
                        grid_entries.number,  
                        grid_entries.x,
                        grid_entries.y
                    FROM 
                        zone
                    JOIN 
                        spawn2 ON spawn2.zone = zone.short_name
                    JOIN 
                        spawnentry ON spawnentry.spawngroupID = spawn2.spawngroupID
                    JOIN 
                        spawngroup ON spawnentry.spawngroupID = spawngroup.id
                    JOIN 
                        grid_entries ON spawn2.pathgrid = grid_entries.gridid AND zone.zoneidnumber = grid_entries.zoneid
                    WHERE 
                        spawnentry.npcID = %s
                    GROUP BY pathgrid, number, zoneidnumber, long_name, short_name, wp_spawns
                    ORDER BY 
                        zone.zoneidnumber, zone.long_name, zone.short_name, spawn2.pathgrid, CAST(grid_entries.number AS SIGNED);
                    """
    try:
        cursor.execute(paths_query, [npc_data.id])
        paths = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching path data for NPC {npc_id}: {e}", exc_info=True)
        paths = []

    creature_path_points = {}

    enable_wp_spawn_notice = False
    for path in paths:
        grid_id = path[3]  # pathgrid
        wp_spawns = path[4]
        x = float(path[6])  # x
        y = float(path[7])  # y

        if grid_id not in creature_path_points:
            creature_path_points[grid_id] = []
        if wp_spawns == 1 and grid_id > 0:
            enable_wp_spawn_notice = True

        creature_path_points[grid_id].append({'x': -x, 'y': -y})

    roam_boxes = []
    spawn_entries = SpawnEntry.objects.filter(npcID=npc_data.id).order_by("-spawngroupID")
    for spawn_entry in spawn_entries:
        roam_box = SpawnGroup.objects.filter(id=spawn_entry.spawngroupID).first()
        try:
            if roam_box.max_x != 0 and roam_box.max_y != 0:
                max_x = roam_box.max_x
                min_x = roam_box.min_x
                max_y = roam_box.max_y
                min_y = roam_box.min_y
                width = max_x - min_x
                height = max_y - min_y
                roam_boxes.append({'start_x': min_x, 'start_y': min_y, 'width': width, 'height': height})
        except AttributeError:  # 'NoneType' object has no attribute 'max_x'
            continue

    seen_rb = set()
    unique_rb = []
    for roam_box in roam_boxes:
        items = tuple(roam_box.items())
        if items not in seen_rb:
            seen_rb.add(items)
            unique_rb.append(roam_box)

    related_quests = Quests.objects.filter(
        Q(related_npcs__npc_id=npc_data.id) |
        Q(starting_npc_id=npc_data.id)
    ).distinct()

    return render(request=request,
                  template_name="npcs/view_npc.html",
                  context={
                      "creature_path_points": json.dumps(creature_path_points),
                      "enable_wp_spawn_notice": enable_wp_spawn_notice,
                      "roam_boxes": unique_rb,
                      "expansion": expansion,
                      "factions": factions,
                      "loottable": loottable,
                      "loot_tables": loot_tables,
                      "merchant_list": merchant_list,
                      "npc_data": npc_data,
                      "npc_page_text": npc_page_text,
                      "npc_spells_entries": npc_spells_entries,
                      "npc_spell_proc_data": npc_spell_proc_data,
                      "opposing_factions": opposing_factions,
                      "related_quests": related_quests,
                      "spawn_point_list": spawn_point_list,
                      "spawn_groups": spawn_groups,
                      "zone": zone,
                  })



@require_http_methods(["GET"])
def npc_special_abilities_api(request, ability_name:str):
    if not ability_name:
        return JsonResponse({'error': 'Ability name is required'}, status=400)

    ability = get_ability_by_name(ability_name)
    if ability:
        return JsonResponse(asdict(ability))

    return JsonResponse({'error': f'Ability "{ability_name}" not found'}, status=404)