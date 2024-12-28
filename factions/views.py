from django.shortcuts import render, redirect
from django.db import connections

from collections import namedtuple
from factions.utils import get_specific_faction_information
from accounts.models import LoginServerAccounts


def index_request(request):
    """
    This will likely become a search page

    :param request: Http request
    :return: Http response
    """
    return redirect("/factions/search")


def search(request):
    """
    Search for a faction by name

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":
        return render(request=request,
                      template_name="factions/search_faction.html")
    if request.method == "POST":
        faction_name = request.POST.get("faction_name")
        query_limit = request.POST.get("query_limit")
        try:
            query_limit = int(query_limit)
        except ValueError:
            return redirect("/factions/search")
        if query_limit < 0:
            query_limit = 0
        elif query_limit > 200:  # yes, this is an arbitrary limit on search results
            query_limit = 200
        cursor = connections['game_database'].cursor()
        query = """SELECT
                    faction_list.id,
                    faction_list.NAME,
                    faction_list.min_cap,
                    faction_list.max_cap 
                  FROM
                    faction_list 
                  WHERE
                    faction_list.NAME LIKE %s 
                  ORDER BY
                    faction_list.NAME 
                    LIMIT %s"""
        cursor.execute(query, ["%" + faction_name + "%", query_limit])
        faction_results = cursor.fetchall()
        return render(request=request,
                      context={"faction_results": faction_results,
                               "query_limit": query_limit},
                      template_name="factions/search_faction.html")


def view_faction(request, faction_id):
    """
    Defines view for https://url.tld/factions/view/<int:pk>

    :param request: Http request
    :param faction_id: a factions id field unique identifier
    :return: Http response
    """
    if request.method == "GET":
        faction_name_query = """SELECT
                                    faction_list.id,
                                    faction_list.NAME 
                                FROM
                                    faction_list
                                WHERE
                                    faction_list.id = %s"""
        cursor = connections['game_database'].cursor()
        cursor.execute(faction_name_query, [faction_id])
        faction_name = cursor.fetchone()

        # Kill these NPCs to raise faction
        raise_faction_query = """SELECT DISTINCT
                                    npc_types.id,
                                    npc_types.NAME,
                                    zone.long_name,
                                    spawn2.zone,
                                    npc_faction_entries.VALUE
                                FROM
                                    npc_faction_entries,
                                    npc_types,
                                    spawnentry,
                                    spawn2,
                                    zone 
                                WHERE
                                    npc_faction_entries.faction_id = %s 
                                    AND npc_faction_entries.npc_faction_id = npc_types.npc_faction_id 
                                    AND npc_faction_entries.VALUE > 0 
                                    AND npc_types.id = spawnentry.npcID 
                                    AND spawn2.spawngroupID = spawnentry.spawngroupID 
                                    AND zone.short_name = spawn2.zone 
                                ORDER BY
                                    zone.long_name"""
        cursor.execute(raise_faction_query, [faction_id])
        raise_faction_result = cursor.fetchall()
        raise_faction_groups = dict()
        for row in raise_faction_result:
            if row[2] not in raise_faction_groups:
                raise_faction_groups[row[2]] = list()
            raise_faction_groups[row[2]].append(row)
        lower_faction_query = """SELECT DISTINCT
                                    npc_types.id,
                                    npc_types.NAME,
                                    zone.long_name,
                                    spawn2.zone,
                                    npc_faction_entries.VALUE
                                FROM
                                    npc_faction_entries,
                                    npc_types,
                                    spawnentry,
                                    spawn2,
                                    zone 
                                WHERE
                                    npc_faction_entries.faction_id = %s 
                                    AND npc_faction_entries.npc_faction_id = npc_types.npc_faction_id 
                                    AND npc_faction_entries.VALUE < 0 
                                    AND npc_types.id = spawnentry.npcID 
                                    AND spawn2.spawngroupID = spawnentry.spawngroupID 
                                    AND zone.short_name = spawn2.zone 
                                ORDER BY
                                    zone.long_name"""
        cursor.execute(lower_faction_query, [faction_id])
        lower_faction_result = cursor.fetchall()
        lower_faction_groups = dict()
        for row in lower_faction_result:
            if row[2] not in lower_faction_groups:
                lower_faction_groups[row[2]] = list()
            lower_faction_groups[row[2]].append(row)

        if request.user.is_authenticated:
            ls_accounts = LoginServerAccounts.objects.filter(ForumName=request.user.username)
            ls_account_ids = [ls_account.LoginServerID for ls_account in ls_accounts]
            cursor = connections['game_database'].cursor()
            character_query = ("SELECT DISTINCT cd.id, cd.name, cd.race, cd.class, cd.deity "
                               "FROM account ac JOIN character_data cd ON ac.id = cd.account_id "
                               "WHERE ac.lsaccount_id IN %s")
            cursor.execute(character_query, [tuple(ls_account_ids)])
            result = cursor.fetchall()
            character_faction_list = []
            CharacterFaction = namedtuple("FactionTableRow", "id name modified_base min_cap max_cap current_value")
            for cd_id, cd_name, cd_race, cd_class, cd_deity in result:
                character_faction = get_specific_faction_information(cd_id, cd_race, cd_class, cd_deity,
                                                                     faction_name[1])
                if character_faction:
                    cf = CharacterFaction(*character_faction)
                    character_faction_list.append([cd_name,cf])

            return render(request=request,
                          context={
                              "character_faction_list": character_faction_list,
                              "faction_name": faction_name,
                              "raise_faction": raise_faction_groups,
                              "lower_faction": lower_faction_groups
                          },
                          template_name="factions/view_faction.html")
        else:
            return render(request=request,
                          context={"faction_name": faction_name,
                                   "raise_faction": raise_faction_groups,
                                   "lower_faction": lower_faction_groups},
                          template_name="factions/view_faction.html")
    redirect("/factions/search")
