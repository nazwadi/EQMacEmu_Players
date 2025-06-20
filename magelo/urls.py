from django.urls import path

from . import views

app_name = "magelo"
urlpatterns = [
    path("view/<str:character_name>", views.character_profile, name="character_profile"),
    path("keys/<str:character_name>", views.character_keys, name="keys"),
    path("aas/<str:character_name>", views.character_aas, name="aas"),
    path('update_permission/', views.update_permission, name='update_permission'),
    path('search/', views.search, name='search'),
]
