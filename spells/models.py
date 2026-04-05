from django.db import models

PATCH_HISTORY_ROLE_CHOICES = [
    ('introduced', 'Introduced'),
    ('updated', 'Updated'),
]


class SpellExpansion(models.Model):
    """
    Build a database to map spells to the expansion they were first introduced.

    Purpose is to provide expansion filtering options for spell lists.
    """
    EXPANSION_CHOICES = [
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
    ]
    id = models.IntegerField(primary_key=True, null=False, default=0)
    # 0 - Original, 1 - Kunark, 2 - Velious, 3- Luclin, 4- PoP, 5 - LoY, etc...
    expansion = models.IntegerField(null=False, default=0, choices=EXPANSION_CHOICES)

    class Meta:
        db_table = 'spell_expansion'


class SpellPatchHistory(models.Model):
    """
    Links a spell (by game-DB id) to a patch message that changed it.

    SpellExpansion already tracks which expansion introduced a spell.
    Only use role='introduced' when a specific patch note documents a
    spell being added mid-expansion. The common case is role='updated'
    (damage/heal amount, mana cost, duration, component changes, etc.).
    """
    spell_id = models.IntegerField(
        help_text="Game-DB spell id (spells_new.id)",
    )
    spell_name = models.CharField(
        max_length=64,
        help_text="Denormalized name for display (game DB is read-only).",
    )
    patch = models.ForeignKey(
        'patch.PatchMessage',
        on_delete=models.CASCADE,
        related_name='spell_history',
    )
    role = models.CharField(
        max_length=10,
        choices=PATCH_HISTORY_ROLE_CHOICES,
        default='updated',
        help_text=(
            "Use 'Updated' for changes documented in the patch. "
            "Only use 'Introduced' when the spell was genuinely added "
            "mid-expansion by this patch — SpellExpansion handles the rest."
        ),
    )
    notes = models.TextField(
        blank=True,
        help_text="What changed and how this may differ from P99 wiki or Allakhazam.",
    )

    def __str__(self):
        return f"{self.spell_name} ({self.spell_id}) — {self.get_role_display()} in {self.patch.title}"

    class Meta:
        verbose_name = 'Spell Patch History'
        verbose_name_plural = 'Spell Patch Histories'
        unique_together = ['spell_id', 'patch', 'role']
        ordering = ['patch__patch_date']
