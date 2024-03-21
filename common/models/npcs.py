from django.db import models


class NPCFaction(models.Model):
    """
    This model maps to the npc_faction table in the database
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False, default=None)
    name = models.TextField(null=True)
    primary_faction = models.IntegerField(null=False, default=0, db_column='primaryfaction')
    ignore_primary_assist = models.SmallIntegerField(null=False, default=0)

    class Meta:
        managed = False
        db_table = 'npc_faction'


class NPCFactionEntries(models.Model):
    """
    This model maps to the npc_faction_entries table in the database
    """
    def __str__(self):
        return str(self.id)

    class Meta:
        managed = False
        db_table = 'npc_faction_entries'


class NPCSpellsEntries(models.Model):
    """
    This model maps to the npc_spells_entries table in the database
    """
    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False, default=None)
    npc_spells_id = models.IntegerField(null=False, default=0)
    spellid = models.SmallIntegerField(null=False, default=0)
    type = models.SmallIntegerField(null=False, default=0)
    minlevel = models.SmallIntegerField(null=False, default=0)
    maxlevel = models.SmallIntegerField(null=False, default=255)
    manacost = models.SmallIntegerField(null=False, default=-1)
    recast_delay = models.IntegerField(null=False, default=-1)
    priority = models.SmallIntegerField(null=False, default=0)
    resist_adjust = models.IntegerField(null=True, default=None)

    class Meta:
        managed = False
        db_table = "npc_spells_entries"


class NPCTypes(models.Model):
    """
    This model maps to the npc_types table in the database.
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False)
    name = models.TextField(unique=True, null=False, default=None)
    lastname = models.CharField(max_length=32, null=True, default=None)
    race = models.SmallIntegerField(null=False, default=0)
    level = models.SmallIntegerField(null=False, default=0)
    max_level = models.SmallIntegerField(null=False, default=0, db_column='maxlevel')
    class_name = models.SmallIntegerField(null=False, default=0, db_column='class')
    hp = models.IntegerField(null=False, default=0)
    mana = models.IntegerField(null=False, default=0)
    min_dmg = models.IntegerField(null=False, default=0, db_column='mindmg')
    max_dmg = models.IntegerField(null=False, default=0, db_column='maxdmg')
    npc_faction_id = models.IntegerField(null=False, default=0)
    npc_spells_id = models.IntegerField(null=False, default=0)
    ac = models.SmallIntegerField(null=False, default=0, db_column='AC')
    attack_count = models.SmallIntegerField(null=False, default=-1)
    MR = models.SmallIntegerField(null=False, default=0)
    CR = models.SmallIntegerField(null=False, default=0)
    DR = models.SmallIntegerField(null=False, default=0)
    FR = models.SmallIntegerField(null=False, default=0)
    PR = models.SmallIntegerField(null=False, default=0)
    special_abilities = models.TextField(null=True, default=None)

    class Meta:
        db_table = "npc_types"
        managed = False
