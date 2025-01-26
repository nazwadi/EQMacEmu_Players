from django.urls import path

from . import views

app_name = "patch"
urlpatterns = [
    path("", views.index, name="index"),
    path("view/<slug:slug>", views.view_patch_message, name="view"),
]
