from django.contrib import admin
from .models import ZonePage, ZonePatchHistory


class ZonePageAdmin(admin.ModelAdmin):
    search_fields = ["id", "short_name"]
    list_display = ["short_name"]
    list_filter = ["short_name"]


@admin.register(ZonePatchHistory)
class ZonePatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['zone_long_name', 'zone_short_name', 'patch', 'role']
    list_filter = ['role']
    search_fields = ['zone_long_name', 'zone_short_name']
    autocomplete_fields = ['patch']
    ordering = ['patch__patch_date']


admin.site.register(ZonePage, ZonePageAdmin)
