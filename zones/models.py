from django.db import models


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
