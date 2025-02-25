from django.shortcuts import render, redirect
from django.contrib import messages
from quests.models import Quests
from quests.models import SERVER_MAX_LEVEL
from common.models.zones import Zone
from common.models.items import Items
from django.views.generic import ListView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from common.models.npcs import NPCTypes


@method_decorator(staff_member_required, name='dispatch')
class NPCLookupView(ListView):
    """
    Used by the admin interface when adding related NPCs
    """
    model = NPCTypes
    template_name = 'admin/npc_lookup.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = NPCTypes.objects.all().order_by('name')
        search_term = self.request.GET.get('q', '')

        if search_term:
            # Try to match by ID or name
            try:
                npc_id = int(search_term)
                id_matches = NPCTypes.objects.filter(id=npc_id)
                if id_matches.exists():
                    return id_matches
            except ValueError:
                pass

            # Search by name
            return queryset.filter(name__icontains=search_term)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('q', '')
        context['target_id'] = self.request.GET.get('target_id', '')
        return context

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
                      context={
                          "quest_exists": False,
                          "quest_id": quest_id,
                      },
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
