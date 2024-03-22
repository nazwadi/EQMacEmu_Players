from django.db import models


class Items(models.Model):
    """
    This model maps to the items table in the database.
    """
    def __str__(self):
        return str(self.id)

    id = models.IntegerField(primary_key=True, null=False, default=0)
    Name = models.CharField(max_length=64, null=False, default=0)
    scroll_effect = models.IntegerField(null=False, default=0, db_column='scrolleffect')
    scroll_type = models.IntegerField(null=False, default=0, db_column='scrolltype')
    source = models.CharField(max_length=20, null=False)
    icon = models.IntegerField(null=False, default=0)
    price = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'items'
        managed = False


