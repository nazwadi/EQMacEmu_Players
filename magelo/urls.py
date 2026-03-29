from django.urls import path

from . import views

app_name = "magelo"
urlpatterns = [
    path("view/<str:character_name>", views.character_profile, name="character_profile"),
    path("keys/<str:character_name>", views.character_keys, name="keys"),
    path("aas/<str:character_name>", views.character_aas, name="aas"),
    path("flags/<str:character_name>", views.character_flags, name="flags"),
    path('update_permission/', views.update_permission, name='update_permission'),
    path('search/', views.search, name='search'),
    path('api/aa-description/<str:aa_name>/', views.magelo_aa_description_api, name='magelo_aa_description_api'),
    path('wishlist/add/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:entry_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('wishlist/<str:character_name>/', views.wishlist_view, name='wishlist'),
]
