from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('npcs', '0001_initial'),
        ('patch', '0006_patch_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='NPCPatchHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('npc_id', models.IntegerField(help_text='Game-DB NPC id (npc_types.id)')),
                ('npc_name', models.CharField(help_text='Denormalized name for display (game DB is read-only).', max_length=64)),
                ('role', models.CharField(
                    choices=[('introduced', 'Introduced'), ('updated', 'Updated')],
                    default='updated',
                    help_text=(
                        "Use 'Updated' for stat/loot/spawn changes documented in the patch. "
                        "Only use 'Introduced' when the NPC was genuinely added mid-expansion "
                        "by this specific patch — expansion-launch NPCs should not have an "
                        "'Introduced' entry here."
                    ),
                    max_length=10,
                )),
                ('notes', models.TextField(blank=True, help_text='What changed and how this may differ from P99 wiki or Allakhazam.')),
                ('patch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='npc_history', to='patch.patchmessage')),
            ],
            options={
                'verbose_name': 'NPC Patch History',
                'verbose_name_plural': 'NPC Patch Histories',
                'ordering': ['patch__patch_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='npcpatchhistory',
            unique_together={('npc_id', 'patch', 'role')},
        ),
    ]
