from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from common.models.items import Items
from common.models.npcs import NPCTypes
from common.models.spells import SpellsNew
from common.models.zones import Zone
from common.models.faction import FactionList
from common.models.tradeskill import TradeskillRecipe
from characters.templatetags import data_utilities
from npcs.templatetags import npc_filters

@require_http_methods(["GET"])
def api_search(request):
    query = request.GET.get('q', '').strip()

    # Minimum 3 characters to protect database
    if len(query) < 3:
        return JsonResponse({'results': {}})

    # Search each category with LIMIT for performance
    results = {
        'items': [],
        'npcs': [],
        'spells': [],
        'zones': [],
        'factions': [],
        'recipes': []
    }

    # Items search
    items = Items.objects.filter(Name__icontains=query)[:8]
    results['items'] = [{
        'id': item.id,
        'name': item.Name,
        'url': f'/items/view/{item.id}',
        'icon': item.icon,
        'icon_url': f'/static/images/items/item_{item.icon}.png',
    } for item in items]

    # NPCs search with space/underscore handling
    query_with_underscores = query.replace(' ', '_')
    query_with_spaces = query.replace('_', ' ')

    npcs = NPCTypes.objects.filter(
        Q(name__icontains=query) |
        Q(name__icontains=query_with_underscores) |
        Q(name__icontains=query_with_spaces)
    ).distinct()[:8]

    results['npcs'] = [{
        'id': npc.id,
        'name': npc.name.replace('_', ' '),
        'url': f'/npcs/view/{npc.id}',
        'level': npc.level,
        'race': data_utilities.npc_race(npc.race),
        'class': data_utilities.npc_class(npc.class_name),
        'body_type': npc_filters.body_type(npc.bodytype),
        'hp': npc.hp,
        'MR': npc.MR
    } for npc in npcs]

    # Spells search
    spells = SpellsNew.objects.filter(name__icontains=query)[:8]
    results['spells'] = [{
        'id': spell.id,
        'name': spell.name,
        'url': f'/spells/view/{spell.id}',
        'custom_icon': spell.custom_icon,
        'mana': spell.mana
    } for spell in spells]

    # Zones search - using short_name for URL since that's what your pattern suggests
    zones = Zone.objects.filter(long_name__icontains=query)[:8]
    results['zones'] = [{
        'id': zone.id,
        'name': zone.long_name,
        'url': f'/zones/view/{zone.short_name}',
        'short_name': zone.short_name
    } for zone in zones]

    # Factions search
    factions = FactionList.objects.filter(name__icontains=query)[:8]
    results['factions'] = [{
        'id': faction.id,
        'name': faction.name,
        'url': f'/factions/view/{faction.id}'
    } for faction in factions]

    # Recipes search
    recipes = TradeskillRecipe.objects.filter(name__icontains=query)[:8]
    results['recipes'] = [{
        'id': recipe.id,
        'name': recipe.name,
        'url': f'/recipes/view/{recipe.id}',
        'tradeskill': recipe.tradeskill
    } for recipe in recipes]

    return JsonResponse({'results': results})