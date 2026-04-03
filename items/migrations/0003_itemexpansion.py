from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_bisrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemExpansionIdRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expansion', models.IntegerField(choices=[
                    (0, 'Original EverQuest'), (1, 'Ruins of Kunark'), (2, 'Scars of Velious'),
                    (3, 'Shadows of Luclin'), (4, 'Planes of Power'), (5, 'Legacy of Ykesha'),
                    (6, 'Lost Dungeons of Norrath'), (7, 'Gates of Discord'), (8, 'Omens of War'),
                    (9, 'Dragons of Norrath'), (10, 'Depths of Darkhollow'), (11, 'Prophecy of Ro'),
                    (12, "The Serpent's Spine"), (13, 'The Buried Sea'), (14, 'Secrets of Faydwer'),
                    (15, 'Seeds of Destruction'), (16, 'Underfoot'), (17, 'House of Thule'),
                    (18, 'Veil of Alaris'), (19, 'Rain of Fear'), (20, 'Call of the Forsaken'),
                    (21, 'The Darkened Sea'), (22, 'The Broken Mirror'), (23, 'Empires of Kunark'),
                    (24, 'Ring of Scale'), (25, 'The Burning Lands'), (26, 'Torment of Velious'),
                    (27, 'Claws of Veeshan'), (28, 'Terror of Luclin'), (29, 'Night of Shadows'),
                    (30, "Laurion's Song"), (31, 'The Outer Brood'),
                ])),
                ('min_item_id', models.IntegerField()),
                ('max_item_id', models.IntegerField(
                    blank=True, null=True,
                    help_text='Exclusive upper bound. Leave blank for "this expansion and above".',
                )),
            ],
            options={
                'verbose_name': 'Item Expansion ID Range',
                'verbose_name_plural': 'Item Expansion ID Ranges',
                'ordering': ['min_item_id'],
            },
        ),
        migrations.CreateModel(
            name='ItemExpansion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.IntegerField(unique=True)),
                ('expansion', models.IntegerField(choices=[
                    (0, 'Original EverQuest'), (1, 'Ruins of Kunark'), (2, 'Scars of Velious'),
                    (3, 'Shadows of Luclin'), (4, 'Planes of Power'), (5, 'Legacy of Ykesha'),
                    (6, 'Lost Dungeons of Norrath'), (7, 'Gates of Discord'), (8, 'Omens of War'),
                    (9, 'Dragons of Norrath'), (10, 'Depths of Darkhollow'), (11, 'Prophecy of Ro'),
                    (12, "The Serpent's Spine"), (13, 'The Buried Sea'), (14, 'Secrets of Faydwer'),
                    (15, 'Seeds of Destruction'), (16, 'Underfoot'), (17, 'House of Thule'),
                    (18, 'Veil of Alaris'), (19, 'Rain of Fear'), (20, 'Call of the Forsaken'),
                    (21, 'The Darkened Sea'), (22, 'The Broken Mirror'), (23, 'Empires of Kunark'),
                    (24, 'Ring of Scale'), (25, 'The Burning Lands'), (26, 'Torment of Velious'),
                    (27, 'Claws of Veeshan'), (28, 'Terror of Luclin'), (29, 'Night of Shadows'),
                    (30, "Laurion's Song"), (31, 'The Outer Brood'),
                ])),
                ('source', models.CharField(
                    choices=[('zone', 'Zone Provenance'), ('id_range', 'Item ID Range'), ('manual', 'Manual Override')],
                    default='zone',
                    max_length=16,
                )),
                ('is_override', models.BooleanField(
                    default=False,
                    help_text='When checked, compute_item_expansions will never overwrite this entry.',
                )),
            ],
            options={
                'verbose_name': 'Item Expansion',
                'verbose_name_plural': 'Item Expansions',
                'ordering': ['item_id'],
            },
        ),
    ]
