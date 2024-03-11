from django.urls import path

from . import views

app_name = "zones"
urlpatterns = [
    path("", views.index, name="index"),
    path("view/<str:short_name>", views.view_zone, name="view"),
    path("view/<int:zone_id>", views.view_zone, name="view"),
]
