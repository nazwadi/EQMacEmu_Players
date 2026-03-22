from django.db import models

from common.constants import PLAYER_CLASSES

EXPANSION_CHOICES = [
    ('vanilla-pre-planar', 'Classic: Pre-Planar'),
    ('vanilla-planar', 'Classic: Planar'),
    ('kunark', 'Kunark'),
    ('velious-group', 'Velious: Group'),
    ('velious-raid', 'Velious: Raid'),
    ('luclin-group', 'Luclin: Group'),
    ('luclin-raid', 'Luclin: Raid'),
    ('pop-group', 'Planes of Power: Group'),
    ('pop-raid', 'Planes of Power: Raid'),
]

# Canonical slot ordering for display
SLOT_ORDER = [
    'Ears', 'Fingers', 'Neck', 'Head', 'Face',
    'Chest', 'Shoulders', 'Arms', 'Back', 'Waist',
    'Wrists', 'Legs', 'Hands', 'Feet',
    'Charm', 'Instrument',
    'Primary H2H', 'Primary 2HS', 'Primary 1HS', 'Primary 1HB',
    'Primary 2HB', 'Primary Piercing', 'Secondary', 'Range',
]


class BISEntry(models.Model):
    """A single item recommendation for a class/expansion/slot combination."""

    EXPANSION_CHOICES = EXPANSION_CHOICES

    class_id = models.SmallIntegerField()
    expansion = models.CharField(max_length=32, choices=EXPANSION_CHOICES)
    slot = models.CharField(max_length=48)
    item_name = models.CharField(max_length=128)
    # item_id links to the game DB Items table; IntegerField (no FK constraint)
    # because Items lives in a separate database.
    item_id = models.IntegerField(null=True, blank=True)
    # 0 = primary BIS pick, 1+ = alternatives in order
    rank = models.PositiveSmallIntegerField(default=0)
    note = models.CharField(max_length=256, blank=True)

    class Meta:
        unique_together = ('class_id', 'expansion', 'slot', 'item_name')
        ordering = ['slot', 'rank']
        verbose_name = 'BIS Entry'
        verbose_name_plural = 'BIS Entries'

    def __str__(self):
        class_name = PLAYER_CLASSES.get(self.class_id, str(self.class_id))
        return f'{class_name} [{self.expansion}] {self.slot}: {self.item_name}'


class BISRevision(models.Model):
    """Audit log entry for a change to the BIS list."""

    ACTION_ADD = 'add'
    ACTION_REMOVE = 'remove'
    ACTION_REORDER = 'reorder'
    ACTION_EDIT = 'edit'
    ACTION_CHOICES = [
        (ACTION_ADD, 'Added'),
        (ACTION_REMOVE, 'Removed'),
        (ACTION_REORDER, 'Reordered'),
        (ACTION_EDIT, 'Edited'),
    ]

    class_id = models.SmallIntegerField()
    expansion = models.CharField(max_length=32)
    slot = models.CharField(max_length=48)
    item_name = models.CharField(max_length=128)
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    old_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    new_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    old_note = models.CharField(max_length=150, blank=True)
    new_note = models.CharField(max_length=150, blank=True)
    edit_summary = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        class_name = PLAYER_CLASSES.get(self.class_id, str(self.class_id))
        return f'{self.changed_by} {self.action} {self.item_name} ({class_name} {self.expansion})'

    def describe(self):
        """Human-readable one-line description of the change."""
        if self.action == self.ACTION_ADD:
            rank_label = 'BIS' if self.new_rank == 0 else f'Alt {self.new_rank}'
            return f'Added {self.item_name} as {rank_label} in {self.slot}'
        if self.action == self.ACTION_REMOVE:
            return f'Removed {self.item_name} from {self.slot}'
        if self.action == self.ACTION_REORDER:
            old_label = 'BIS' if self.old_rank == 0 else f'Alt {self.old_rank}'
            new_label = 'BIS' if self.new_rank == 0 else f'Alt {self.new_rank}'
            return f'Moved {self.item_name} in {self.slot} from {old_label} to {new_label}'
        if self.action == self.ACTION_EDIT:
            return f'Edited note on {self.item_name} in {self.slot}'
        return f'{self.action} {self.item_name}'
