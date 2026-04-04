"""
Migration 2 of 2 for faction normalization.
Populates the Faction table from existing denormalized rows, then removes the
old faction_id/name/faction_name fields from QuestFaction and FactionReward.
"""
from django.db import migrations, models
import django.db.models.deletion


def populate_factions(apps, schema_editor):
    QuestFaction = apps.get_model('quests', 'QuestFaction')
    FactionReward = apps.get_model('quests', 'FactionReward')
    Faction = apps.get_model('quests', 'Faction')

    for qf in QuestFaction.objects.all():
        faction, _ = Faction.objects.get_or_create(
            faction_id=qf.old_faction_id,
            defaults={'name': qf.name},
        )
        qf.faction = faction
        qf.save()

    for fr in FactionReward.objects.all():
        faction, _ = Faction.objects.get_or_create(
            faction_id=fr.old_faction_id,
            defaults={'name': fr.faction_name},
        )
        fr.faction = faction
        fr.save()


def reverse_populate_factions(apps, schema_editor):
    QuestFaction = apps.get_model('quests', 'QuestFaction')
    FactionReward = apps.get_model('quests', 'FactionReward')

    for qf in QuestFaction.objects.select_related('faction').all():
        qf.old_faction_id = qf.faction.faction_id
        qf.name = qf.faction.name
        qf.save()

    for fr in FactionReward.objects.select_related('faction').all():
        fr.old_faction_id = fr.faction.faction_id
        fr.faction_name = fr.faction.name
        fr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0007_faction_lookup_table'),
    ]

    operations = [
        # Populate Faction table and set FKs
        migrations.RunPython(populate_factions, reverse_populate_factions),

        # QuestFaction: drop old unique_together, make FK non-null, add new unique_together, remove old fields, update index
        migrations.AlterUniqueTogether(
            name='questfaction',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='questfaction',
            name='faction',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='quest_factions',
                to='quests.faction',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='questfaction',
            unique_together={('quest', 'faction', 'role')},
        ),
        migrations.RemoveField(
            model_name='questfaction',
            name='old_faction_id',
        ),
        migrations.RemoveField(
            model_name='questfaction',
            name='name',
        ),

        # FactionReward: make FK non-null, remove old fields, swap indexes
        migrations.AlterField(
            model_name='factionreward',
            name='faction',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='faction_rewards',
                to='quests.faction',
            ),
        ),
        migrations.RemoveIndex(
            model_name='factionreward',
            name='reward_faction_id_idx',
        ),
        migrations.RemoveIndex(
            model_name='factionreward',
            name='reward_faction_name_idx',
        ),
        migrations.AddIndex(
            model_name='factionreward',
            index=models.Index(fields=['faction'], name='reward_faction_idx'),
        ),
        migrations.RemoveField(
            model_name='factionreward',
            name='old_faction_id',
        ),
        migrations.RemoveField(
            model_name='factionreward',
            name='faction_name',
        ),
    ]
