from django.contrib import admin

from spells.models import SpellExpansion, SpellPatchHistory


@admin.register(SpellExpansion)
class SpellExpansionAdmin(admin.ModelAdmin):
    list_display = ('id', 'expansion', 'spell_name_display')
    list_filter = ('expansion',)
    search_fields = ('id',)

    def spell_name_display(self, obj):
        return f"Spell ID: {obj.id}"
    spell_name_display.short_description = 'Spell'


@admin.register(SpellPatchHistory)
class SpellPatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['spell_name', 'spell_id', 'patch', 'role']
    list_filter = ['role']
    search_fields = ['spell_name', 'spell_id']
    autocomplete_fields = ['patch']
    ordering = ['patch__patch_date']
