from django.shortcuts import render
from django.db import connections
from collections import namedtuple

from common.models.zones import Zone
from common.models.spawns import SpawnEntry


def index(request):
    """
    Displays the /zones/ page

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":

        zone_data = Zone.objects.all()

        return render(request=request,
                      template_name="zones/index.html",
                      context={"zone_data": zone_data, })


def view_zone(request, short_name):
    """
    Displays the /zones/<short_name> page

    :param request: Http request
    :param short_name: a zone short_name
    :return: Http response
    """
    cursor = connections['game_database'].cursor()
    zone_data = Zone.objects.filter(short_name=short_name).first()

    cursor.execute("""SELECT DISTINCT d.id, d.name, d.race, d.class, d.level, a.min_expansion 
                      FROM spawn2 a
                        JOIN spawngroup b ON b.id = a.spawngroupID
                        JOIN spawnentry c ON c.spawngroupID = b.id
                        JOIN npc_types d ON d.id = c.npcID
                      WHERE a.zone = %s
                      ORDER BY d.name, d.id""", [zone_data.short_name])
    npc_results = cursor.fetchall()

    cursor.execute("""SELECT gs.id, gs.max_x, gs.max_y, gs.max_z, gs.min_x, gs.min_y, gs.heading, 
                             gs.max_allowed, gs.comment AS comment, gs.respawn_timer, gs.item AS giid, i.name AS name, 
                             gs.min_expansion, gs.max_expansion
                       FROM ground_spawns gs 
                         JOIN items i ON gs.item = i.id
                       WHERE gs.zoneid=%s AND gs.item=i.id OR gs.zoneid=0 AND gs.item=i.id""", [zone_data.zone_id_number])
    ground_spawn_results = cursor.fetchall()

    SpawnPoint = namedtuple('SpawnPoint', ['x', 'y', 'z', 'respawntime', 'variance', 'min_expansion',
                                                'max_expansion', 'enabled'])
    cursor.execute("""SELECT DISTINCT spawngroupID, x, y, z, respawntime, variance, min_expansion, max_expansion, enabled 
                      FROM spawn2 
                      WHERE zone = %s""", [zone_data.short_name])
    spawn_point_results = cursor.fetchall()
    spawn_points = list()
    for sp in spawn_point_results:
        point = SpawnPoint(sp[1], sp[2], sp[3], sp[4], sp[5], sp[6], sp[7], sp[8])
        spawn_entry_results = SpawnEntry.objects.filter(spawngroupID=sp[0])
        spawn_points.append((point, spawn_entry_results))

    cursor.execute("""SELECT f.id, i.name, f.skill_level, f.chance 
                      FROM fishing f 
                        JOIN items i on i.id=f.itemid
                      WHERE f.zoneid=%s""", [zone_data.zone_id_number])
    fish = cursor.fetchall()

    cursor.execute("""SELECT f.id, i.name, f.level, f.chance 
                      FROM forage f 
                        JOIN items i on i.id=f.itemid
                      WHERE f.zoneid=%s""", [zone_data.zone_id_number])
    forage = cursor.fetchall()

    cursor.execute("""SELECT nt.merchant_id, nt.name, nt.race, nt.class, nt.gender, s.y, s.x, s.z, s.min_expansion
                      FROM npc_types as nt
                        JOIN spawnentry AS se ON nt.id = se.npcID
                        JOIN spawn2 as s ON se.spawngroupID = s.spawngroupID
                        JOIN zone as z ON s.zone = z.short_name
                      WHERE nt.merchant_id > 0 and z.short_name = %s;""", [zone_data.short_name])
    merchant_results = cursor.fetchall()

    return render(request=request,
                  template_name="zones/view_zone.html",
                  context={"zone_data": zone_data,
                           "merchants": merchant_results,
                           "npc_results": npc_results,
                           "ground_spawns": ground_spawn_results,
                           "spawn_points": spawn_points,
                           "fish": fish,
                           "forage": forage, })
