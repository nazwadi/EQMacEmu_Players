from django.urls import path

from . import views

app_name = "quests"
urlpatterns = [
    path("", views.search, name="index"),
    path("search", views.search, name="search"),
    path("view/<int:quest_id>", views.view_quest, name="view"),
]
