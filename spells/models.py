from django.db import models


class SpellExpansion(models.Model):
    """
    Build a database to map spells to the expansion they were first introduced.

    Purpose is to provide expansion filtering options for spell lists.
    """
    EXPANSION_CHOICES = [
        (0, 'Original EverQuest'),
        (1, 'Ruins of Kunark'),
        (2, 'Scars of Velious'),
        (3, 'Shadows of Luclin'),
        (4, 'Planes of Power'),
        (5, 'Legacy of Ykesha'),
        (6, 'Lost Dungeons of Norrath'),
        (7, 'Gates of Discord'),
        (8, 'Omens of War'),
        (9, 'Omens of War'),
    ]
    id = models.IntegerField(primary_key=True, null=False, default=0)
    # 0 - Original, 1 - Kunark, 2 - Velious, 3- Luclin, 4- PoP, 5 - LoY, etc...
    expansion = models.IntegerField(null=False, default=0, choices=EXPANSION_CHOICES)

    class Meta:
        db_table = 'spell_expansion'
