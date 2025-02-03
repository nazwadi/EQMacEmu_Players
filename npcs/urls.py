from django.urls import path

from . import views

app_name = "npcs"
urlpatterns = [
    path("", views.index_request, name="index"),
    path("search", views.search, name="search"),
    path("view/<int:npc_id>", views.view_npc, name="view"),
    path("api/special-ability/<str:ability_name>", views.npc_special_abilities_api, name="npc_special_ability_api"),
]
