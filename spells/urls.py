from django.urls import path

from . import views

app_name = "spells"
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("view/<int:spell_id>", views.view_spell, name="view"),
]
