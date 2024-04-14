from django.shortcuts import render, redirect

from common.models.tradeskill import TradeskillRecipe
from common.models.tradeskill import TradeskillRecipeEntries


def index(request):
    """
    Placeholder
    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request=request,
                      template_name="recipes/search_recipe.html")


def search(request):
    """
    Search for a recipe by name

    :param request: Http request
    :return: Http response
    """
    tradeskill_options = {
        59: "Alchemy",
        60: "Baking",
        63: "Blacksmithing",
        65: "Brewing",
        55: "Fishing",
        64: "Fletching",
        68: "Jewelry Making",
        56: "Make Poison",
        69: "Pottery",
        58: "Research",
        57: "Tinkering",
        61: "Tailoring",
        75: "Quest Combine",
    }
    if request.method == "GET":
        return render(request=request,
                      template_name="recipes/search_recipe.html",
                      context={
                          "tradeskill_options": tradeskill_options,
                      })

    if request.method == "POST":
        recipe_name = request.POST.get("recipe_name")
        tradeskill = request.POST.get("tradeskill")
        min_trivial = request.POST.get("min_trivial")
        max_trivial = request.POST.get("max_trivial")
        if tradeskill == "-1":  # any tradeskill
            results = (TradeskillRecipe.objects.filter(name__icontains=recipe_name)
                       .filter(trivial__gte=min_trivial).filter(trivial__lte=max_trivial))
        else:
            results = (TradeskillRecipe.objects.filter(name__icontains=recipe_name).filter(tradeskill=tradeskill)
                       .filter(trivial__gte=min_trivial).filter(trivial__lte=max_trivial))

        search_results = list()
        for result in results:
            recipe_entries = TradeskillRecipeEntries.objects.filter(recipe_id=result.id).order_by("-success_count")
            search_results.append((result, recipe_entries))

        return render(request=request,
                      context={
                          "tradeskill_options": tradeskill_options,
                          "search_results": search_results
                      },
                      template_name="recipes/search_recipe.html")


def view_recipe(request, recipe_id):
    """
    Defines view for https://url.tld/recipes/view/<int:pk>

    :param request: Http request
    :param recipe_id: a tradeskill_recipes id field unique identifier
    :return: Http response
    """
    tradeskill_recipe = TradeskillRecipe.objects.get(id=recipe_id)
    tradeskill_recipe_entries = TradeskillRecipeEntries.objects.filter(recipe_id=recipe_id).order_by("-component_count")
    return render(request=request,
                  context={
                      "tradeskill_recipe": tradeskill_recipe,
                      "tradeskill_recipe_entries": tradeskill_recipe_entries,
                  },
                  template_name="recipes/view_recipe.html")
