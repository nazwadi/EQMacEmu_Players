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
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.site.site_header = "EQMacEmu Accounts Administration"

urlpatterns = [
    path(r"", lambda request: redirect("/accounts/")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("characters/", include("characters.urls")),
    path("character_transfer/", include("character_transfer.urls")),
    path("factions/", include("factions.urls")),
    path("items/", include("items.urls")),
    path("npcs/", include("npcs.urls")),
    path("pets/", include("pets.urls")),
    path("quests/", include("quests.urls")),
    path("recipes/", include("recipes.urls")),
    path("spells/", include("spells.urls")),
    path("zones/", include("zones.urls")),
    path("mdeditor/", include('mdeditor.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += staticfiles_urlpatterns()
