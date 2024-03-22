import math
from django.shortcuts import render, redirect
from django.db import connections
from common.models.npcs import NPCTypes
from common.models.npcs import MerchantList
from common.models.npcs import MerchantListTemp
from common.utils import calculate_item_price
from collections import namedtuple


def index_request(request):
    """
    This will likely become a search page

    :param request: Http request
    :return: Http response
    """
    return render(request=request,
                  template_name="npcs/view_npc.html")


def list_npcs(request):
    """
    Displays a list of npcs that match the npc name

    :param request: Http request
    :return: Http response
    """
    return render(request=request,
                  template_name="npcs/view_npc.html")


def view_npc(request, npc_id):
    """
    Defines view for https://url.tld/npcs/view/<int:pk>

    :param request: Http request
    :param npc_id: a NPCTypes id field unique identifier
    :return: Http response
    """
    npc_data = NPCTypes.objects.filter(id=npc_id).first()
    if npc_data is None:
        return redirect("accounts:index")
    cursor = connections['game_database'].cursor()

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
    if npc_spell_proc_data:
        ProcData = namedtuple('ProcData', ['spell_name', 'custom_icon', 'proc', 'proc_chance'])
        npc_spell_proc_data = ProcData(*npc_spell_proc_data)
    else:
        npc_spell_proc_data = None

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
    spawn_point_list = list()
    if spawn_data:
        for spawn in spawn_data:
            SpawnData = namedtuple("SpawnData", ["long_name", "short_name", "x", "y", "z",
                                                 "respawntime", "variance", "min_expansion", "max_expansion"])
            spawn_point_list.append(SpawnData(*spawn))

    print(spawn_point_list)
    ZoneTuple = namedtuple("Zone", ["long_name", "short_name"])
    zone = ZoneTuple(spawn_point_list[0].long_name, spawn_point_list[0].short_name)
    cursor.execute("""SELECT
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
    factions = list()
    opposing_factions = list()
    for name, value, npc_value in npc_faction_entries:
        if value > 0:
            opposing_factions.append((name, value, npc_value))
        else:
            factions.append((name, value, npc_value))

    merchant_list_result = MerchantList.objects.filter(merchant_id=npc_data.merchant_id)
    merchant_list_temp_result = MerchantListTemp.objects.filter(npc_id=npc_data.merchant_id)
    MerchantListTuple = namedtuple('MerchantList', ['id', 'name', 'icon', 'platinum', 'gold',
                                                    'silver', 'copper', 'charges', 'quantity'])
    merchant_list = list()
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

    merchant_list_temp = list()
    for item in merchant_list_temp_result:
        platinum, gold, silver, copper = calculate_item_price(item.item_id.price)
        merchant_list_temp.append(MerchantListTuple(id=item.item_id.id,
                                                    name=item.item_id.Name,
                                                    icon=item.item_id.icon,
                                                    platinum=platinum,
                                                    gold=gold,
                                                    silver=silver,
                                                    copper=copper,
                                                    charges=item.charges,
                                                    quantity=item.quantity, ))

    return render(request=request,
                  template_name="npcs/view_npc.html",
                  context={"npc_data": npc_data,
                           "npc_spells_entries": npc_spells_entries,
                           "npc_spell_proc_data": npc_spell_proc_data,
                           "factions": factions,
                           "opposing_factions": opposing_factions,
                           "spawn_point_list": spawn_point_list,
                           "merchant_list": merchant_list,
                           "merchant_list_temp": merchant_list_temp,
                           "zone": zone, })
