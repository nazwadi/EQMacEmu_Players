# managers.py
from django.db import models
import logging

logger = logging.getLogger(__name__)


class QuestQuerySet(models.QuerySet):
    def for_npc(self, npc_id):
        """Get all quests related to a particular NPC"""
        # Get quests where this NPC is the starting NPC
        starting_quests = self.filter(starting_npc_id=npc_id)

        # Get quests where this NPC is in the related NPCs
        related_quests = self.filter(related_npcs__npc_id=npc_id)

        # Combine the querysets
        return (starting_quests | related_quests).distinct()

    def for_item(self, item_id):
        """Get all quests related to a particular item"""
        # Get quests where this item is in the quest_items
        item_quests = self.filter(quest_items__item_id=item_id)

        # We need to also check the JSON field for reward items
        # This is more complex as we need to check a JSON field
        # This is a basic implementation - might need refinement based on your JSON structure
        reward_quests = self.filter(quest_reward__contains={'item_id': item_id})

        # Combine the querysets
        return (item_quests | reward_quests).distinct()

    def for_zone(self, zone_id=None, short_name=None):
        """Get all quests related to a particular zone"""
        if not zone_id and not short_name:
            raise ValueError("Must provide either zone_id or short_name")

        # Get quests where this zone is the starting zone
        if short_name:
            starting_quests = self.filter(starting_zone=short_name)
        else:
            # You might need to adjust this if you have a mapping between zone_id and short_name
            starting_quests = self.none()

        # Get quests where this zone is in the related zones
        if zone_id:
            related_quests = self.filter(related_zones__zone_id=zone_id)
        elif short_name:
            related_quests = self.filter(related_zones__short_name=short_name)

        # Combine the querysets
        return (starting_quests | related_quests).distinct()

    def for_level_range(self, min_level, max_level=None):
        """Get all quests appropriate for a character level range"""
        if max_level is None:
            max_level = min_level

        # This handles the quest's level range logic
        # - minimum_level <= max_level: character's max level is at or above quest min level
        # - maximum_level == -1 OR maximum_level >= min_level: quest has no max level or it's at or above character min level
        return self.filter(
            models.Q(minimum_level__lte=max_level) &
            (models.Q(maximum_level=-1) | models.Q(maximum_level__gte=min_level))
        )

    def for_class(self, class_id):
        """Get all quests available to a specific class"""
        # This works if class_restrictions is a bitmap or if -1 means "all classes"
        return self.filter(
            models.Q(class_restrictions=-1) |
            models.Q(class_restrictions=class_id)
        )

    def for_race(self, race_id):
        """Get all quests available to a specific race"""
        # This works if race_restrictions is a bitmap or if -1 means "all races"
        return self.filter(
            models.Q(race_restrictions=-1) |
            models.Q(race_restrictions=race_id)
        )

    def for_expansion(self, expansion_id):
        """Get all quests from a specific expansion or earlier"""
        return self.filter(expansion_introduced__lte=expansion_id)


class QuestManager(models.Manager):
    def get_queryset(self):
        return QuestQuerySet(self.model, using=self._db)

    # Pass through all the custom queryset methods
    def for_npc(self, npc_id):
        return self.get_queryset().for_npc(npc_id)

    def for_item(self, item_id):
        return self.get_queryset().for_item(item_id)

    def for_zone(self, zone_id=None, short_name=None):
        return self.get_queryset().for_zone(zone_id, short_name)

    def for_level_range(self, min_level, max_level=None):
        return self.get_queryset().for_level_range(min_level, max_level)

    def for_class(self, class_id):
        return self.get_queryset().for_class(class_id)

    def for_race(self, race_id):
        return self.get_queryset().for_race(race_id)

    def for_expansion(self, expansion_id):
        return self.get_queryset().for_expansion(expansion_id)