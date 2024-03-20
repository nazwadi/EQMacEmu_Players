from django.db import models


class SpellsNew(models.Model):
    """
    This model maps to the spells_new table in the database.
    """
    id = models.IntegerField(primary_key=True, null=False, default=0)
    name = models.CharField(max_length=64, null=True, default=None)
    icon = models.IntegerField(null=False, default=0)
    mem_icon = models.IntegerField(null=False, default=0, db_column='memicon')
    skill = models.IntegerField(null=False, default=98)
    mana = models.IntegerField(null=False, default=0)
    custom_icon = models.IntegerField(null=True, default=0)
    classes1 = models.IntegerField(null=True, default=255)
    classes2 = models.IntegerField(null=True, default=255)
    classes3 = models.IntegerField(null=True, default=255)
    classes4 = models.IntegerField(null=True, default=255)
    classes5 = models.IntegerField(null=True, default=255)
    classes6 = models.IntegerField(null=True, default=255)
    classes7 = models.IntegerField(null=True, default=255)
    classes8 = models.IntegerField(null=True, default=255)
    classes9 = models.IntegerField(null=True, default=255)
    classes10 = models.IntegerField(null=True, default=255)
    classes11 = models.IntegerField(null=True, default=255)
    classes12 = models.IntegerField(null=True, default=255)
    classes13 = models.IntegerField(null=True, default=255)
    classes14 = models.IntegerField(null=True, default=255)
    classes15 = models.IntegerField(null=True, default=255)
    not_player_spell = models.IntegerField(null=True, default=0)
    target_type = models.IntegerField(null=False, default=2, db_column='targettype')

    class Meta:
        db_table = 'spells_new'
        managed = False

