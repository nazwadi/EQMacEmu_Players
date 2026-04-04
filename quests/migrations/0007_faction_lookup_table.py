"""
Migration 1 of 2 for faction normalization.
Creates the Faction lookup table. Renames the existing faction_id integer columns
to old_faction_id first (to avoid a column name collision when the FK field
'faction' is added — Django names that column faction_id too), then adds the
nullable faction FKs so the data migration in 0008 can populate them.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0006_patch_history_notes_issue_reports'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('faction_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Faction',
                'verbose_name_plural': 'Factions',
                'ordering': ['name'],
            },
        ),
        # Rename conflicting columns before adding FK (which also creates a faction_id column)
        migrations.RenameField(
            model_name='questfaction',
            old_name='faction_id',
            new_name='old_faction_id',
        ),
        migrations.RenameField(
            model_name='factionreward',
            old_name='faction_id',
            new_name='old_faction_id',
        ),
        # Add nullable FKs — Django will now create faction_id columns without conflict
        migrations.AddField(
            model_name='questfaction',
            name='faction',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='quest_factions',
                to='quests.faction',
            ),
        ),
        migrations.AddField(
            model_name='factionreward',
            name='faction',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='faction_rewards',
                to='quests.faction',
            ),
        ),
    ]
