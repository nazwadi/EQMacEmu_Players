from django.db import models


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
