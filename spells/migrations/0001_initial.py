from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Initial migration capturing the pre-existing spell_expansion table.
    Run with --fake-initial so Django marks it applied without
    attempting to CREATE TABLE on a table that already exists.
    """

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SpellExpansion',
            fields=[
                ('id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('expansion', models.IntegerField(
                    choices=[
                        (0, 'Original EverQuest'), (1, 'Ruins of Kunark'), (2, 'Scars of Velious'),
                        (3, 'Shadows of Luclin'), (4, 'Planes of Power'), (5, 'Legacy of Ykesha'),
                        (6, 'Lost Dungeons of Norrath'), (7, 'Gates of Discord'), (8, 'Omens of War'),
                        (9, 'Dragons of Norrath'), (10, 'Depths of Darkhollow'),
                    ],
                    default=0,
                )),
            ],
            options={
                'db_table': 'spell_expansion',
            },
        ),
    ]
