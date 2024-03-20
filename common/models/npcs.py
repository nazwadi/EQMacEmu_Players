from django.db import models


class NPCTypes(models.Model):
    """
    This model maps to the npc_types table in the database.
    """

    def __str__(self):
        return str(self.id)

    id = models.AutoField(primary_key=True, null=False)
    name = models.TextField(unique=True, null=False, default=None)

    class Meta:
        db_table = "npc_types"
        managed = False
