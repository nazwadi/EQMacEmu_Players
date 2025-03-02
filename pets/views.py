import logging
from collections import namedtuple

from django.contrib import messages
from django.db import connections
from django.shortcuts import render

from common.constants import PET_CLASSES
from common.models.npcs import NPCTypes
from common.models.spells import SpellsNew


def list_pets(request, pet_class_id: int = None):
    """
    List pets filtered by class id if provided

    :param request:  Http request
    :param pet_class_id: id of the pet class
    :return: Http response
    """
    context = {
        "pet_id": pet_class_id,
        "pet_classes": PET_CLASSES
    }

    if pet_class_id is not None and 1 <= pet_class_id <= 15:

        class_field = f'classes{pet_class_id}'

        query = (
            f"SELECT sn.NAME, sn.id, sn.new_icon, sn.teleport_zone,"
            f"sn.{class_field} AS plevel, nt.race, nt.level, nt.class, "
            f"nt.hp, nt.mana, nt.AC, nt.mindmg, nt.maxdmg "
            f"FROM spells_new sn "
            f"INNER JOIN pets p ON p.type = sn.teleport_zone "
            f"INNER JOIN npc_types nt ON nt.NAME = sn.teleport_zone "
            f"WHERE sn.{class_field} > %s AND sn.{class_field} < %s "
            f"ORDER BY sn.{class_field}"
        )

        with connections['game_database'].cursor() as cursor:
            cursor.execute(query, [0, 70])
            results = cursor.fetchall()

        PetData = namedtuple("PetData", ["name", "id", "new_icon", "teleport_zone", "plevel",
                                         "npc_race", "level", "npc_class", "hp", "mana", "AC", "mindmg", "maxdmg"])

        pets = []
        for result in results:
            pets.append(PetData(*result))

        context["pets"] = pets
    else:
        messages.error(request, f"Invalid pet class ID. Please specify a value between 1 and 15.")

    return render(request=request, template_name="pets/list_pets.html", context=context)


def view_pet(request, pet_name: str = None):
    spells = ''
    pet = NPCTypes.objects.filter(name=pet_name).first()
    pet_spells_query = """SELECT * FROM npc_spells WHERE id = %s"""
    cursor = connections['game_database'].cursor()
    try:
        cursor.execute(pet_spells_query, [pet.npc_spells_id])
        pet_spells = cursor.fetchall()
    except AttributeError as e:
        logging.error(f"Error while searching for spells that summon {pet_name}. Error: {e}")
        messages.error(request, f"Error while searching for spells that summon '{pet_name}'. Spell not found.")
        pet_spells = []
    if pet_spells:
        spells_query = """SELECT npc_spells_entries.spellid
                          FROM npc_spells_entries
                          WHERE npc_spells_entries.npc_spells_id = %s
                              AND npc_spells_entries.minlevel <= %s
                              AND npc_spells_entries.maxlevel >= %s
                          ORDER BY npc_spells_entries.priority DESC"""
        cursor.execute(spells_query, [pet.npc_spells_id, pet.level, pet.level])
        spells = cursor.fetchall()
        spell_list = list()
        for entry in spells:
            entry = entry[0]
            spell = SpellsNew.objects.filter(id=entry).first()
            spell_list.append(spell)

        return render(request=request,
                      template_name="pets/view_pet.html",
                      context={"pet": pet,
                               "spell_list": spell_list})
    return render(request=request,
                  template_name="404.html",
                  context={"pet": pet,})
