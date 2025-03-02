from django.db import models
from mdeditor.fields import MDTextField
from common.constants import ZONE_SHORT_TO_LONG

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


class Quests(models.Model):
    """
    This model stores quest data that should correlate to quest scripts in the database
    """

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
    quest_reward = models.JSONField(default=dict, blank=True,
                                    help_text="Reward data like {'item_id': 123, 'faction': 'Guardians', 'exp': 500, 'flag': 'completed_zone'}")
    factions_required = models.ManyToManyField("QuestFactionRequired", blank=True, related_name="required_for_quests")
    factions_raised = models.ManyToManyField("QuestFactionRaised", blank=True, related_name="raised_for_quests")
    factions_lowered = models.ManyToManyField("QuestFactionLowered", blank=True, related_name="lowered_for_quests")

    def __str__(self):
        return str(self.name)

    # Helper method to find reward items
    def get_reward_items(self):
        """Return a list of item_ids from the quest_reward JSON field"""
        if not self.quest_reward or 'item_id' not in self.quest_reward:
            return []

        if isinstance(self.quest_reward['item_id'], list):
            return self.quest_reward['item_id']
        return [self.quest_reward['item_id']]

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


class QuestFactionRequired(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __unicode__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name = 'Required Faction'
        verbose_name_plural = 'Required Factions'
        ordering = ['name']


class QuestFactionRaised(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __unicode__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name = 'Raised Faction'
        verbose_name_plural = 'Raised Factions'
        ordering = ['name']


class QuestFactionLowered(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __unicode__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name = 'Lowered Faction'
        verbose_name_plural = 'Lowered Factions'
        ordering = ['name']


class QuestItem(models.Model):
    """
    This model stores quest items related to a given quest
    """
    item_id = models.IntegerField(null=False, default=0)
    Name = models.CharField(max_length=64, null=False, default=0)

    def __str__(self):
        return f"{self.Name} ({self.item_id})"

    def __unicode__(self):
        return f"{self.Name} ({self.item_id})"

    class Meta:
        verbose_name = 'Quest Item'
        verbose_name_plural = 'Quest Items'
        indexes = [
            models.Index(fields=['item_id'], name='item_id_idx'),
            models.Index(fields=['Name'], name='item_name_idx'),
        ]
        ordering = ['Name']
        unique_together = ['item_id', 'Name']  # Ensure no duplicate entries for the same item


class QuestsRelatedNPC(models.Model):
    """
    This model stores npcs related to a given quest
    """
    npc_id = models.IntegerField(null=False, default=0, unique=True)  # TODO: OneToOne with NPCTypes (different database)
    name = models.CharField(max_length=64, default='', unique=False, null=False, blank=True)

    def __str__(self):
        return f"{self.name} ({self.npc_id})"

    def __unicode__(self):
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

    def __unicode__(self):
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
