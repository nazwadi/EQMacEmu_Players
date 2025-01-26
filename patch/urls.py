from django.urls import path

from . import views

app_name = "factions"
urlpatterns = [
    path("", views.index_request, name="index"),
    path("search", views.search, name="search"),
    path("view/<int:faction_id>", views.view_faction, name="view"),
]
