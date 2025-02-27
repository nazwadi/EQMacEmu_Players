from django import forms
from django.contrib import admin
from django.db import models
from django_jsonform.forms.fields import JSONFormField
from common.templatetags.expansion_filters import exp_filter
from django.urls import reverse
from django.utils.html import format_html

from common.models.npcs import NPCTypes
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
    list_display = ("zone_id", "long_name", "short_name")
    search_fields = ["short_name", "long_name", "zone_id"]


class NPCLookupWidget(forms.TextInput):
    """Custom widget to add an NPC lookup button next to the NPC ID field"""

    def render(self, name, value, attrs=None, renderer=None):
        # Ensure attrs is a mutable dictionary
        attrs = attrs or {}

        # Render the original input field
        output = super().render(name, value, attrs, renderer)

        # Generate the lookup URL
        lookup_url = reverse('npc_lookup') + f'?target_id={attrs.get("id", "id_" + name)}'

        # Create the lookup button with updated CSS classes
        output += format_html(
            '<a href="{}" class="related-lookup lookup-btn" id="lookup_id_{}" '
            'onclick="event.stopPropagation(); window.open(this.href, \'npcPopup\', \'width=800,height=600\'); return false;" '
            'title="Look Up NPC">&nbsp;</a>',
            lookup_url, name
        )

        # Add a span to display the NPC name if an ID is provided
        if value:
            try:
                npc = NPCTypes.objects.get(id=value)
                output += format_html(
                    '<span class="npc-name-display" id="name_display_{}">{} ({})</span>',
                    attrs.get('id', 'id_' + name), npc.name, value
                )
            except NPCTypes.DoesNotExist:
                output += format_html(
                    '<span class="npc-name-not-found" id="name_display_{}">{}</span>',
                    attrs.get('id', 'id_' + name), 'NPC not found'
                )

        return output


class RelatedNPCAdminForm(forms.ModelForm):
    class Meta:
        model = QuestsRelatedNPC
        fields = '__all__'
        widgets = {
            'npc_id': NPCLookupWidget(),
        }


class QuestsRelatedNPCAdmin(admin.ModelAdmin):
    list_display = ("name", "npc_id")
    search_fields = ["name", "npc_id"]
    form = RelatedNPCAdminForm

    # Add a custom action to look up an NPC by ID
    def lookup_npc(self, request, queryset):
        # This is a placeholder - in a real implementation, you would
        # add a view that allows searching NPCs
        pass

    lookup_npc.short_description = "Look up NPC details"
    actions = ['lookup_npc']


class RelatedNPCInline(admin.TabularInline):
    model = Quests.related_npcs.through
    extra = 1
    verbose_name = "Related NPC"
    verbose_name_plural = "Related NPCs"

    formfield_overrides = {
        models.ForeignKey: {'widget': NPCLookupWidget},
    }


class QuestAdminForm(forms.ModelForm):
    quest_reward = JSONFormField(schema={
        'type': 'object',
        'properties': {
            'item_id': {'type': 'integer'},
            'item_name': {'type': 'string'},
            'exp': {'type': 'integer'},
            'faction': {'type': 'string'},
            'flag': {'type': 'string'},
        }
    },
        help_text=Quests._meta.get_field('quest_reward').help_text
    )

    class Meta:
        model = Quests
        fields = '__all__'
        widgets = {
            'starting_npc_id': NPCLookupWidget(),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add autocomplete widget for related NPCs
            if 'related_npcs' in self.fields:
                self.fields['related_npcs'].help_text = "Search for NPCs by name or ID"


class RelatedNPCInline(admin.TabularInline):
    model = Quests.related_npcs.through
    extra = 1
    verbose_name = "Related NPC"
    verbose_name_plural = "Related NPCs"

    # Custom template for the inline to include a lookup button
    template = 'admin/edit_inline/tabular_with_npc_lookup.html'


class QuestsAdmin(admin.ModelAdmin):
    form = QuestAdminForm
    search_fields = ["id", "name"]
    list_display = ("name", "id", "get_expansion_introduced", "starting_zone")
    list_filter = ["name"]
    filter_horizontal = (
    "quest_items", "related_npcs", "related_zones", "factions_required", "factions_raised", "factions_lowered")
    readonly_fields = ("id",)

    # Use the inline for related NPCs
    inlines = [RelatedNPCInline]
    exclude = ('related_npcs',)  # Exclude the original field since we're using the inline

    fieldsets = (
        ("Where to Begin", {
            "fields": ("id", "name", "starting_npc_id", "starting_zone", "quest_reward")
        }),
        ("Availability", {
            "classes": ("collapse",),
            "description": f"Set restrictions to -1 to indicate no restrictions. (i.e. None). Setting Max Level to -1 will display the default Server Max Level, {SERVER_MAX_LEVEL}.",
            "fields": ("expansion_introduced", "minimum_level", "maximum_level", "class_restrictions",
                       "race_restrictions", "deity_restrictions", "is_repeatable", "monster_mission"),
        }),
        ("Description", {
            "description": "Put the content of the quest page here (i.e. quest description, walkthrough, checklists, notes)",
            "fields": ("description",),
        }),
        ("Quest Items", {
            "description": "Any items that are required for this quest.",
            "fields": ("quest_items",),
        }),
        ("Related Zones", {
            "description": "Include any zones related to this quest or that contain things required for this quest.",
            "fields": ("related_zones",),
        }),
        # ("Related NPCs", {
        #     "description": "Include any npcs involved directly in quest dialogues or that drop quest items, etc...",
        #     "fields": ("related_npcs",),
        # }),
        ("Factions", {
            "classes": ("collapse",),
            "fields": ("factions_required", "factions_raised", "factions_lowered")
        }),
    )

    def get_starting_npc(self, obj):
        return obj.starting_npc_id

    get_starting_npc.short_description = "Quest Giver"

    def get_starting_npc_name(self, obj):
        try:
            npc = NPCTypes.objects.get(id=obj.starting_npc_id)
            return f"{npc.name} ({obj.starting_npc_id})"
        except NPCTypes.DoesNotExist:
            return f"Unknown ({obj.starting_npc_id})"

    get_starting_npc_name.short_description = "Quest Giver"

    def get_expansion_introduced(self, obj):
        return exp_filter(obj.expansion_introduced)

    get_expansion_introduced.short_description = "Expansion Introduced"

    class Media:
        js = ('admin/js/npc_lookup.js',)


admin.site.register(Quests, QuestsAdmin)
admin.site.register(QuestFactionRequired, QuestFactionRequiredAdmin)
admin.site.register(QuestFactionRaised, QuestFactionRaisedAdmin)
admin.site.register(QuestFactionLowered, QuestFactionLoweredAdmin)
admin.site.register(QuestsRelatedZone, QuestsRelatedZoneAdmin)
admin.site.register(QuestsRelatedNPC, QuestsRelatedNPCAdmin)
admin.site.register(QuestItem, QuestItemAdmin)
