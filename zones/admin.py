from django.contrib import admin
from .models import ZonePage


class ZonePageAdmin(admin.ModelAdmin):
    search_fields = ["id", "short_name"]
    list_display = ["short_name", ]
    list_filter = ["short_name"]


admin.site.register(ZonePage, ZonePageAdmin)
