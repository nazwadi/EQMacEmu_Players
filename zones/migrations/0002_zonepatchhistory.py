from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0001_initial'),
        ('patch', '0006_patch_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZonePatchHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone_short_name', models.CharField(help_text="Zone short name (e.g. 'qeynos', 'commons'). Matches zone.short_name in the game DB.", max_length=32)),
                ('zone_long_name', models.CharField(help_text='Denormalized display name (game DB is read-only).', max_length=128)),
                ('role', models.CharField(
                    choices=[('introduced', 'Introduced'), ('updated', 'Updated')],
                    default='updated',
                    help_text=(
                        "Use 'Updated' for content/mob/loot changes documented in the patch. "
                        "Only use 'Introduced' when a zone opened mid-expansion via this patch."
                    ),
                    max_length=10,
                )),
                ('notes', models.TextField(blank=True, help_text='What changed and how this may differ from P99 wiki or Allakhazam.')),
                ('patch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zone_history', to='patch.patchmessage')),
            ],
            options={
                'verbose_name': 'Zone Patch History',
                'verbose_name_plural': 'Zone Patch Histories',
                'ordering': ['patch__patch_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='zonepatchhistory',
            unique_together={('zone_short_name', 'patch', 'role')},
        ),
    ]
