from django.urls import path

from . import views

app_name = "npcs"
urlpatterns = [
    path("search", views.search, name="search"),
    path("view/<int:item_id>", views.view_item, name="view"),
]
