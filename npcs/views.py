from django.shortcuts import render, redirect
from django.db import connections
from common.models.npcs import NPCTypes
from common.models.npcs import NPCSpellsEntries
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
                            s.min_expansion,
                            s.max_expansion,
                            s.respawntime
                        FROM
                            npc_types AS n
                            JOIN spawnentry AS se ON n.id = se.npcID
                            JOIN spawn2 AS s ON se.spawngroupID = s.spawngroupID
                            JOIN zone AS z ON s.zone = z.short_name 
                        WHERE
                            n.id=%s
                            AND race != '127' 
                            AND race != '240' 
                            AND z.min_status = 0 
                            LIMIT 1;
    
    """, [npc_data.id])
    spawn_data = cursor.fetchone()
    if spawn_data:
        SpawnData = namedtuple("SpawnData", "long_name short_name min_expansion max_expansion respawntime")
        spawn_data = SpawnData(*spawn_data)
    else:
        spawn_data = None

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

    return render(request=request,
                  template_name="npcs/view_npc.html",
                  context={"npc_data": npc_data,
                           "npc_spells_entries": npc_spells_entries,
                           "npc_spell_proc_data": npc_spell_proc_data,
                           "factions": factions,
                           "opposing_factions": opposing_factions,
                           "spawn_data": spawn_data, })
