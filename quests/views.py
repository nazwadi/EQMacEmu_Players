from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connections
from quests.models import Quests
from quests.models import SERVER_MAX_LEVEL
from common.models.npcs import NPCTypes
from common.models.zones import Zone
from common.models.items import Items

def view_quest(request, quest_id):
    """
    Defines view for https://url.tld/quests/view/<int:pk>

    :param request: Http request
    :param quest_id: a quest id field unique identifier
    :return: Http response
    """
    quest = Quests.objects.filter(id=quest_id).first()
    if quest:
        starting_npc = NPCTypes.objects.filter(id=quest.starting_npc_id).first()
        related_npcs = [NPCTypes.objects.get(id=npc.npc_id) for npc in quest.related_npcs.all() if quest.related_npcs]
        related_zones = [Zone.objects.get(zone_id_number=zone.zone_id) for zone in quest.related_zones.all() if quest.related_zones]
        quest_items = [Items.objects.get(id=quest_item.item_id) for quest_item in quest.quest_items.all() if quest.quest_items]
    else:
        return render(request=request,
                      context={"quest_exists": False },
                      template_name="quests/view_quest.html")
    return render(request=request,
                  context={
                      "quest_exists": True,
                      "quest": quest,
                      "default_max_level": SERVER_MAX_LEVEL,
                      "quest_items": quest_items,
                      "starting_npc": starting_npc,
                      "related_npcs": related_npcs,
                      "related_zones": related_zones,
                  },
                  template_name="quests/view_quest.html")
