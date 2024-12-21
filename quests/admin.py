from django.contrib import admin
from common.templatetags.expansion_filters import exp_filter

from quests.models import Quests
from quests.models import QuestFactionRequired
from quests.models import QuestFactionRaised
from quests.models import QuestFactionLowered
from quests.models import QuestsRelatedNPC
from quests.models import QuestsRelatedZone
from quests.models import QuestItem
from quests.models import SERVER_MAX_LEVEL

class QuestFactionRequiredAdmin(admin.ModelAdmin):
    pass

class QuestFactionRaisedAdmin(admin.ModelAdmin):
    pass

class QuestFactionLoweredAdmin(admin.ModelAdmin):
    pass

class QuestItemAdmin(admin.ModelAdmin):
    pass

class QuestsRelatedZoneAdmin(admin.ModelAdmin):
    pass

class QuestsRelatedNPCAdmin(admin.ModelAdmin):
    pass

class QuestsAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]
    list_display = ("name", "id", "get_expansion_introduced", "starting_zone")
    list_filter = ["name"]
    filter_horizontal = ("quest_items", "related_npcs", "related_zones", "factions_required", "factions_raised", "factions_lowered")
    readonly_fields = ("id",)
    fieldsets = (
        ("Quick Facts", {
            "fields": ("id", "name", "starting_npc_id", "starting_zone", "expansion_introduced")
        }),
        ("Description", {
            "description": "Put the content of the quest page here (i.e. quest description, walkthrough, checklists, notes)",
            "fields": ("description",),
        }),
        ("Related NPCs", {
            "description": "Include any npcs involved directly in quest dialogues or that drop quest items, etc...",
            "fields": ("related_npcs",),
        }),
        ("Related Zones", {
            "description": "Include any zones related to this quest or that contain things required for this quest.",
            "fields": ("related_zones",),
        }),
        ("Quest Items", {
            "description": "Any items that are required for this quest.",
            "fields": ("quest_items",),
        }),
        ("Factions", {
            "classes": ("collapse",),
            "fields": ("factions_required", "factions_raised", "factions_lowered")
        }),
        ("Restrictions", {
            "classes": ("collapse",),
            "description": "Set these to -1 to indicate no restrictions. (i.e. None)",
            "fields": ("class_restrictions", "race_restrictions", "deity_restrictions"),
        }),
        ("Advanced Settings", {
            "classes": ("collapse",),
            "description": f"Setting Max Level to -1 will display the default Server Max Level, {SERVER_MAX_LEVEL}.",
            "fields": ("minimum_level", "maximum_level", "is_repeatable", "monster_mission"),
        }),
    )

    def get_starting_npc(self, obj):
        return obj.starting_npc_id
    get_starting_npc.short_description = "Quest Giver"

    def get_expansion_introduced(self, obj):
        return exp_filter(obj.expansion_introduced)
    get_expansion_introduced.short_description = "Expansion Introduced"

admin.site.register(Quests, QuestsAdmin)
admin.site.register(QuestFactionRequired, QuestFactionRequiredAdmin)
admin.site.register(QuestFactionRaised, QuestFactionRaisedAdmin)
admin.site.register(QuestFactionLowered, QuestFactionLoweredAdmin)
admin.site.register(QuestsRelatedZone, QuestsRelatedZoneAdmin)
admin.site.register(QuestsRelatedNPC, QuestsRelatedNPCAdmin)
admin.site.register(QuestItem, QuestItemAdmin)
