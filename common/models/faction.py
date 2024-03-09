from django.db import models


class FactionListMod(models.Model):
    """
    This model maps to the faction_list_model table in the database
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False)
    faction_id = models.IntegerField(unique=True, null=False)
    mod = models.SmallIntegerField(null=False)
    mod_name = models.CharField(max_length=16, null=False)

    class Meta:
        db_table = 'faction_list_mod'


