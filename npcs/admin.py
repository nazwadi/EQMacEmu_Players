from django.contrib import admin
from npcs.models import NpcPage, NPCPatchHistory


class NpcPageAdmin(admin.ModelAdmin):
    search_fields = ["npc_id"]
    list_display = ["npc_id", "description"]
    list_filter = ["npc_id"]


@admin.register(NPCPatchHistory)
class NPCPatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['npc_name', 'npc_id', 'patch', 'role']
    list_filter = ['role']
    search_fields = ['npc_name', 'npc_id']
    autocomplete_fields = ['patch']
    ordering = ['patch__patch_date']


admin.site.register(NpcPage, NpcPageAdmin)
