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
from quests.models import QuestFaction
from quests.models import QuestIssueReport
from quests.models import QuestPatchHistory
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
from quests.models import QUEST_STATUS_CHOICES


class QuestCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    list_display = ("name", "description")
    list_filter = ["name"]


class QuestTagAdmin(admin.ModelAdmin):
    pass


class QuestItemAdmin(admin.ModelAdmin):
    list_display = ("name", "item_id")
    search_fields = ["name", "item_id"]


class QuestsRelatedZoneAdmin(admin.ModelAdmin):
    list_display = ("zone_id", "long_name", "short_name")
    search_fields = ["short_name", "long_name", "zone_id"]


class NPCLookupWidget(forms.TextInput):
    """Custom widget to add an NPC lookup button next to the NPC ID field"""

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        output = super().render(name, value, attrs, renderer)
        lookup_url = reverse('npc_lookup') + f'?target_id={attrs.get("id", "id_" + name)}'
        output += format_html(
            '<a href="{}" class="related-lookup lookup-btn" id="lookup_id_{}" '
            'onclick="event.stopPropagation(); window.open(this.href, \'npcPopup\', \'width=800,height=600\'); return false;" '
            'title="Look Up NPC">&nbsp;</a>',
            lookup_url, name
        )
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


# class QuestsRelatedNPCAdmin(admin.ModelAdmin):
#     list_display = ("name", "npc_id")
#     search_fields = ["name", "npc_id"]
#     form = RelatedNPCAdminForm
#
#     def lookup_npc(self, request, queryset):
#         pass
#
#     lookup_npc.short_description = "Look up NPC details"
#     actions = ['lookup_npc']
#
#
# class RelatedNPCInline(admin.TabularInline):
#     model = Quests.related_npcs.through
#     extra = 1
#     classes = ['collapse']
#     verbose_name = "Related NPC"
#     verbose_name_plural = "Related NPCs"
#     formfield_overrides = {
#         models.ForeignKey: {'widget': NPCLookupWidget},
#     }
#     template = 'admin/edit_inline/tabular_with_npc_lookup.html'


class QuestFactionInline(admin.TabularInline):
    model = QuestFaction
    extra = 1
    classes = ['collapse']
    verbose_name = "Faction"
    verbose_name_plural = "Factions"


class QuestPatchHistoryInline(admin.TabularInline):
    model = QuestPatchHistory
    extra = 1
    classes = ['collapse']
    verbose_name = "Patch History Entry"
    verbose_name_plural = "Patch History"
    autocomplete_fields = ['patch']
    fields = ('patch', 'role', 'notes')


class ItemRewardInline(admin.TabularInline):
    model = ItemReward
    extra = 1
    verbose_name = "Item Reward"
    verbose_name_plural = "Item Rewards"


class ExperienceRewardInline(admin.TabularInline):
    model = ExperienceReward
    classes = ['collapse']
    extra = 1
    verbose_name = "Experience Reward"
    verbose_name_plural = "Experience Rewards"


class CurrencyRewardInline(admin.TabularInline):
    model = CurrencyReward
    classes = ['collapse']
    extra = 1
    verbose_name = "Currency Reward"
    verbose_name_plural = "Currency Rewards"


class FactionRewardInline(admin.TabularInline):
    model = FactionReward
    classes = ['collapse']
    extra = 1
    verbose_name = "Faction Reward"
    verbose_name_plural = "Faction Rewards"


class SkillRewardInline(admin.TabularInline):
    model = SkillReward
    classes = ['collapse']
    extra = 1
    verbose_name = "Skill Reward"
    verbose_name_plural = "Skill Rewards"


class SpellRewardInline(admin.TabularInline):
    model = SpellReward
    classes = ['collapse']
    extra = 1
    verbose_name = "Spell Reward"
    verbose_name_plural = "Spell Rewards"


class TitleRewardInline(admin.TabularInline):
    model = TitleReward
    classes = ['collapse']
    extra = 1
    verbose_name = "Title Reward"
    verbose_name_plural = "Title Rewards"


class AARewardInline(admin.TabularInline):
    model = AAReward
    classes = ['collapse']
    extra = 1
    verbose_name = "AA Reward"
    verbose_name_plural = "AA Rewards"


class AccessRewardInline(admin.TabularInline):
    model = AccessReward
    classes = ['collapse']
    extra = 1
    verbose_name = "Access Reward"
    verbose_name_plural = "Access Rewards"


class QuestAdminForm(forms.ModelForm):
    class Meta:
        model = Quests
        fields = '__all__'
        widgets = {
            'starting_npc_id': NPCLookupWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'related_npcs' in self.fields:
            self.fields['related_npcs'].help_text = "Search for NPCs by name or ID"


class QuestsAdmin(admin.ModelAdmin):
    form = QuestAdminForm
    search_fields = ["id", "name"]
    list_display = ("name", "id", "status", "get_expansion_introduced", "starting_zone", "updated_at")
    list_filter = ["status", "expansion_introduced", "starting_zone"]
    filter_horizontal = ("quest_items", "related_npcs", "related_zones")
    readonly_fields = ("id", "created_at", "updated_at")
    actions = ["publish_quests", "unpublish_quests"]

    inlines = [
        # RelatedNPCInline,
        QuestPatchHistoryInline,
        QuestFactionInline,
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
    exclude = ('related_npcs',)

    fieldsets = (
        ("Publishing", {
            "fields": ("status",),
            "description": "Drafts are only visible to staff. Publish when the quest content is ready.",
        }),
        ("Summary Information", {
            "fields": ("id", "name", "starting_npc_id", "starting_zone", "expansion_introduced",
                       "minimum_level", "maximum_level")
        }),
        ("Quest Chain", {
            "classes": ("collapse",),
            "description": "Link this quest to a prerequisite quest to form a quest chain.",
            "fields": ("prerequisite",),
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
        ("Category and Tags", {
            "classes": ("collapse",),
            "description": "Provide category and tagging information.",
            "fields": ("difficulty_rating", "estimated_time", "category", "tags")
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.action(description="Publish selected quests")
    def publish_quests(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f"{updated} quest(s) published.")

    @admin.action(description="Unpublish selected quests (revert to draft)")
    def unpublish_quests(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f"{updated} quest(s) reverted to draft.")

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


class QuestFactionAdmin(admin.ModelAdmin):
    list_display = ('quest', 'name', 'faction_id', 'role')
    search_fields = ['name', 'faction_id', 'quest__name']
    list_filter = ['role']


class ItemRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'item_name', 'item_id', 'quantity')
    search_fields = ['item_name', 'item_id', 'quest__name']
    list_filter = ['is_optional', 'reward_group', 'attuned']


class ExperienceRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'amount', 'is_percentage')
    search_fields = ['amount', 'is_percentage', 'quest__name']
    list_filter = ['is_optional', 'reward_group']


class CurrencyRewardAdmin(admin.ModelAdmin):
    list_display = ('quest', 'platinum', 'gold', 'silver', 'copper')
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


class QuestIssueReportAdmin(admin.ModelAdmin):
    list_display = ('quest', 'reporter_name', 'created_at', 'status', 'short_body')
    list_filter = ['status']
    search_fields = ['quest__name', 'reporter_name', 'body']
    readonly_fields = ('quest', 'reporter_name', 'body', 'created_at')
    actions = ['mark_resolved']

    @admin.display(description='Report')
    def short_body(self, obj):
        return obj.body[:80] + '…' if len(obj.body) > 80 else obj.body

    @admin.action(description='Mark selected reports as resolved')
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} report(s) marked as resolved.")


admin.site.register(Quests, QuestsAdmin)
admin.site.register(QuestCategory, QuestCategoryAdmin)
admin.site.register(QuestTag, QuestTagAdmin)
admin.site.register(QuestFaction, QuestFactionAdmin)
admin.site.register(QuestsRelatedZone, QuestsRelatedZoneAdmin)
# admin.site.register(QuestsRelatedNPC, QuestsRelatedNPCAdmin)
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
admin.site.register(QuestIssueReport, QuestIssueReportAdmin)
