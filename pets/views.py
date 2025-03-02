import logging
from collections import namedtuple

from django.contrib import messages
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError, DatabaseError
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
    """
    View pet by name with its spells

    :param request:  Http request
    :param pet_name: name of the pet
    :return: Http response
    """
    if not pet_name:
        messages.error(request, "No pet name provided.")
        return render(request, "404.html", {})

    pet = NPCTypes.objects.filter(name=pet_name).first()
    if not pet:
        messages.error(request, f"Pet '{pet_name}' not found.")
        return render(request, "404.html", {})

    context = {"pet": pet}

    if not pet.npc_spells_id:
        messages.info(request, f"Pet '{pet_name}' doesn't have any spells.")
        return render(request, "pets/view_pet.html", context)

    try:
        with connections['game_database'].cursor() as cursor:
            cursor.execute(
                "SELECT id FROM npc_spells WHERE id = %s",
                [pet.npc_spells_id]
            )
            pet_spells = cursor.fetchone()

            if not pet_spells:
                messages.warning(request, f"Spell set {pet.npc_spells_id} not found for '{pet_name}'.")
                return render(request, "pets/view_pet.html", context)

            cursor.execute(
                """SELECT spellid
                   FROM npc_spells_entries
                   WHERE npc_spells_id = %s
                      AND minlevel <= %s
                      AND maxlevel >= %s
                   ORDER BY priority DESC""",
                [pet.npc_spells_id, pet.level, pet.level]
            )
            spell_ids = [row[0] for row in cursor.fetchall()]

    except (OperationalError, ProgrammingError, DatabaseError, IndexError) as e:
        logging.error(f"Database error retrieving spells for pet '{pet_name}': {e}")
        messages.error(request, f"An error occurred while retrieving pet spell information.")
        return render(request, "pets/view_pet.html", context)

    if spell_ids:
        spell_list = list(SpellsNew.objects.filter(id__in=spell_ids))
        # Preserve original order from the priority-sorted query
        spell_list.sort(key=lambda x: spell_ids.index(x.id))
        context["spell_list"] = spell_list

    return render(request=request, template_name="pets/view_pet.html", context=context)
