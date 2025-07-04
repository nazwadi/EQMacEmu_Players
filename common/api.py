from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from common.models.items import Items
from common.models.npcs import NPCTypes
from common.models.spells import SpellsNew
from common.models.zones import Zone
from common.models.faction import FactionList
from common.models.tradeskill import TradeskillRecipe

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
        'icon': item.icon
    } for item in items]

    # NPCs search
    npcs = NPCTypes.objects.filter(name__icontains=query)[:8]
    results['npcs'] = [{
        'id': npc.id,
        'name': npc.name,
        'url': f'/npcs/view/{npc.id}',
        'level': npc.level
    } for npc in npcs]

    # Spells search
    spells = SpellsNew.objects.filter(name__icontains=query)[:8]
    results['spells'] = [{
        'id': spell.id,
        'name': spell.name,
        'url': f'/spells/view/{spell.id}',
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