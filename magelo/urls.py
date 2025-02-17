from django.urls import path

from . import views

app_name = "magelo"
urlpatterns = [
    path("view/<str:character_name>", views.character_profile, name="character_profile"),
    path('update_permission/', views.update_permission, name='update_permission'),
    path('search/', views.search, name='search'),
]
