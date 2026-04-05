from django.db import models

PATCH_HISTORY_ROLE_CHOICES = [
    ('introduced', 'Introduced'),
    ('updated', 'Updated'),
]


class ZonePage(models.Model):
    """
    Zone Page Text
    """
    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=32, null=True, blank=True, default=None)
    level_of_monsters = models.TextField(null=True, blank=True, default=None)
    types_of_monsters = models.TextField(null=True, blank=True, default=None)
    description = models.TextField(blank=True)
    map = models.TextField(blank=True)
    dangers = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    travel_to_from = models.TextField(blank=True)
    history_lore = models.TextField(blank=True)


class ZonePatchHistory(models.Model):
    """
    Links a zone (by short_name) to a patch message that changed it.

    Zones were introduced with their expansion. Only use role='introduced'
    when a specific patch note documents a zone opening or becoming accessible
    mid-expansion. The common case is role='updated' (mob changes, loot,
    zone connections, content additions, etc.).
    """
    zone_short_name = models.CharField(
        max_length=32,
        help_text="Zone short name (e.g. 'qeynos', 'commons'). Matches zone.short_name in the game DB.",
    )
    zone_long_name = models.CharField(
        max_length=128,
        help_text="Denormalized display name (game DB is read-only).",
    )
    patch = models.ForeignKey(
        'patch.PatchMessage',
        on_delete=models.CASCADE,
        related_name='zone_history',
    )
    role = models.CharField(
        max_length=10,
        choices=PATCH_HISTORY_ROLE_CHOICES,
        default='updated',
        help_text=(
            "Use 'Updated' for content/mob/loot changes documented in the patch. "
            "Only use 'Introduced' when a zone opened mid-expansion via this patch."
        ),
    )
    notes = models.TextField(
        blank=True,
        help_text="What changed and how this may differ from P99 wiki or Allakhazam.",
    )

    def __str__(self):
        return f"{self.zone_long_name} ({self.zone_short_name}) — {self.get_role_display()} in {self.patch.title}"

    class Meta:
        verbose_name = 'Zone Patch History'
        verbose_name_plural = 'Zone Patch Histories'
        unique_together = ['zone_short_name', 'patch', 'role']
        ordering = ['patch__patch_date']
