from django.db import models


class FactionList(models.Model):
    """
    This model maps to the faction list table in the database
    """

    def __str__(self):
        return str(self.id)

    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=50, null=False)
    base = models.SmallIntegerField(null=False, default=0)
    see_illusion = models.SmallIntegerField(null=False, default=1)
    min_cap = models.SmallIntegerField(null=False, default=0)
    max_cap = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = 'faction_list'
        managed = False


class FactionListMod(models.Model):
    """
    This model maps to the faction_list_mod table in the database
    """

    def __str__(self):
        return f"{self.id}, {self.mod_name}, {self.mod}"

    def __repr__(self):
        return f"{self.id}, {self.mod_name}, {self.mod}"

    id = models.AutoField(primary_key=True, null=False)
    faction_id = models.IntegerField(unique=True, null=False)
    mod = models.SmallIntegerField(null=False)
    mod_name = models.CharField(max_length=16, null=False)

    class Meta:
        db_table = 'faction_list_mod'
        managed = False
