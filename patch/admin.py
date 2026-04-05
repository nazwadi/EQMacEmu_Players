from django.contrib import admin

from .models import PatchMessage, Comment, PatchTag
from quests.models import QuestPatchHistory
from npcs.models import NPCPatchHistory
from items.models import ItemPatchHistory
from spells.models import SpellPatchHistory
from zones.models import ZonePatchHistory


class PatchTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class QuestPatchHistoryInline(admin.TabularInline):
    model = QuestPatchHistory
    extra = 0
    fields = ('quest', 'role', 'notes')
    autocomplete_fields = ['quest']
    verbose_name = "Quest"
    verbose_name_plural = "Quests"


class NPCPatchHistoryInline(admin.TabularInline):
    model = NPCPatchHistory
    extra = 0
    fields = ('npc_id', 'npc_name', 'role', 'notes')
    verbose_name = "NPC"
    verbose_name_plural = "NPCs"


class ItemPatchHistoryInline(admin.TabularInline):
    model = ItemPatchHistory
    extra = 0
    fields = ('item_id', 'item_name', 'role', 'notes')
    verbose_name = "Item"
    verbose_name_plural = "Items"


class SpellPatchHistoryInline(admin.TabularInline):
    model = SpellPatchHistory
    extra = 0
    fields = ('spell_id', 'spell_name', 'role', 'notes')
    verbose_name = "Spell"
    verbose_name_plural = "Spells"


class ZonePatchHistoryInline(admin.TabularInline):
    model = ZonePatchHistory
    extra = 0
    fields = ('zone_short_name', 'zone_long_name', 'role', 'notes')
    verbose_name = "Zone"
    verbose_name_plural = "Zones"


class PatchMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "patch_date", "patch_type", "expansion", "markdown_edited", "short_description")
    list_filter = ("patch_type", "expansion", "markdown_edited", "patch_year", "tags")
    search_fields = ["title", "body_plaintext"]
    prepopulated_fields = {"slug": ("title", "patch_number_this_date")}
    readonly_fields = ("markdown_edited",)
    filter_horizontal = ("tags",)
    inlines = [QuestPatchHistoryInline, NPCPatchHistoryInline, ItemPatchHistoryInline, SpellPatchHistoryInline, ZonePatchHistoryInline]

    def save_model(self, request, obj, form, change):
        if 'body_markdown' in form.changed_data:
            obj.markdown_edited = True
        super().save_model(request, obj, form, change)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'body', 'patch_message', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('username', 'body')
    actions = ['approve_comments']

    @staticmethod
    def approve_comments(self, request, queryset):
        queryset.update(active=True)


admin.site.register(PatchMessage, PatchMessageAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PatchTag, PatchTagAdmin)
