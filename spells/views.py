import json
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from common.models.spells import SpellsNew
from common.models.items import Items
from spells.utils import calc_buff_duration
from spells.utils import spell_effects
from spells.utils import build_effect_descriptions


def index(request):
    """
    Defines view for https://url.tld/spells/

    :param request: Http request
    :return: an Http Response object
    """
    if request.method == "GET":
        return render(request=request,
                      template_name="spells/spells_index.html",
                      context={},
                      )


def search(request):
    """
    Search for a spell by name

    :param request: Http request
    :return: Http response
    """
    classes = {
        1: "Warrior",
        2: "Cleric",
        3: "Paladin",
        4: "Ranger",
        5: "Shadowknight",
        6: "Druid",
        7: "Monk",
        8: "Bard",
        9: "Rogue",
        10: "Shaman",
        11: "Necromancer",
        12: "Wizard",
        13: "Magician",
        14: "Enchanter",
        15: "Beastlord",
    }
    if request.method == "GET":
        return render(request=request,
                      template_name="spells/search_spells.html",
                      context={"classes": classes},
                      )
    if request.method == "POST":
        spell_name = request.POST.get("spell_name")
        class_name = request.POST.get("class_name")
        level = request.POST.get("level")
        return render(request=request,
                      template_name="spells/search_spells.html",
                      context={"classes": classes},
                      )


def list_spells(request, class_id):
    """
    Defines view for https://url.tld/spells/list/<int:pk>

    :param request: Http request
    :param class_id: a class id field unique identifier
    :return: Http response
    """
    if request.method == "GET":
        clsid = class_id if class_id in [2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15] else None
        return render(request=request,
                      template_name="spells/list.html",
                      context={"class_id": clsid},
                      )


def buy_spells(request, class_id):
    """
    Defines view for https://url.tld/spells/buy/<int:pk>

    :param request: Http request
    :param class_id: a class id field unique identifier
    :return: Http response
    """
    if request.method == "GET":
        clsid = str(class_id) if class_id in [2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15] else None
        filename = f'static/spell_data/spell_buy.json'
        with open(filename, 'r') as json_file:
            spell_list = json.load(json_file)
        spells = spell_list[clsid]
        for spell in spells:
            if spell['purchase_location_info'] != "None":
                grouped_locations = {}
                purchase_locations  = spell['purchase_location_info'].split(';')
                for location in purchase_locations:
                    merchant = location.split(',')
                    zone_key = merchant[3]
                    merchant_id = merchant[0].replace(' ', '')
                    merchant_info = merchant[1]
                    if zone_key not in grouped_locations:
                        grouped_locations.update({zone_key: []})
                    grouped_locations[zone_key].append({'id': merchant_id, 'info': merchant_info})
                    spell['purchase_location_info'] = grouped_locations
        return render(request=request,
                      template_name="spells/buy.html",
                      context={"class_id": clsid,
                               "spells": spells},
                      )


def view_spell(request, spell_id):
    """
    Defines view for https://url.tld/spells/view/<int:pk>

    :param request: Http request
    :param spell_id: a spell id field unique identifier
    :return: Http response
    """
    if request.method == "GET":
        try:
            spell_data = SpellsNew.objects.get(pk=spell_id)
        except ObjectDoesNotExist:
            spell_data = None
        spell_duration = calc_buff_duration(65, spell_data.buff_duration_formula, spell_data.buff_duration)

        # Calculate the minimum level for this spell for spell effect description purposes
        min_level = 65
        for i in range(1, 16):
            if getattr(spell_data, 'classes'+str(i)) < min_level:
                min_level = getattr(spell_data, 'classes'+str(i))

        # Extract slot_id, effect_id, base_value, max_value from spell data
        sp_effects = list()
        for slot_id in range(1, 13):
            if spell_data.__getattribute__(f'effectid{slot_id}') != 254:
                print(slot_id, getattr(spell_data, f'effectid{slot_id}'))
                sp_effects.append(
                    (slot_id,
                     getattr(spell_data, f'effectid{slot_id}'),
                     spell_data.__getattribute__(f'effect_base_value{slot_id}'),
                     spell_data.__getattribute__(f'max{slot_id}'))
                  )

        sp_effects = build_effect_descriptions(sp_effects, spell_duration, min_level)

        try:
            scrolls = Items.objects.filter(scroll_effect=spell_data.id, scroll_type=7)
        except ObjectDoesNotExist:
            scrolls = None
        components = list()
        if spell_data.components1 >= 0:
            components.append((Items.objects.filter(id=spell_data.components1).first(), spell_data.component_counts1))
        if spell_data.components2 >= 0:
            components.append((Items.objects.filter(id=spell_data.components2).first(), spell_data.component_counts2))
        if spell_data.components3 >= 0:
            components.append((Items.objects.filter(id=spell_data.components3).first(), spell_data.component_counts3))
        if spell_data.components4 >= 0:
            components.append((Items.objects.filter(id=spell_data.components4).first(), spell_data.component_counts4))
        return render(request=request,
                      template_name="spells/view_spell.html",
                      context={"spell_data": spell_data,
                               "spell_effects": sp_effects,
                               "scrolls": scrolls,
                               "components": components,
                               "spell_duration": spell_duration},
                      )
