from django.contrib import admin

from spells.models import SpellExpansion

@admin.register(SpellExpansion)
class SpellExpansionAdmin(admin.ModelAdmin):
    list_display = ('id', 'expansion', 'spell_name_display')
    list_filter = ('expansion',)
    search_fields = ('id',)

    def spell_name_display(self, obj):
        # You could potentially query the SpellsNew model here
        # if you set up a database router or connection
        return f"Spell ID: {obj.id}"
    spell_name_display.short_description = 'Spell'
