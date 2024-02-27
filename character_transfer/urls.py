from django.urls import path

from . import views

app_name = "character_transfer"
urlpatterns = [
    path("", views.index, name="index"),
]
