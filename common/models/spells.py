from django.db import models


class SpellsNew(models.Model):
    """
    This model maps to the spells_new table in the database.
    """
    id = models.IntegerField(primary_key=True, null=False, default=0)
    name = models.CharField(max_length=64, null=True, default=None)
    you_cast = models.CharField(max_length=120, null=True, default=None)
    other_casts = models.CharField(max_length=120, null=True, default=None)
    cast_on_you = models.CharField(max_length=120, null=True, default=None)
    cast_on_other = models.CharField(max_length=120, null=True, default=None)
    spell_fades = models.CharField(max_length=120, null=True, default=None)
    icon = models.IntegerField(null=False, default=0)
    mem_icon = models.IntegerField(null=False, default=0, db_column='memicon')
    skill = models.IntegerField(null=False, default=98)
    mana = models.IntegerField(null=False, default=0)
    buff_duration = models.IntegerField(null=False, default=0, db_column='buffduration')
    buff_duration_formula = models.IntegerField(null=False, default=7, db_column='buffdurationformula')
    range = models.IntegerField(null=False, default=100)
    aoe_range = models.IntegerField(null=False, default=0, db_column='aoerange')
    cast_time = models.IntegerField(null=False, default=0)
    recovery_time = models.IntegerField(null=False, default=0)
    recast_time = models.IntegerField(null=False, default=0)
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
    components1 = models.IntegerField(null=False, default=-1)
    components2 = models.IntegerField(null=False, default=-1)
    components3 = models.IntegerField(null=False, default=-1)
    components4 = models.IntegerField(null=False, default=-1)
    component_counts1 = models.IntegerField(null=False, default=1)
    component_counts2 = models.IntegerField(null=False, default=1)
    component_counts3 = models.IntegerField(null=False, default=1)
    component_counts4 = models.IntegerField(null=False, default=1)
    effect_base_value1 = models.IntegerField(null=True, default=100)
    not_player_spell = models.IntegerField(null=True, default=0)
    target_type = models.IntegerField(null=False, default=2, db_column='targettype')
    resist_type = models.IntegerField(null=False, default=2, db_column='resisttype')
    resist_diff = models.IntegerField(null=False, default=-150, db_column='resistdiff')
    time_of_day = models.IntegerField(null=False, default=0, db_column='TimeOfDay')
    zone_type = models.IntegerField(null=False, default=-1, db_column='zonetype')
    spell_category = models.IntegerField(null=False, default=-99)

    class Meta:
        db_table = 'spells_new'
        managed = False

