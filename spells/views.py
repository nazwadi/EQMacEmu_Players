import json
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from common.models.spells import SpellsNew
from common.models.items import Items
from spells.utils import calc_buff_duration
from spells.utils import build_effect_descriptions
from spells.utils import prep_spell_data
from django.db.models import Q


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
        clsid = class_id if class_id in [2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15] else 0
        match clsid:
            case 2:
                result = (SpellsNew.objects.filter(classes2__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes2')).order_by(f"classes{clsid}"))
            case 3:
                result = (SpellsNew.objects.filter(classes3__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes3')).order_by(f"classes{clsid}"))
            case 4:
                result = (SpellsNew.objects.filter(classes4__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes4')).order_by(f"classes{clsid}"))
            case 5:
                result = (SpellsNew.objects.filter(classes5__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes5')).order_by(f"classes{clsid}"))
            case 6:
                result = (SpellsNew.objects.filter(classes6__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes6')).order_by(f"classes{clsid}"))
            case 8:
                result = (SpellsNew.objects.filter(classes8__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes8')).order_by(f"classes{clsid}"))
            case 10:
                result = (SpellsNew.objects.filter(classes10__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes10')).order_by(f"classes{clsid}"))
            case 11:
                result = (SpellsNew.objects.filter(classes11__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes11')).order_by(f"classes{clsid}"))
            case 12:
                result = (SpellsNew.objects.filter(classes12__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes12')).order_by(f"classes{clsid}"))
            case 13:
                result = (SpellsNew.objects.filter(classes13__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes13')).order_by(f"classes{clsid}"))
            case 14:
                result = (SpellsNew.objects.filter(classes14__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes14')).order_by(f"classes{clsid}"))
            case 15:
                result = (SpellsNew.objects.filter(classes15__lt=255).filter(not_player_spell=0)
                          .annotate(level=F('classes15')).order_by(f"classes{clsid}"))
            case _:
                result = None
        spells = dict()
        if result is not None:
            for spell in result:
                spell_effects = prep_spell_data(spell)
                if spell.level in spells:
                    spells[spell.level].append({"spell": spell, "spell_effects": spell_effects})
                else:
                    spells[spell.level] = [{"spell": spell, "spell_effects": spell_effects}]
        return render(request=request,
                      template_name="spells/list.html",
                      context={"class_id": clsid,
                               "spells": spells},
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
                purchase_locations = spell['purchase_location_info'].split(';')
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

        # Calculate the minimum level for this spell for spell effect description and spell_min_duration purposes
        min_level = 65
        for i in range(1, 16):
            if getattr(spell_data, 'classes' + str(i)) < min_level:
                min_level = getattr(spell_data, 'classes' + str(i))

        spell_min_duration = calc_buff_duration(min_level, spell_data.buff_duration_formula, spell_data.buff_duration)
        spell_min_time = spell_min_duration * 6
        spell_max_duration = calc_buff_duration(65, spell_data.buff_duration_formula, spell_data.buff_duration)
        spell_max_time = spell_max_duration * 6

        # Extract slot_id, effect_id, base_value, max_value from spell data
        sp_effects = list()
        for slot_id in range(1, 13):
            if spell_data.__getattribute__(f'effectid{slot_id}') != 254:
                sp_effects.append(
                    (slot_id,
                     getattr(spell_data, f'effectid{slot_id}'),
                     getattr(spell_data, f'formula{slot_id}'),
                     getattr(spell_data, f'effect_base_value{slot_id}'),
                     getattr(spell_data, f'max{slot_id}'))
                )

        sp_effects = build_effect_descriptions(spell_data, sp_effects, spell_max_duration, min_level)
        items_with_effect = Items.objects.filter(Q(click_effect=spell_data.id) |
                                                 Q(worn_effect=spell_data.id) |
                                                 Q(proc_effect=spell_data.id))

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
                               "spell_min_duration": spell_min_duration,
                               "spell_min_time": spell_min_time,
                               "spell_max_duration": spell_max_duration,
                               "spell_max_time": spell_max_time,
                               "items_with_effect": items_with_effect,
                               },
                      )
