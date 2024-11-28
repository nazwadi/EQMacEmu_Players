from django.db import models

from common.models.npcs import NPCTypes


class SpawnGroup(models.Model):
    """
    This model maps to the spawngroup table in the database.
    """

    def __str__(self):
        return str(self.id)

    id = models.IntegerField(primary_key=True, null=False, default=None)
    name = models.CharField(max_length=50, null=False, unique=True)
    spawn_limit = models.SmallIntegerField(null=False, default=0)
    max_x = models.FloatField(null=False, default=0)
    min_x = models.FloatField(null=False, default=0)
    max_y = models.FloatField(null=False, default=0)
    min_y = models.FloatField(null=False, default=0)
    delay = models.IntegerField(null=False, default=45000)
    min_delay = models.IntegerField(null=False, default=15000, db_column="mindelay")
    despawn = models.SmallIntegerField(null=False, default=0)
    despawn_timer = models.IntegerField(null=False, default=100)
    rand_spawns = models.IntegerField(null=False, default=0)
    rand_respawntime = models.IntegerField(null=False, default=1200)
    rand_variance = models.IntegerField(null=False, default=0)
    rand_condition = models.IntegerField(null=False, default=0, db_column="rand_condition_")
    wp_spawns = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = "spawngroup"
        managed = False

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

    class Meta:
        db_table = "spawn2"
        managed = False
