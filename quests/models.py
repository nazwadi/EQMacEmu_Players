from django.db import models
from django.core.validators import MinValueValidator
from mdeditor.fields import MDTextField
from common.constants import ZONE_SHORT_TO_LONG
from quests.managers import QuestManager

SERVER_MAX_LEVEL = 60

EXPANSION_INTRODUCED_CHOICES = {
    0: "Vanilla",
    1: "The Ruins of Kunark",
    2: "The Scars of Velious",
    3: "The Shadows of Luclin",
    4: "The Planes of Power",
    5: "The Legacy of Ykesha ",
    6: "Lost Dungeons of Norrath",
    7: "Gates of Discord",
    8: "Omens of War",
    9: "Dragons of Norrath",
    10: "Depths of Darkhollow",
}

PLAYER_RACE_RESTRICTION_CHOICES = {
    -1: "None",
    0: "Unknown",
    1: "Human",
    2: "Barbarian",
    3: "Erudite",
    4: "Wood Elf",
    5: "High Elf",
    6: "Dark Elf",
    7: "Half Elf",
    8: "Dwarf",
    9: "Troll",
    10: "Ogre",
    11: "Halfling",
    12: "Gnome",
    13: "Iksar",
    14: "Vah Shir",
    128: "Iksar",
}

PLAYER_CLASS_RESTRICTION_CHOICES = {
    -1: "None",
    0: "Unknown",
    1: "Warrior",
    2: "Cleric",
    3: "Paladin",
    4: "Ranger",
    5: "Shadowknight",
    6: "Druid",
    7: "Monk",
    8: "Bard",
    9: "Rogue",
    10: "Shaman",
    11: "Necromancer",
    12: "Wizard",
    13: "Magician",
    14: "Enchanter",
    15: "Beastlord",
}

PLAYER_DEITY_RESTRICTIONS = {
    -1: "None",
    140: "Agnostic",
    396: "Agnostic",  # Yes, the duplicate is intentional
    201: "Bertoxxulous",
    202: "Brell Serilis",
    203: "Cazic Thule",
    204: "Erollisi Marr",
    205: "Bristlebane",
    206: "Innoruuk",
    207: "Karana",
    208: "Mithaniel Marr",
    209: "Prexus",
    210: "Quellious",
    211: "Rallos Zek",
    212: "Rodcet Nife",
    213: "Solusek Ro",
    214: "The Tribunal",
    215: "Tunare",
    216: "Veeshan",
}


# Base Reward class - abstract
class QuestReward(models.Model):
    quest = models.ForeignKey('Quests', on_delete=models.CASCADE, related_name='%(class)s_rewards')
    is_optional = models.BooleanField(default=False, help_text="Whether player can choose this reward or not")
    reward_group = models.PositiveSmallIntegerField(default=0,
                                                    help_text="Group rewards together - player chooses one reward from each group")

    class Meta:
        abstract = True
        ordering = ['quest', 'reward_group']


# Item rewards
class ItemReward(QuestReward):
    item_id = models.IntegerField()
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    charges = models.PositiveIntegerField(null=True, blank=True,
                                          help_text="Number of charges, if applicable")
    attuned = models.BooleanField(default=False, help_text="Whether the item is attuned (no-trade)")

    def __str__(self):
        qty = f"{self.quantity}x " if self.quantity > 1 else ""
        return f"{qty}{self.item_name} ({self.item_id})"

    class Meta(QuestReward.Meta):
        verbose_name = "Item Reward"
        verbose_name_plural = "Item Rewards"
        indexes = [
            models.Index(fields=['item_id'], name='reward_item_id_idx'),
            models.Index(fields=['item_name'], name='reward_item_name_idx'),
        ]


# Experience rewards
class ExperienceReward(QuestReward):
    amount = models.IntegerField(validators=[MinValueValidator(1)])
    is_percentage = models.BooleanField(default=False,
                                        help_text="Whether this is a percentage of level or flat amount")

    def __str__(self):
        if self.is_percentage:
            return f"{self.amount}% of level"
        return f"{self.amount} experience points"

    class Meta(QuestReward.Meta):
        verbose_name = "Experience Reward"
        verbose_name_plural = "Experience Rewards"


# Money rewards
class CurrencyReward(QuestReward):
    platinum = models.PositiveIntegerField(default=0)
    gold = models.PositiveIntegerField(default=0)
    silver = models.PositiveIntegerField(default=0)
    copper = models.PositiveIntegerField(default=0)

    def __str__(self):
        parts = []
        if self.platinum > 0:
            parts.append(f"{self.platinum}pp")
        if self.gold > 0:
            parts.append(f"{self.gold}gp")
        if self.silver > 0:
            parts.append(f"{self.silver}sp")
        if self.copper > 0:
            parts.append(f"{self.copper}cp")
        return " ".join(parts) if parts else "No currency"

    class Meta(QuestReward.Meta):
        verbose_name = "Currency Reward"
        verbose_name_plural = "Currency Rewards"


# Faction rewards
class FactionReward(QuestReward):
    faction_id = models.IntegerField()
    faction_name = models.CharField(max_length=100)
    amount = models.IntegerField(help_text="Positive for faction gain, negative for faction loss")

    def __str__(self):
        action = "gain" if self.amount > 0 else "loss"
        return f"{self.faction_name} {action}: {abs(self.amount)}"

    class Meta(QuestReward.Meta):
        verbose_name = "Faction Reward"
        verbose_name_plural = "Faction Rewards"
        indexes = [
            models.Index(fields=['faction_id'], name='reward_faction_id_idx'),
            models.Index(fields=['faction_name'], name='reward_faction_name_idx'),
        ]


# Skill rewards
class SkillReward(QuestReward):
    skill_id = models.IntegerField(null=True, blank=True)
    skill_name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(default=1, help_text="Skill points gained")

    def __str__(self):
        return f"{self.skill_name} +{self.amount}"

    class Meta(QuestReward.Meta):
        verbose_name = "Skill Reward"
        verbose_name_plural = "Skill Rewards"


# Spell rewards
class SpellReward(QuestReward):
    spell_id = models.IntegerField()
    spell_name = models.CharField(max_length=100)
    spell_level = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.spell_name} (Level {self.spell_level})"

    class Meta(QuestReward.Meta):
        verbose_name = "Spell Reward"
        verbose_name_plural = "Spell Rewards"
        indexes = [
            models.Index(fields=['spell_id'], name='reward_spell_id_idx'),
        ]


# Title rewards
class TitleReward(QuestReward):
    title_text = models.CharField(max_length=200)
    is_prefix = models.BooleanField(default=True, help_text="Is this a prefix or suffix title")

    def __str__(self):
        title_type = "Prefix" if self.is_prefix else "Suffix"
        return f"{title_type}: {self.title_text}"

    class Meta(QuestReward.Meta):
        verbose_name = "Title Reward"
        verbose_name_plural = "Title Rewards"


# AA rewards
class AAReward(QuestReward):
    aa_id = models.IntegerField(null=True, blank=True)
    aa_name = models.CharField(max_length=100)
    aa_points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.aa_name}: {self.aa_points} point(s)"

    class Meta(QuestReward.Meta):
        verbose_name = "AA Reward"
        verbose_name_plural = "AA Rewards"


# Access/Flag rewards
class AccessReward(QuestReward):
    flag_name = models.CharField(max_length=100)
    flag_value = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, help_text="What access does this flag provide?")

    def __str__(self):
        return f"Access: {self.flag_name}"

    class Meta(QuestReward.Meta):
        verbose_name = "Access Reward"
        verbose_name_plural = "Access Rewards"
        indexes = [
            models.Index(fields=['flag_name'], name='reward_flag_name_idx'),
        ]


class QuestCategory(models.Model):
    """Main categories for quests"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="CSS class or icon reference")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Quest Categories"
        ordering = ['name']


class QuestTag(models.Model):
    """Flexible tags for quest filtering and search"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

FACTION_ROLE_CHOICES = [
    ('required', 'Required'),
    ('raised', 'Raised'),
    ('lowered', 'Lowered'),
]


QUEST_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
]


class Quests(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, unique=True)
    description = MDTextField(null=True, blank=True, default="")
    starting_npc_id = models.IntegerField(default=0, null=False)
    starting_zone = models.CharField(max_length=100, null=False, choices=sorted(ZONE_SHORT_TO_LONG.items()))
    expansion_introduced = models.SmallIntegerField(null=True, default=0, choices=EXPANSION_INTRODUCED_CHOICES)
    minimum_level = models.SmallIntegerField(null=True, default=1)
    maximum_level = models.SmallIntegerField(null=True, default=-1)
    class_restrictions = models.IntegerField(null=False, default=0, choices=PLAYER_CLASS_RESTRICTION_CHOICES)
    race_restrictions = models.IntegerField(null=False, default=0, choices=PLAYER_RACE_RESTRICTION_CHOICES)
    deity_restrictions = models.IntegerField(null=False, default=0, choices=PLAYER_DEITY_RESTRICTIONS)
    is_repeatable = models.BooleanField(default=True)
    monster_mission = models.BooleanField(default=False)
    related_npcs = models.ManyToManyField("QuestsRelatedNPC", blank=True, related_name="quests")
    related_zones = models.ManyToManyField("QuestsRelatedZone", blank=True, related_name="quests")
    quest_items = models.ManyToManyField("QuestItem", blank=True, related_name="quests")
    difficulty_rating = models.SmallIntegerField(choices=[(1, 'Very Easy'), (2, 'Easy'),
                                                          (3, 'Medium'), (4, 'Hard'),
                                                          (5, 'Very Hard')], default=3)
    estimated_time = models.CharField(max_length=50, blank=True, help_text="Estimated time to complete")
    category = models.ForeignKey(QuestCategory, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='quests')
    tags = models.ManyToManyField(QuestTag, blank=True, related_name='quests')
    prerequisite = models.ForeignKey('self', null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='sequels')
    status = models.CharField(max_length=10, choices=QUEST_STATUS_CHOICES, default='draft', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestManager()

    def __str__(self):
        return str(self.name)

    def get_quest_chain(self):
        """Walk back to the first quest and return the full chain in order."""
        first = self
        while first.prerequisite:
            first = first.prerequisite
        chain = []
        current = first
        while current:
            chain.append(current)
            current = current.sequels.first()
        return chain

    def get_all_rewards(self):
        rewards = []
        rewards.extend(list(self.itemreward_rewards.all()))
        rewards.extend(list(self.experiencereward_rewards.all()))
        rewards.extend(list(self.currencyreward_rewards.all()))
        rewards.extend(list(self.factionreward_rewards.all()))
        rewards.extend(list(self.skillreward_rewards.all()))
        rewards.extend(list(self.spellreward_rewards.all()))
        rewards.extend(list(self.titlereward_rewards.all()))
        rewards.extend(list(self.aareward_rewards.all()))
        rewards.extend(list(self.accessreward_rewards.all()))
        return sorted(rewards, key=lambda r: r.reward_group)

    def get_reward_groups(self):
        all_rewards = self.get_all_rewards()
        groups = {}
        for reward in all_rewards:
            if reward.reward_group not in groups:
                groups[reward.reward_group] = []
            groups[reward.reward_group].append(reward)
        return groups

    def get_reward_items(self):
        return [reward.item_id for reward in self.itemreward_rewards.all()]

    class Meta:
        managed = True
        db_table = 'quests'
        verbose_name = 'Quest'
        verbose_name_plural = 'Quests'
        indexes = [
            models.Index(fields=['name'], name='quest_name_idx'),
            models.Index(fields=['starting_zone'], name='starting_zone_idx'),
            models.Index(fields=['starting_npc_id'], name='starting_npc_idx'),
            models.Index(fields=['expansion_introduced'], name='expansion_idx'),
            models.Index(fields=['minimum_level', 'maximum_level'], name='level_range_idx'),
            models.Index(fields=['class_restrictions'], name='class_idx'),
            models.Index(fields=['race_restrictions'], name='race_idx'),
        ]
        ordering = ['name']


class QuestFaction(models.Model):
    quest = models.ForeignKey(Quests, on_delete=models.CASCADE, related_name='quest_factions')
    faction_id = models.IntegerField()
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=FACTION_ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Quest Faction'
        verbose_name_plural = 'Quest Factions'
        unique_together = ['quest', 'faction_id', 'role']
        ordering = ['role', 'name']
        indexes = [
            models.Index(fields=['faction_id'], name='quest_faction_id_idx'),
            models.Index(fields=['role'], name='quest_faction_role_idx'),
        ]


class QuestItem(models.Model):
    item_id = models.IntegerField(null=False, default=0)
    name = models.CharField(max_length=64, null=False, default='', db_column='Name')

    def __str__(self):
        return f"{self.name} ({self.item_id})"

    class Meta:
        verbose_name = 'Quest Item'
        verbose_name_plural = 'Quest Items'
        indexes = [
            models.Index(fields=['item_id'], name='item_id_idx'),
            models.Index(fields=['name'], name='item_name_idx'),
        ]
        ordering = ['name']
        unique_together = ['item_id', 'name']


PATCH_HISTORY_ROLE_CHOICES = [
    ('introduced', 'Introduced'),
    ('updated', 'Updated'),
]


ISSUE_REPORT_STATUS_CHOICES = [
    ('open', 'Open'),
    ('resolved', 'Resolved'),
]


class QuestPatchHistory(models.Model):
    quest = models.ForeignKey('Quests', on_delete=models.CASCADE, related_name='patch_history')
    patch = models.ForeignKey('patch.PatchMessage', on_delete=models.CASCADE, related_name='quest_history')
    role = models.CharField(max_length=10, choices=PATCH_HISTORY_ROLE_CHOICES, default='updated')
    notes = models.TextField(blank=True, help_text="Staff note: what changed and how this may differ from P99 wiki or Allakhazam")

    def __str__(self):
        return f"{self.quest.name} — {self.get_role_display()} in {self.patch.title}"

    class Meta:
        verbose_name = 'Quest Patch History'
        verbose_name_plural = 'Quest Patch Histories'
        unique_together = ['quest', 'patch', 'role']
        ordering = ['patch__patch_date']


class QuestIssueReport(models.Model):
    quest = models.ForeignKey('Quests', on_delete=models.CASCADE, related_name='issue_reports')
    body = models.TextField()
    reporter_name = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ISSUE_REPORT_STATUS_CHOICES, default='open', db_index=True)

    def __str__(self):
        return f"Issue on '{self.quest.name}' ({self.created_at.date()})"

    class Meta:
        verbose_name = 'Quest Issue Report'
        verbose_name_plural = 'Quest Issue Reports'
        ordering = ['-created_at']


class QuestsRelatedNPC(models.Model):
    """
    This model stores npcs related to a given quest
    """
    npc_id = models.IntegerField(null=False, default=0, unique=True)  # TODO: OneToOne with NPCTypes (different database)
    name = models.CharField(max_length=64, default='', unique=False, null=False, blank=True)

    def __str__(self):
        return f"{self.name} ({self.npc_id})"

    class Meta:
        managed = True
        db_table = 'quests_related_npc'
        verbose_name = 'Quest Related NPC'
        verbose_name_plural = 'Quest Related NPCs'
        indexes = [
            models.Index(fields=['npc_id'], name='npc_id_idx'),
            models.Index(fields=['name'], name='npc_name_idx'),
        ]
        ordering = ['name']


class QuestsRelatedZone(models.Model):
    """
    This model stores zones related to a given quest
    """
    zone_id = models.IntegerField(null=False, default=0)
    long_name = models.TextField(null=False)
    short_name = models.CharField(max_length=32, null=True, unique=True)

    def __str__(self):
        return str(self.long_name)

    class Meta:
        managed = True
        db_table = 'quests_related_zone'
        verbose_name = 'Quest Related Zone'
        verbose_name_plural = 'Quest Related Zones'
        indexes = [
            models.Index(fields=['short_name'], name='short_name_idx'),
            models.Index(fields=['zone_id'], name='zone_id_idx'),
        ]
        ordering = ['short_name']

