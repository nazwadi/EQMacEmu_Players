from django.db import models


class Zone(models.Model):
    """
    This model maps to the zone table in the database.
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False)
    file_name = models.CharField(max_length=16, null=True, default=None)
    long_name = models.TextField(null=False)
    short_name = models.CharField(max_length=32, null=True, unique=True)
    map_file_name = models.CharField(max_length=100, null=True, default=None)
    safe_x = models.FloatField(null=False, default=0.0)
    safe_y = models.FloatField(null=False, default=0.0)
    safe_z = models.FloatField(null=False, default=0.0)
    safe_heading = models.FloatField(null=False, default=0.0)
    graveyard_id = models.FloatField(null=False, default=0.0)
    min_level = models.SmallIntegerField(null=False, default=0)
    min_status = models.SmallIntegerField(null=False, default=0)
    zone_id_number = models.IntegerField(null=False, default=0, db_column="zoneidnumber")
    timezone = models.IntegerField(null=False, default=0)
    max_clients = models.IntegerField(null=False, default=0, db_column="maxclients")
    ruleset = models.IntegerField(null=False, default=0)
    note = models.CharField(max_length=80, null=True, default=None)
    underworld = models.FloatField(null=False, default=0)
    min_clip = models.FloatField(null=False, default=450, db_column="minclip")
    max_clip = models.FloatField(null=False, default=450, db_column="maxclip")
    fog_minclip = models.FloatField(null=False, default=450)
    fog_maxclip = models.FloatField(null=False, default=450)
    fog_blue = models.SmallIntegerField(null=False, default=0)
    fog_red = models.SmallIntegerField(null=False, default=0)
    fog_green = models.SmallIntegerField(null=False, default=0)
    sky = models.SmallIntegerField(null=False, default=1)
    ztype = models.SmallIntegerField(null=False, default=1)
    zone_exp_multiplier = models.FloatField(null=False, default=0.0)
    gravity = models.FloatField(null=False, default=0)
    time_type = models.SmallIntegerField(null=False, default=2)
    fog_red1 = models.SmallIntegerField(null=False, default=0)
    fog_green1 = models.SmallIntegerField(null=False, default=0)
    fog_blue1 = models.SmallIntegerField(null=False, default=0)
    fog_minclip1 = models.FloatField(null=False, default=450)
    fog_maxclip1 = models.FloatField(null=False, default=450)
    fog_red2 = models.SmallIntegerField(null=False, default=0)
    fog_green2 = models.SmallIntegerField(null=False, default=0)
    fog_blue2 = models.SmallIntegerField(null=False, default=0)
    fog_minclip2 = models.FloatField(null=False, default=450)
    fog_maxclip2 = models.FloatField(null=False, default=450)
    fog_red3 = models.SmallIntegerField(null=False, default=0)
    fog_green3 = models.SmallIntegerField(null=False, default=0)
    fog_blue3 = models.SmallIntegerField(null=False, default=0)
    fog_minclip3 = models.FloatField(null=False, default=450)
    fog_maxclip3 = models.FloatField(null=False, default=450)
    fog_red4 = models.SmallIntegerField(null=True, default=0)
    fog_green4 = models.SmallIntegerField(null=False, default=0)
    fog_blue4 = models.SmallIntegerField(null=False, default=0)
    fog_minclip4 = models.FloatField(null=False, default=450)
    fog_maxclip4 = models.FloatField(null=False, default=450)
    fog_density = models.FloatField(null=False, default=0)
    flag_needed = models.CharField(max_length=128, null=False)
    can_bind = models.SmallIntegerField(null=False, default=1, db_column="canbind")
    can_combat = models.SmallIntegerField(null=False, default=1, db_column="cancombat")
    can_levitate = models.SmallIntegerField(null=False, default=1, db_column="canlevitate")
    expansion = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = "zone"


class ZonePoints(models.Model):
    """
    This model maps to the zone_points table in the database
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False, default=None)
    zone = models.CharField(max_length=32, null=True)
    number = models.SmallIntegerField(null=False, default=None)
    y = models.FloatField(null=False, default=0)
    x = models.FloatField(null=False, default=0)
    z = models.FloatField(null=False, default=0)
    heading = models.FloatField(null=False, default=0)
    target_y = models.FloatField(null=False, default=0)
    target_x = models.FloatField(null=False, default=0)
    target_z = models.FloatField(null=False, default=0)
    target_heading = models.FloatField(null=False, default=0)
    target_zone_id = models.IntegerField(null=False, default=0)
    client_version_mask = models.IntegerField(null=False, default=4294967295)

    class Meta:
        db_table = "zone_points"
