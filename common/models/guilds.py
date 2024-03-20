from django.db import models
from django.db.models import SmallIntegerField
from common.models.characters import Characters


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
        db_table = 'guilds'
        managed = False


class GuildMembers(models.Model):
    """
    This model maps to the guild_members table in the database.
    """

    def __str__(self):
        return self.char_id

    char_id = models.OneToOneField(Characters, primary_key=True, on_delete=models.RESTRICT, db_column='char_id')
    guild_id = models.OneToOneField(Guilds, on_delete=models.RESTRICT, db_column='guild_id')
    rank = models.SmallIntegerField(null=False, default=0)
    tribute_enable = models.SmallIntegerField(null=False, default=0)
    total_tribute = models.IntegerField(null=False, default=0)
    last_tribute = models.IntegerField(null=False, default=0)
    banker = models.SmallIntegerField(null=False, default=0)
    public_note = models.TextField(null=False, default=None)
    alt = SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = 'guild_members'
        managed = False
