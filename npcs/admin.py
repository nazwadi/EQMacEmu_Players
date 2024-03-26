from django.contrib import admin
from npcs.models import NpcPage


class NpcPageAdmin(admin.ModelAdmin):
    search_fields = ["npc_id"]
    list_display = ["npc_id", "description"]
    list_filter = ["npc_id"]


admin.site.register(NpcPage, NpcPageAdmin)
