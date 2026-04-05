from django.db import models

from common.constants import PLAYER_CLASSES

PATCH_HISTORY_ROLE_CHOICES = [
    ('introduced', 'Introduced'),
    ('updated', 'Updated'),
]

# Integer-keyed expansion choices used by ItemExpansion (covers all 31 expansions).
ITEM_EXPANSION_CHOICES = [
    (0, 'Original EverQuest'),
    (1, 'Ruins of Kunark'),
    (2, 'Scars of Velious'),
    (3, 'Shadows of Luclin'),
    (4, 'Planes of Power'),
    (5, 'Legacy of Ykesha'),
    (6, 'Lost Dungeons of Norrath'),
    (7, 'Gates of Discord'),
    (8, 'Omens of War'),
    (9, 'Dragons of Norrath'),
    (10, 'Depths of Darkhollow'),
    (11, 'Prophecy of Ro'),
    (12, "The Serpent's Spine"),
    (13, 'The Buried Sea'),
    (14, 'Secrets of Faydwer'),
    (15, 'Seeds of Destruction'),
    (16, 'Underfoot'),
    (17, 'House of Thule'),
    (18, 'Veil of Alaris'),
    (19, 'Rain of Fear'),
    (20, 'Call of the Forsaken'),
    (21, 'The Darkened Sea'),
    (22, 'The Broken Mirror'),
    (23, 'Empires of Kunark'),
    (24, 'Ring of Scale'),
    (25, 'The Burning Lands'),
    (26, 'Torment of Velious'),
    (27, 'Claws of Veeshan'),
    (28, 'Terror of Luclin'),
    (29, 'Night of Shadows'),
    (30, "Laurion's Song"),
    (31, 'The Outer Brood'),
]

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


class ItemExpansionIdRange(models.Model):
    """
    Configurable item ID → expansion mapping used as a fallback by
    compute_item_expansions when no zone provenance data exists for an item
    (e.g. crafted, quest-reward, or vendor-only items).

    Ranges are evaluated in ascending min_item_id order; the first range whose
    window contains the item ID wins.  Edit via the Django admin, then re-run:

        python manage.py compute_item_expansions --force

    For individual exceptions (a later item filling an earlier ID slot, etc.)
    use ItemExpansion.is_override instead of adjusting ranges here.
    """
    expansion = models.IntegerField(choices=ITEM_EXPANSION_CHOICES)
    min_item_id = models.IntegerField()
    max_item_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='Exclusive upper bound. Leave blank for "this expansion and above".',
    )

    class Meta:
        ordering = ['min_item_id']
        verbose_name = 'Item Expansion ID Range'
        verbose_name_plural = 'Item Expansion ID Ranges'

    def __str__(self):
        label = dict(ITEM_EXPANSION_CHOICES).get(self.expansion, str(self.expansion))
        upper = str(self.max_item_id) if self.max_item_id is not None else '∞'
        return f'{label}: IDs {self.min_item_id} – {upper}'


class ItemExpansion(models.Model):
    """
    Maps an item ID (from the game DB) to the expansion it was first introduced in.

    Populated by the compute_item_expansions management command using zone provenance
    (minimum expansion of zones the item drops in) with an item ID range fallback.
    Set is_override=True via the admin to pin a specific expansion and prevent the
    management command from overwriting it.
    """
    SOURCE_ZONE = 'zone'
    SOURCE_ID_RANGE = 'id_range'
    SOURCE_MANUAL = 'manual'
    SOURCE_CHOICES = [
        (SOURCE_ZONE, 'Zone Provenance'),
        (SOURCE_ID_RANGE, 'Item ID Range'),
        (SOURCE_MANUAL, 'Manual Override'),
    ]

    item_id = models.IntegerField(unique=True)
    expansion = models.IntegerField(choices=ITEM_EXPANSION_CHOICES, db_index=True)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_ZONE)
    is_override = models.BooleanField(
        default=False,
        help_text='When checked, compute_item_expansions will never overwrite this entry.',
    )

    class Meta:
        ordering = ['item_id']
        verbose_name = 'Item Expansion'
        verbose_name_plural = 'Item Expansions'

    def __str__(self):
        label = dict(ITEM_EXPANSION_CHOICES).get(self.expansion, str(self.expansion))
        return f'Item {self.item_id}: {label} ({self.source})'


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


class ItemPatchHistory(models.Model):
    """
    Links an item (by game-DB id) to a patch message that changed it.

    Most items were introduced with their expansion — ItemExpansion already
    tracks that. Only use role='introduced' when a specific patch note
    documents the item being added mid-expansion. The common case is
    role='updated' (stat change, effect change, no-rent/no-drop flag, etc.).
    """
    item_id = models.IntegerField(
        help_text="Game-DB item id (items.id)",
    )
    item_name = models.CharField(
        max_length=128,
        help_text="Denormalized name for display (game DB is read-only).",
    )
    patch = models.ForeignKey(
        'patch.PatchMessage',
        on_delete=models.CASCADE,
        related_name='item_history',
    )
    role = models.CharField(
        max_length=10,
        choices=PATCH_HISTORY_ROLE_CHOICES,
        default='updated',
        help_text=(
            "Use 'Updated' for stat/flag/effect changes documented in the patch. "
            "Only use 'Introduced' when the item was genuinely added mid-expansion "
            "by this specific patch — ItemExpansion handles expansion-launch items."
        ),
    )
    notes = models.TextField(
        blank=True,
        help_text="What changed and how this may differ from P99 wiki or Allakhazam.",
    )

    def __str__(self):
        return f"{self.item_name} ({self.item_id}) — {self.get_role_display()} in {self.patch.title}"

    class Meta:
        verbose_name = 'Item Patch History'
        verbose_name_plural = 'Item Patch Histories'
        unique_together = ['item_id', 'patch', 'role']
        ordering = ['patch__patch_date']
