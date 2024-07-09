from django.urls import path

from . import views

app_name = "pets"
urlpatterns = [
    path("view/<str:pet_name>", views.view_pet, name="view"),
    path("list", views.list_pets, name="list"),
    path("list/<int:pet_class_id>", views.list_pets, name="list"),
]