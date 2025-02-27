import logging

from common.constants import PET_CLASSES
from common.models.npcs import NPCTypes
from common.models.spells import SpellsNew
from django.shortcuts import render
from django.db import connections
from django.contrib import messages
from django.http import Http404
from collections import namedtuple


def list_pets(request, pet_class_id: int = None):
    """

    :param request:  Http request
    :param pet_class_id: id of the pet class
    :return: Http response
    """
    if pet_class_id is not None:
        pets_query = (f"SELECT spells_new.NAME, spells_new.id, spells_new.new_icon, spells_new.teleport_zone,"
                      f"{'spells_new.classes' + str(pet_class_id)} AS plevel, npc_types.race, npc_types.`level`,npc_types.class, npc_types.hp, npc_types.mana,"
                      f"npc_types.AC, npc_types.mindmg,npc_types.maxdmg FROM spells_new INNER JOIN pets ON pets.`type` = spells_new.teleport_zone"
                      f" INNER JOIN npc_types ON npc_types.NAME = spells_new.teleport_zone "
                      f"WHERE {'spells_new.classes' + str(pet_class_id)} > 0 AND {'spells_new.classes' + str(pet_class_id)} < 70 "
                      f"ORDER BY {'spells_new.classes' + str(pet_class_id)}")
        cursor = connections['game_database'].cursor()
        cursor.execute(pets_query)
        results = cursor.fetchall()
        PetData = namedtuple("PetData", ["name", "id", "new_icon", "teleport_zone", "plevel",
                                         "npc_race", "level", "npc_class", "hp", "mana", "AC", "mindmg",
                                         "maxdmg"])
        pets = list()
        for result in results:
            pets.append(PetData(*result))
        return render(request=request,
                      template_name="pets/list_pets.html",
                      context={"pet_id": pet_class_id,
                               "pet_classes": PET_CLASSES,
                               "pets": pets})
    return render(request=request,
                  template_name="pets/list_pets.html",
                  context={"pet_id": pet_class_id,
                           "pet_classes": PET_CLASSES})


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
