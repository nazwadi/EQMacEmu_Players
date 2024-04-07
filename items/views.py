from django.shortcuts import render, redirect
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist

from common.models.items import Items
from common.utils import calculate_item_price
from collections import namedtuple


def search(request):
    """
    Search for an item by name

    :param request: Http request
    :return: Http response
    """
    if request.method == "GET":
        return render(request=request,
                      template_name="items/search_item.html")

    return render(request=request,
                  template_name="npcs/search_npc.html",
                  context={"search_results": search_results,
                           "level_range": range(100)})


def view_item(request, item_id):
    """
    Defines view for https://url.tld/npcs/view/<int:pk>

    :param request: Http request
    :param npc_id: a NPCTypes id field unique identifier
    :return: Http response
    """
    return render(request=request,
                  template_name="npcs/view_npc.html",
                  context={
                           "zone": zone,
                  })
