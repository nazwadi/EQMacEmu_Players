from django.db import models

PATCH_HISTORY_ROLE_CHOICES = [
    ('introduced', 'Introduced'),
    ('updated', 'Updated'),
]


class NpcPage(models.Model):
    """
    Npc Page Text
    """
    def __str__(self):
        return str(self.npc_id)

    npc_id = models.IntegerField(primary_key=True, null=False, default=None)
    description = models.TextField(blank=True)
    portrait = models.TextField(blank=True)
    related_quests = models.TextField(blank=True)


class NPCPatchHistory(models.Model):
    """
    Links an NPC (by game-DB id) to a patch message that changed it.

    Most NPCs were introduced with their expansion — only use role='introduced'
    when a specific patch note documents the NPC being added mid-expansion.
    The common case is role='updated' (stat change, loot change, spawn move, etc.).
    """
    npc_id = models.IntegerField(
        help_text="Game-DB NPC id (npc_types.id)",
    )
    npc_name = models.CharField(
        max_length=64,
        help_text="Denormalized name for display (game DB is read-only).",
    )
    patch = models.ForeignKey(
        'patch.PatchMessage',
        on_delete=models.CASCADE,
        related_name='npc_history',
    )
    role = models.CharField(
        max_length=10,
        choices=PATCH_HISTORY_ROLE_CHOICES,
        default='updated',
        help_text=(
            "Use 'Updated' for stat/loot/spawn changes documented in the patch. "
            "Only use 'Introduced' when the NPC was genuinely added mid-expansion "
            "by this specific patch — expansion-launch NPCs should not have an "
            "'Introduced' entry here."
        ),
    )
    notes = models.TextField(
        blank=True,
        help_text="What changed and how this may differ from P99 wiki or Allakhazam.",
    )

    def __str__(self):
        return f"{self.npc_name} ({self.npc_id}) — {self.get_role_display()} in {self.patch.title}"

    class Meta:
        verbose_name = 'NPC Patch History'
        verbose_name_plural = 'NPC Patch Histories'
        unique_together = ['npc_id', 'patch', 'role']
        ordering = ['patch__patch_date']
