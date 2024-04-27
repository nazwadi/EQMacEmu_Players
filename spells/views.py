from django.shortcuts import render, redirect
from django.db import connections


def index(request):
    """
    Index page for spells
    :param request:
    :return: an Http Response object
    """
    if request.method == "GET":
        return redirect(search)


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


def view_spell(request, spell_id):
    """
    Defines view for https://url.tld/spells/view/<int:pk>

    :param request: Http request
    :param spell_id: a spell id field unique identifier
    :return: Http response
    """
    if request.method == "GET":
        return render(request=request,
                      template_name="spells/view_spell.html",
                      context={},
                      )
