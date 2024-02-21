from django.db import models
from django.db.models import SmallIntegerField


class Characters(models.Model):
    """
    This model maps to the character_data table in the database.
    """

    def __str__(self):
        return self.name

    id = models.AutoField(primary_key=True)
    account_id = models.IntegerField(default=0, null=False)
    forum_id = models.IntegerField(default=0, null=False)
    name = models.CharField(max_length=64, default='', unique=True, null=False, blank=True)
    last_name = models.CharField(max_length=64, default='', null=False, blank=True)
    title = models.CharField(max_length=32, default='', null=False, blank=True)
    suffix = models.CharField(max_length=32, default='', null=False, blank=True)
    zone_id = models.IntegerField(default='0', null=False)
    y = models.FloatField(default=0, null=False)
    x = models.FloatField(default=0, null=False)
    z = models.FloatField(default=0, null=False)
    heading = models.FloatField(default=0, null=False)
    gender = models.SmallIntegerField(default='0', null=False)
    race = models.SmallIntegerField(default='0', null=False)
    class_name = models.SmallIntegerField(default='0', null=False, db_column="`class`")
    level = models.IntegerField(default='0', null=False)
    deity = models.IntegerField(default='0', null=False)
    birthday = models.IntegerField(default='0', null=False)
    last_login = models.IntegerField(default='0', null=False)
    time_played = models.IntegerField(default='0', null=False)
    level2 = models.SmallIntegerField(default='0', null=False)
    anon = models.SmallIntegerField(default='0', null=False)
    gm = models.SmallIntegerField(default='0', null=False)
    face = models.IntegerField(default='0', null=False)
    hair_color = models.SmallIntegerField(default='0', null=False)
    hair_style = models.SmallIntegerField(default='0', null=False)
    beard = models.SmallIntegerField(default='0', null=False)
    beard_color = models.SmallIntegerField(default='0', null=False)
    eye_color_1 = models.SmallIntegerField(default='0', null=False)
    eye_color_2 = models.SmallIntegerField(default='0', null=False)
    exp = models.IntegerField(default='0', null=False)
    aa_points_spent = models.IntegerField(default='0', null=False)
    aa_exp = models.IntegerField(default='0', null=False)
    aa_points = models.IntegerField(default='0', null=False)
    points = models.IntegerField(default='0', null=False)
    cur_hp = models.IntegerField(default='0', null=False)
    mana = models.IntegerField(default='0', null=False)
    endurance = models.IntegerField(default='0', null=False)
    intoxication = models.IntegerField(default='0', null=False)
    str = models.IntegerField(default='0', null=False)
    sta = models.IntegerField(default='0', null=False)
    cha = models.IntegerField(default='0', null=False)
    dex = models.IntegerField(default='0', null=False)
    int_stat = models.IntegerField(default='0', null=False, db_column='`int`')
    agi = models.IntegerField(default='0', null=False)
    wis = models.IntegerField(default='0', null=False)
    zone_change_count = models.IntegerField(default='0', null=False)
    hunger_level = models.IntegerField(default='0', null=False)
    thirst_level = models.IntegerField(default='0', null=False)
    pvp_status = models.SmallIntegerField(default='0', null=False)
    air_remaining = models.IntegerField(default='0', null=False)
    autosplit_enabled = models.IntegerField(default='0', null=False)
    mailkey = models.CharField(max_length=16, default='', null=False)
    firstlogon = models.SmallIntegerField(default=0, null=False)
    e_aa_effects = models.IntegerField(default='0', null=False)
    e_percent_to_aa = models.IntegerField(default='0', null=False)
    e_expended_aa_spent = models.IntegerField(default='0', null=False)
    boatid = models.IntegerField(default='0', null=False)
    boatname = models.CharField(max_length=25, null=True)
    famished = models.IntegerField(default=0, null=False)
    is_deleted = models.SmallIntegerField(default=0, null=False)
    showhelm = models.SmallIntegerField(default=1, null=False)
    fatigue = models.IntegerField(default=0, null=True)
    e_self_found = models.SmallIntegerField(default=0, null=False)
    e_solo_only = models.SmallIntegerField(default=0, null=False)
    e_hardcore = models.SmallIntegerField(default=0, null=False)
    e_hardcore_death_time = models.BigIntegerField(default=0, null=False)
    e_betabuff_gear_flag = models.SmallIntegerField(default='0', null=False)

    class Meta:
        db_table = "character_data"
        verbose_name_plural = 'Characters'


class CharacterFactionValues(models.Model):
    """
    This model maps to the character_faction_values table in the database.
    """

    def __str__(self):
        return str(self.faction_id)

    id = models.IntegerField(primary_key=True, null=False, default=None)
    faction_id = models.IntegerField(null=False, unique=True, default=None)
    current_value = SmallIntegerField(null=False, default=0)
    temp = SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = "character_faction_values"


class CharacterSkills(models.Model):
    """
    This model maps to the character_skills table in the database.
    """

    def __str__(self):
        return self.skill_id

    id = models.IntegerField(primary_key=True, null=False, default=None)
    skill_id = models.SmallIntegerField(null=False, default=0)
    value = SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = "character_skills"


class CharacterCurrency(models.Model):
    """
    This model maps to the character_currency table in the database.
    """

    def __str__(self):
        return self.id

    id = models.IntegerField(primary_key=True, null=False, default=0)
    platinum = models.IntegerField(null=False, default=0)
    gold = models.IntegerField(null=False, default=0)
    silver = models.IntegerField(null=False, default=0)
    copper = models.IntegerField(null=False, default=0)
    platinum_bank = models.IntegerField(null=False, default=0)
    gold_bank = models.IntegerField(null=False, default=0)
    silver_bank = models.IntegerField(null=False, default=0)
    copper_bank = models.IntegerField(null=False, default=0)
    platinum_cursor = models.IntegerField(null=False, default=0)
    gold_cursor = models.IntegerField(null=False, default=0)
    silver_cursor = models.IntegerField(null=False, default=0)
    copper_cursor = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'character_currency'


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

    class Meta:
        db_table = 'items'


class CharacterKeyring(models.Model):
    """
    This model maps to the character_keyring table in the database
    """
    def __str__(self):
        return self.item_id.id

    id = models.ForeignKey(Characters, primary_key=True, on_delete=models.RESTRICT, db_column='id')
    item_id = models.ForeignKey(Items, on_delete=models.RESTRICT, db_column='item_id')
#    item_id = models.IntegerField(null=False, default=0, db_column='item_id')

    class Meta:
        db_table = 'character_keyring'


class CharacterLanguages(models.Model):
    """
    This model maps to the character_languages table in the database
    """

    def __str__(self):
        return self.id

    id = models.IntegerField(primary_key=True, null=False, default=None)
    lang_id = models.SmallIntegerField(null=False, default=0)
    value = SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = "character_languages"


class SpellsNew(models.Model):
    """
    This model maps to the spells_new table in the database.
    """
    id = models.IntegerField(primary_key=True, null=False, default=0)
    name = models.CharField(max_length=64, null=True, default=None)
    icon = models.IntegerField(null=False, default=0)
    memicon = models.IntegerField(null=False, default=0)
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
    targettype = models.IntegerField(null=False, default=2)

    class Meta:
        managed = True
        db_table = 'spells_new'


class CharacterSpells(models.Model):
    """
    This model maps to the character_spells table in the database.
    """

    def __str__(self):
        return self.spell_id

    id = models.IntegerField(primary_key=True, null=False, default=0)
    slot_id = models.SmallIntegerField(null=False, default=0)
    spell_id = models.ForeignKey(SpellsNew, on_delete=models.RESTRICT, db_column='spell_id')

    class Meta:
        managed = True
        db_table = 'character_spells'


class Guilds(models.Model):
    """
    This model maps to the guilds table in the database
    """

    def __str__(self):
        return str(self.id)

    id = models.IntegerField(primary_key=True, null=False, default=None)
    name = models.CharField(max_length=32, null=False, unique=True)
    leader = models.IntegerField(null=False, unique=True, default=0)
    minstatus = SmallIntegerField(null=False, default=0)
    motd = models.TextField(null=False, default=None)
    tribute = models.IntegerField(null=False, default=0)
    motd_setter = models.CharField(max_length=64, null=False)
    channel = models.CharField(max_length=128, null=False)
    url = models.CharField(max_length=512, null=False)

    class Meta:
        managed = True
        db_table = 'guilds'


class GuildMembers(models.Model):
    """
    This model maps to the guild_members table in the database.
    """

    def __str__(self):
        return self.char_id

    char_id = models.ForeignKey(Characters, primary_key=True, on_delete=models.RESTRICT, db_column='char_id')
    guild_id = models.ForeignKey(Guilds, on_delete=models.RESTRICT, db_column='guild_id')
    rank = models.SmallIntegerField(null=False, default=0)
    tribute_enable = models.SmallIntegerField(null=False, default=0)
    total_tribute = models.IntegerField(null=False, default=0)
    last_tribute = models.IntegerField(null=False, default=0)
    banker = models.SmallIntegerField(null=False, default=0)
    public_note = models.TextField(null=False, default=None)
    alt = SmallIntegerField(null=False, default=0)

    class Meta:
        managed = True
        db_table = 'guild_members'
