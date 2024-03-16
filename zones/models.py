from django.db import models


class ZonePage(models.Model):
    """
    Zone Page Text
    """
    def __str__(self):
        return self.id

    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=32, null=True, blanke=True, default=None)
    description = models.TextField(blank=True)
    map_legend = models.TextField(blank=True)
