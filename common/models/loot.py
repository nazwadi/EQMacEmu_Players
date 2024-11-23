from django.db import models

from common.models.items import Items


class LootTable(models.Model):
    """
    This model maps to the loottable table in the database.
    """
    def __str__(self):
        return str(self.id)

    id = models.IntegerField(primary_key=True, null=False, default=0)
    name = models.CharField(max_length=255, null=False)
    min_cash = models.IntegerField(null=False, default=0, db_column='mincash')
    max_cash = models.IntegerField(null=False, default=0, db_column='maxcash')
    avg_coin = models.IntegerField(null=False, default=0, db_column='avgcoin')
    done = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = 'loottable'
        managed = False


class LootDrop(models.Model):
    """
    This model maps to the lootdrop table in the database.
    """
    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False, default=None)
    name = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = 'lootdrop'
        managed = False


class LootTableEntries(models.Model):
    """
    This model maps to the loottable_entries table in the database.
    """
    def __str__(self):
        return str(self.lootdrop_id.id)

    loottable_id = models.IntegerField(primary_key=True, null=False, default=0)
    lootdrop_id = models.OneToOneField(LootDrop, models.DO_NOTHING, db_column='lootdrop_id')
    multiplier = models.SmallIntegerField(null=False, default=1)
    probability = models.SmallIntegerField(null=False, default=100)
    drop_limit = models.SmallIntegerField(null=False, default=0, db_column='droplimit')
    min_drop = models.SmallIntegerField(null=False, default=0, db_column='mindrop')
    multiplier_min = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = 'loottable_entries'
        managed = False


class LootDropEntries(models.Model):
    """
    This model maps to the lootdrop_entries table in the database
    """
    def __str__(self):
        return str(self.item_id.Name)

    lootdrop_id = models.IntegerField(primary_key=True, null=False, default=0)
    item_id = models.OneToOneField(Items, models.DO_NOTHING, db_column='item_id')
    item_charges = models.SmallIntegerField(null=False, default=1)
    equip_item = models.SmallIntegerField(null=False, default=0)
    chance = models.FloatField(null=False, default=1)
    disabled_chance = models.FloatField(null=False, default=0)
    min_level = models.SmallIntegerField(null=False, default=0, db_column='minlevel')
    max_level = models.SmallIntegerField(null=False, default=255, db_column='maxlevel')
    multiplier = models.SmallIntegerField(null=False, default=1)
    min_expansion = models.SmallIntegerField(null=False, default=-1, db_column='min_expansion')
    max_expansion = models.SmallIntegerField(null=False, default=-1, db_column='max_expansion')
    content_flags = models.CharField(max_length=100, null=True, default=None)
    content_flags_disabled = models.CharField(max_length=100, null=True, default=None)

    class Meta:
        db_table = 'lootdrop_entries'
        managed = False
