from django.shortcuts import render, redirect
from django.db import connections
from collections import namedtuple

from zones.models import ZonePage
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
    if not zone_data:
        return redirect("zones:index")
    cursor.execute("""SELECT DISTINCT zp.target_zone_id, z.short_name, z.long_name
                                    FROM zone_points zp JOIN zone z ON zp.target_zone_id = z.zoneidnumber 
                                    WHERE zone=%s""", [[short_name]])
    zone_points = cursor.fetchall()

    zone_page_text = ZonePage.objects.filter(short_name=zone_data.short_name).first()

    cursor.execute("""SELECT DISTINCT d.id, d.name, d.race, d.class, d.gender, d.level, d.hp, d.MR, d.CR, d.FR, d.DR, d.PR, d.maxlevel, a.min_expansion, a.max_expansion 
                      FROM spawn2 a
                        JOIN spawngroup b ON b.id = a.spawngroupID
                        JOIN spawnentry c ON c.spawngroupID = b.id
                        JOIN npc_types d ON d.id = c.npcID
                      WHERE a.zone = %s and d.race != '127'
                      ORDER BY d.name, d.id""", [zone_data.short_name])  # Race 127 = 'Invisible Man'
    npc_results = cursor.fetchall()

    cursor.execute("""SELECT gs.id, gs.max_x, gs.max_y, gs.max_z, gs.min_x, gs.min_y, gs.heading, 
                             gs.max_allowed, gs.comment AS comment, gs.respawn_timer, gs.item AS giid, i.name AS name, 
                             i.icon as icon, gs.min_expansion, gs.max_expansion
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
        spawn_entry_results = SpawnEntry.objects.filter(spawngroupID=sp[0]).exclude(npcID__race='127')
        if spawn_entry_results:
            spawn_points.append((point, spawn_entry_results))

    cursor.execute("""SELECT i.id, i.name, i.icon, f.skill_level, f.chance, f.min_expansion, f.max_expansion
                      FROM fishing f 
                        JOIN items i on i.id=f.itemid
                      WHERE f.zoneid=%s""", [zone_data.zone_id_number])
    fish = cursor.fetchall()

    cursor.execute("""SELECT i.id, i.name, i.icon, f.level, f.chance, f.min_expansion, f.max_expansion
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

    cursor.execute("""SELECT
                        i.id,
                        i.NAME,
                        i.icon,
                        GROUP_CONCAT( DISTINCT CONCAT( n.NAME, ':', n.id ) ORDER BY n.NAME SEPARATOR ',' ) AS DroppingNPCs 
                      FROM
                        spawnentry se
                        INNER JOIN ( SELECT * FROM spawn2 WHERE zone = %s ) AS A ON se.spawngroupID = A.spawngroupID
                        INNER JOIN npc_types n ON n.id = se.npcID
                        INNER JOIN ( SELECT DISTINCT lte.lootdrop_id, lte.loottable_id FROM loottable_entries lte ) AS B ON n.loottable_id = B.loottable_id
                        INNER JOIN ( SELECT DISTINCT lde.item_id, lde.lootdrop_id FROM lootdrop_entries lde ) AS C ON B.lootdrop_id = C.lootdrop_id
                        INNER JOIN items i ON C.item_id = i.id 
                      GROUP BY
                        i.id,
                        i.NAME 
                      ORDER BY
                        i.NAME;""", [zone_data.short_name])
    items_result = cursor.fetchall()

    return render(request=request,
                  template_name="zones/view_zone.html",
                  context={"zone_data": zone_data,
                           "zone_points": zone_points,
                           "zone_page_text": zone_page_text,
                           "merchants": merchant_results,
                           "items": items_result,
                           "npc_results": npc_results,
                           "ground_spawns": ground_spawn_results,
                           "spawn_points": spawn_points,
                           "fish": fish,
                           "forage": forage, })
