from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from quests.models import Quests
from quests.models import SERVER_MAX_LEVEL
from quests.forms import QuestSearchForm
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
    quest = Quests.objects.filter(id=quest_id).first()
    if not quest or (quest.status == 'draft' and not request.user.is_staff):
        return render(request=request,
                      context={
                          "quest_exists": False,
                          "quest_id": quest_id,
                      },
                      template_name="quests/view_quest.html")

    starting_npc = NPCTypes.objects.filter(id=quest.starting_npc_id).first()

    npc_ids = list(quest.related_npcs.values_list('npc_id', flat=True))
    related_npcs = list(NPCTypes.objects.filter(id__in=npc_ids))

    zone_ids = list(quest.related_zones.values_list('zone_id', flat=True))
    related_zones = list(Zone.objects.filter(zone_id_number__in=zone_ids))

    item_ids = list(quest.quest_items.values_list('item_id', flat=True))
    quest_items = list(Items.objects.filter(id__in=item_ids))

    quest_factions = quest.quest_factions.all()

    patch_history = quest.patch_history.select_related('patch').order_by('patch__patch_date')
    patch_introduced = patch_history.filter(role='introduced').first()
    patch_updates = patch_history.filter(role='updated')

    return render(request=request,
                  context={
                      "quest_exists": True,
                      "quest": quest,
                      'factions_required': quest_factions.filter(role='required'),
                      'factions_raised': quest_factions.filter(role='raised'),
                      'factions_lowered': quest_factions.filter(role='lowered'),
                      "default_max_level": SERVER_MAX_LEVEL,
                      "quest_items": quest_items,
                      "starting_npc": starting_npc,
                      "related_npcs": related_npcs,
                      "related_zones": related_zones,
                      "quest_chain": quest.get_quest_chain() if quest.prerequisite or quest.sequels.exists() else None,
                      "rewards": quest.get_all_rewards(),
                      "patch_introduced": patch_introduced,
                      "patch_updates": patch_updates,
                  },
                  template_name="quests/view_quest.html")


def search(request):
    form = QuestSearchForm()
    search_results = []

    if request.method == "POST":
        form = QuestSearchForm(request.POST)
        if form.is_valid():
            queryset = Quests.objects.all() if request.user.is_staff else Quests.objects.filter(status='published')
            cd = form.cleaned_data

            if cd.get('quest_name'):
                queryset = queryset.filter(name__icontains=cd['quest_name'])

            if cd.get('starting_zone'):
                queryset = queryset.filter(
                    Q(starting_zone__icontains=cd['starting_zone']) |
                    Q(related_zones__short_name__icontains=cd['starting_zone']) |
                    Q(related_zones__long_name__icontains=cd['starting_zone'])
                ).distinct()

            if cd.get('expansion') and cd['expansion'] != '-1':
                queryset = queryset.filter(expansion_introduced__lte=int(cd['expansion']))

            if cd.get('player_class') and cd['player_class'] != '-1':
                class_id = int(cd['player_class'])
                queryset = queryset.filter(Q(class_restrictions=-1) | Q(class_restrictions=class_id))

            if cd.get('player_race') and cd['player_race'] != '-1':
                race_id = int(cd['player_race'])
                queryset = queryset.filter(Q(race_restrictions=-1) | Q(race_restrictions=race_id))

            min_level = cd.get('min_level') or 1
            max_level = cd.get('max_level') or SERVER_MAX_LEVEL
            queryset = queryset.filter(
                Q(minimum_level__lte=max_level) &
                (Q(maximum_level=-1) | Q(maximum_level__gte=min_level))
            )

            limit = cd.get('query_limit') or 50
            search_results = list(queryset[:limit])

    return render(request,
                  template_name="quests/search_quest.html",
                  context={
                      "form": form,
                      "search_results": search_results,
                  })
