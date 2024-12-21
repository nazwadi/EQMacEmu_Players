from django.urls import path

from . import views

app_name = "quests"
urlpatterns = [
    path("view/<int:quest_id>", views.view_quest, name="view"),
]
