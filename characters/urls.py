from django.urls import path

from . import views

app_name = "characters"
urlpatterns = [
    path("", views.index_request, name="index"),
    path("exp", views.experience, name="exp"),
    path("exp/<int:race_id>", views.experience, name="exp"),
    path("list/<str:game_account_name>", views.list_characters, name="list"),
    path("view/<str:character_name>", views.view_character, name="view"),
]
