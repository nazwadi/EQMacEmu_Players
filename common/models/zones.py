from django.db import models


class Zone(models.Model):
    """
    This model maps to the zone table in the database.
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False)
    short_name = models.CharField(max_length=32, null=True, unique=True)
    long_name = models.TextField(null=False)
    zone_exp_multiplier = models.FloatField(null=False, default=0.0)
    expansion = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = "zone"