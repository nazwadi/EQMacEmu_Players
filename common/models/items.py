from django.db import models


class Items(models.Model):
    """
    This model maps to the items table in the database.
    """
    def __str__(self):
        return str(self.id)

    id = models.IntegerField(primary_key=True, null=False, default=0)
    minstatus = models.SmallIntegerField(null=False, default=0)
    Name = models.CharField(max_length=64, null=False, default=0)
    aagi = models.IntegerField(null=False, default=0)
    acha = models.IntegerField(null=False, default=0)
    adex = models.IntegerField(null=False, default=0)
    aint = models.IntegerField(null=False, default=0)
    asta = models.IntegerField(null=False, default=0)
    astr = models.IntegerField(null=False, default=0)
    awis = models.IntegerField(null=False, default=0)
    hp = models.IntegerField(null=False, default=0)
    mana = models.IntegerField(null=False, default=0)
    fr = models.IntegerField(null=False, default=0)
    dr = models.IntegerField(null=False, default=0)
    cr = models.IntegerField(null=False, default=0)
    mr = models.IntegerField(null=False, default=0)
    pr = models.IntegerField(null=False, default=0)
    max_charges = models.IntegerField(null=False, default=0, db_column='maxcharges')
    scroll_effect = models.IntegerField(null=False, default=0, db_column='scrolleffect')
    scroll_type = models.IntegerField(null=False, default=0, db_column='scrolltype')
    source = models.CharField(max_length=20, null=False)
    icon = models.IntegerField(null=False, default=0)
    price = models.IntegerField(null=False, default=0)
    no_drop = models.IntegerField(null=False, default=0, db_column='nodrop')
    no_rent = models.IntegerField(null=False, default=0, db_column='norent')
    lore = models.CharField(max_length=80, null=False)
    magic = models.IntegerField(null=False, default=0)
    slots = models.IntegerField(null=False, default=0)
    ac = models.IntegerField(null=False, default=0)
    stackable = models.IntegerField(null=False, default=0)
    click_effect = models.IntegerField(null=False, default=0, db_column='clickeffect')
    click_type = models.IntegerField(null=False, default=0, db_column='clicktype')
    worn_effect = models.IntegerField(null=False, default=0, db_column='worneffect')
    worn_type = models.IntegerField(null=False, default=0, db_column='worntype')
    proc_effect = models.IntegerField(null=False, default=0, db_column='proceffect')
    cast_time = models.IntegerField(null=False, default=0, db_column='casttime')
    weight = models.IntegerField(null=False, default=0)
    size = models.IntegerField(null=False, default=0)
    item_type = models.IntegerField(null=False, default=0, db_column='itemtype')
    delay = models.IntegerField(null=False, default=0)
    classes = models.IntegerField(null=False, default=0)
    races = models.IntegerField(null=False, default=0)
    damage = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'items'
        managed = False


