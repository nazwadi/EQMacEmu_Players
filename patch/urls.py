from django.urls import path

from . import views
from .feeds import LatestPatchesFeed

app_name = "patch"
urlpatterns = [
    path("", views.index, name="index"),
    path("view/<slug:slug>", views.view_patch_message, name="view"),
    path("view/<slug:slug>/raw/", views.patch_raw, name="raw"),
    path("export/json/", views.export_json, name="export_json"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("feed/", LatestPatchesFeed(), name="feed"),
]
