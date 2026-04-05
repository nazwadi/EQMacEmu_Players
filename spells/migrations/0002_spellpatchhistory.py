from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spells', '0001_initial'),
        ('patch', '0006_patch_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpellPatchHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spell_id', models.IntegerField(help_text='Game-DB spell id (spells_new.id)')),
                ('spell_name', models.CharField(help_text='Denormalized name for display (game DB is read-only).', max_length=64)),
                ('role', models.CharField(
                    choices=[('introduced', 'Introduced'), ('updated', 'Updated')],
                    default='updated',
                    help_text=(
                        "Use 'Updated' for changes documented in the patch. "
                        "Only use 'Introduced' when the spell was genuinely added "
                        "mid-expansion by this patch — SpellExpansion handles the rest."
                    ),
                    max_length=10,
                )),
                ('notes', models.TextField(blank=True, help_text='What changed and how this may differ from P99 wiki or Allakhazam.')),
                ('patch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spell_history', to='patch.patchmessage')),
            ],
            options={
                'verbose_name': 'Spell Patch History',
                'verbose_name_plural': 'Spell Patch Histories',
                'ordering': ['patch__patch_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='spellpatchhistory',
            unique_together={('spell_id', 'patch', 'role')},
        ),
    ]
