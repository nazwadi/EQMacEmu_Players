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


class Spawn2(models.Model):
    """
    This model maps to the spawn2 table in the database.
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False, default=None)
    spawngroupID = models.IntegerField(null=False, unique=True, default=0)
    zone = models.CharField(max_length=32, null=True, default=None)
    x = models.FloatField(null=False, default=0.000000)
    y = models.FloatField(null=False, default=0.000000)
    z = models.FloatField(null=False, default=0.000000)
    heading = models.FloatField(null=False, default=0.000000)
    respawntime = models.IntegerField(null=False, default=0)
    variance = models.FloatField(null=False, default=0)
    pathgrid = models.IntegerField(null=False, default=0)
    _condition = models.IntegerField(null=False, default=0)
    cond_value = models.IntegerField(null=False, default=1)
    enabled = models.SmallIntegerField(null=False, default=1)
    animation = models.SmallIntegerField(null=False, default=0)
    boot_respawntime = models.IntegerField(null=False, default=0)
    clear_timer_onboot = models.SmallIntegerField(null=False, default=0)
    boot_variance = models.IntegerField(null=False, default=0)
    force_z = models.SmallIntegerField(null=False, default=0)
    min_expansion = models.FloatField(null=False, default=0)  # This will change to tinyint soon
    max_expansion = models.FloatField(null=False, default=0)  # This will change to tinyint soon
    raid_target_spawnpoint = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = "spawn2"
        managed = False
