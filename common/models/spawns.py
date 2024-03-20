from django.db import models

from common.models.npcs import NPCTypes


class SpawnEntry(models.Model):
    """
    This model maps to the spawnentry table in the database.
    """

    def __str__(self):
        return str(self.spawngroupID)

    spawngroupID = models.IntegerField(primary_key=True, null=False, default=0)
    npcID = models.OneToOneField(NPCTypes, null=False, default=0, on_delete=models.RESTRICT, db_column='npcID')
    chance = models.SmallIntegerField(null=False, default=0)
    min_time = models.SmallIntegerField(null=False, default=0, db_column='mintime')
    max_time = models.SmallIntegerField(null=False, default=0, db_column='maxtime')
    min_expansion = models.SmallIntegerField(null=False, default=-1)
    max_expansion = models.SmallIntegerField(null=False, default=-1)

    class Meta:
        db_table = "spawnentry"
        managed = False
