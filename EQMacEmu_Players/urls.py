"""
URL configuration for EQMacEmu Accounts project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "EQMacEmu Accounts Administration"

urlpatterns = [
    path(r"", include("accounts.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("characters/", include("characters.urls")),
    path("character_transfer/", include("character_transfer.urls")),
    path("factions/", include("factions.urls")),
    path("items/", include("items.urls")),
    path("npcs/", include("npcs.urls")),
    path("pets/", include("pets.urls")),
    path("recipes/", include("recipes.urls")),
    path("spells/", include("spells.urls")),
    path("zones/", include("zones.urls")),
]
