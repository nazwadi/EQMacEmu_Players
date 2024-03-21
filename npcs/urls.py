from django.urls import path

from . import views

app_name = "npcs"
urlpatterns = [
    path("", views.index_request, name="index"),
    path("list/<str:name>", views.list_npcs, name="list"),
    path("view/<int:npc_id>", views.view_npc, name="view"),
]
