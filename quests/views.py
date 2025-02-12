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

        related_npcs = []
        if quest.related_npcs.exists():
            related_npcs = [NPCTypes.objects.filter(id=npc.npc_id).first() for npc in quest.related_npcs.all()]
            related_npcs = [npc for npc in related_npcs if npc]  # Remove None values

        related_zones = []
        if quest.related_zones.exists():
            related_zones = [Zone.objects.filter(zone_id_number=zone.zone_id).first() for zone in quest.related_zones.all()]
            related_zones = [zone for zone in related_zones if zone]  # Remove None values

        quest_items = []
        if quest.quest_items.exists():
            quest_items = [Items.objects.filter(id=quest_item.item_id).first() for quest_item in quest.quest_items.all()]
            quest_items = [item for item in quest_items if item]  # Remove None values
    else:
        return render(request=request,
                      context={"quest_exists": False},
                      template_name="quests/view_quest.html")

    return render(request=request,
                  context={
                      "quest_exists": True,
                      "quest": quest,
                      'factions_required': quest.factions_required.all() or [],
                      'factions_raised': quest.factions_raised.all() or [],
                      'factions_lowered': quest.factions_lowered.all() or [],
                      "default_max_level": SERVER_MAX_LEVEL,
                      "quest_items": quest_items,
                      "starting_npc": starting_npc,
                      "related_npcs": related_npcs,
                      "related_zones": related_zones,
                  },
                  template_name="quests/view_quest.html")
