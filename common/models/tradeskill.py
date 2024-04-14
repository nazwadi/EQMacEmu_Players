from django.db import models
from common.models.items import Items


class TradeskillRecipe(models.Model):
    """
    This model maps to the items table in the database.
    """
    def __str__(self):
        return str(self.name)

    id = models.BigAutoField(primary_key=True, null=False, default=0)
    name = models.CharField(max_length=64, null=False, default=0)
    tradeskill = models.SmallIntegerField(null=False, default=0)
    skill_needed = models.SmallIntegerField(null=False, default=0, db_column='skillneeded')
    trivial = models.SmallIntegerField(null=False, default=0)
    no_fail = models.SmallIntegerField(null=False, default=0, db_column='nofail')
    replace_container = models.SmallIntegerField(null=False, default=0)
    notes = models.TextField(null=True, blank=True)
    quest = models.SmallIntegerField(null=False, default=0)
    enabled = models.SmallIntegerField(null=False, default=1)

    class Meta:
        db_table = 'tradeskill_recipe'
        managed = False


class TradeskillRecipeEntries(models.Model):
    """
    This model maps to the items table in the database.
    """
    def __str__(self):
        return str(self.id)

    id = models.BigAutoField(primary_key=True, null=False, default=0)
    recipe_id = models.OneToOneField(TradeskillRecipe, on_delete=models.DO_NOTHING, db_column='recipe_id')
    item_id = models.OneToOneField(Items, on_delete=models.DO_NOTHING, db_column='item_id')
    success_count = models.SmallIntegerField(null=False, default=0, db_column='successcount')
    fail_count = models.SmallIntegerField(null=False, default=0, db_column='failcount')
    component_count = models.SmallIntegerField(null=False, default=1, db_column='componentcount')
    is_container = models.SmallIntegerField(null=False, default=0, db_column='iscontainer')

    class Meta:
        db_table = 'tradeskill_recipe_entries'
        managed = False

