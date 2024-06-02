from django.urls import path

from . import views

app_name = "spells"
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("list/<int:class_id>", views.list_spells, name="list"),
    path("buy/<int:class_id>", views.buy_spells, name="buy"),
    path("view/<int:spell_id>", views.view_spell, name="view"),
]
