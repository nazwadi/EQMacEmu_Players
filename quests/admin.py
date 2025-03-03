from django import forms
from django.contrib import admin
from django.db import models
from common.templatetags.expansion_filters import exp_filter
from django.urls import reverse
from django.utils.html import format_html

from common.models.npcs import NPCTypes
from quests.models import Quests
from quests.models import QuestCategory
from quests.models import QuestTag
from quests.models import QuestFactionRequired
from quests.models import QuestFactionRaised
from quests.models import QuestFactionLowered
from quests.models import QuestsRelatedNPC
from quests.models import QuestsRelatedZone
from quests.models import QuestItem
from quests.models import ItemReward
from quests.models import ExperienceReward
from quests.models import FactionReward
from quests.models import SkillReward
from quests.models import SpellReward
from quests.models import AAReward
from quests.models import AccessReward
from quests.models import TitleReward
from quests.models import CurrencyReward



from quests.models import SERVER_MAX_LEVEL


class QuestCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    list_display = ("name", "description")
    list_filter = ["name"]


class QuestTagAdmin(admin.ModelAdmin):
    pass


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
    classes = ['collapse']  # This makes the inline collapsed by default
    verbose_name = "Related NPC"
    verbose_name_plural = "Related NPCs"

    formfield_overrides = {
        models.ForeignKey: {'widget': NPCLookupWidget},
    }

    # Custom template for the inline to include a lookup button
    template = 'admin/edit_inline/tabular_with_npc_lookup.html'


class ItemRewardInline(admin.TabularInline):
    model = ItemReward
    extra = 1
    verbose_name = "Item Reward"
    verbose_name_plural = "Item Rewards"

class ExperienceRewardInline(admin.TabularInline):
    model = ExperienceReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "Experience Reward"
    verbose_name_plural = "Experience Rewards"

class CurrencyRewardInline(admin.TabularInline):
    model = CurrencyReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "Currency Reward"
    verbose_name_plural = "Currency Rewards"

class FactionRewardInline(admin.TabularInline):
    model = FactionReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "Faction Reward"
    verbose_name_plural = "Faction Rewards"

class SkillRewardInline(admin.TabularInline):
    model = SkillReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "Skill Reward"
    verbose_name_plural = "Skill Rewards"

class SpellRewardInline(admin.TabularInline):
    model = SpellReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "Spell Reward"
    verbose_name_plural = "Spell Rewards"

class TitleRewardInline(admin.TabularInline):
    model = TitleReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "Title Reward"
    verbose_name_plural = "Title Rewards"

class AARewardInline(admin.TabularInline):
    model = AAReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "AA Reward"
    verbose_name_plural = "AA Rewards"

class AccessRewardInline(admin.TabularInline):
    model = AccessReward
    classes = ['collapse']  # This makes the inline collapsed by default
    extra = 1
    verbose_name = "Access Reward"
    verbose_name_plural = "Access Rewards"

class QuestAdminForm(forms.ModelForm):

    class Meta:
        model = Quests
        fields = '__all__'
        exclude = ['quest_reward']  # Exclude the quest_reward field as we're using inlines
        widgets = {
            'starting_npc_id': NPCLookupWidget(),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add autocomplete widget for related NPCs
            if 'related_npcs' in self.fields:
                self.fields['related_npcs'].help_text = "Search for NPCs by name or ID"

class QuestsAdmin(admin.ModelAdmin):
    form = QuestAdminForm
    search_fields = ["id", "name"]
    list_display = ("name", "id", "get_expansion_introduced", "starting_zone")
    list_filter = ["name"]
    filter_horizontal = (
    "quest_items", "related_npcs", "related_zones", "factions_required", "factions_raised", "factions_lowered")
    readonly_fields = ("id",)

    # Use the inline for related NPCs
    inlines = [
        RelatedNPCInline,

        # All rewards
        ItemRewardInline,
        ExperienceRewardInline,
        CurrencyRewardInline,
        FactionRewardInline,
        SkillRewardInline,
        SpellRewardInline,
        TitleRewardInline,
        AARewardInline,
        AccessRewardInline,
    ]
    exclude = ('related_npcs',)  # Exclude the original field since we're using the inline

    fieldsets = (
        ("Summary Information", {
            "fields": ("id", "name", "starting_npc_id", "starting_zone", "expansion_introduced",
                       "minimum_level", "maximum_level")
        }),
        ("Availability", {
            "classes": ("collapse",),
            "description": f"Set restrictions to -1 to indicate no restrictions. (i.e. None). Setting Max Level to -1 will display the default Server Max Level, {SERVER_MAX_LEVEL}.",
            "fields": ("class_restrictions", "race_restrictions", "deity_restrictions", "is_repeatable",
                       "monster_mission"),
        }),
        ("Description", {
            "description": "Put the content of the quest page here (i.e. quest description, walkthrough, checklists, notes)",
            "fields": ("description",),
        }),
        ("Quest Items", {
            "classes": ("collapse",),
            "description": "Any items that are required for this quest.",
            "fields": ("quest_items",),
        }),
        ("Related Zones", {
            "classes": ("collapse",),
            "description": "Include any zones related to this quest or that contain things required for this quest.",
            "fields": ("related_zones",),
        }),
        ("Factions", {
            "classes": ("collapse",),
            "fields": ("factions_required", "factions_raised", "factions_lowered")
        }),
        ("Category and Tags", {
            "classes": ("collapse",),
            "description": "Provide category and tagging information.",
            "fields": ("category", "tags")
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
        js = ['admin/js/npc_lookup.js']


class ItemRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'item_name', 'item_id', 'quantity')
    search_fields = ['item_name', 'item_id', 'quest__name']
    list_filter = ['is_optional', 'reward_group', 'attuned']

class ExperienceRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'amount', 'is_percentage')
    search_fields = ['amount', 'is_percentage', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

class CurrencyRewardAdmin(admin.ModelAdmin):
    list_display = ('quest','platinum', 'gold', 'silver', 'copper')
    search_fields = ['platinum', 'gold', 'silver', 'copper', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

class FactionRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'faction_name', 'faction_id', 'amount')
    search_fields = ['faction_name', 'faction_id', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

class SkillRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'skill_name', 'skill_id', 'amount')
    search_fields = ['skill_name', 'skill_id', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

class SpellRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'spell_name', 'spell_id', 'spell_level')
    search_fields = ['spell_name', 'spell_id', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

class TitleRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'title_text', 'is_prefix')
    search_fields = ['title_text', 'is_prefix', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

class AARewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'aa_name', 'aa_id', 'aa_points')
    search_fields = ['aa_name', 'aa_id', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

class AccessRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'flag_name', 'flag_value', 'description')
    search_fields = ['flag_name', 'flag_value', 'quest__name']
    list_filter = ['is_optional', 'reward_group']

admin.site.register(Quests, QuestsAdmin)
admin.site.register(QuestCategory, QuestCategoryAdmin)
admin.site.register(QuestTag, QuestTagAdmin)
admin.site.register(QuestFactionRequired, QuestFactionRequiredAdmin)
admin.site.register(QuestFactionRaised, QuestFactionRaisedAdmin)
admin.site.register(QuestFactionLowered, QuestFactionLoweredAdmin)
admin.site.register(QuestsRelatedZone, QuestsRelatedZoneAdmin)
admin.site.register(QuestsRelatedNPC, QuestsRelatedNPCAdmin)
admin.site.register(QuestItem, QuestItemAdmin)

admin.site.register(ItemReward, ItemRewardAdmin)
admin.site.register(ExperienceReward, ExperienceRewardAdmin)
admin.site.register(CurrencyReward, CurrencyRewardAdmin)
admin.site.register(FactionReward, FactionRewardAdmin)
admin.site.register(SkillReward, SkillRewardAdmin)
admin.site.register(SpellReward, SpellRewardAdmin)
admin.site.register(TitleReward, TitleRewardAdmin)
admin.site.register(AAReward, AARewardAdmin)
admin.site.register(AccessReward, AccessRewardAdmin)
