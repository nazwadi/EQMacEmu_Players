from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0004_itemexpansion_expansion_index'),
        ('patch', '0006_patch_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemPatchHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.IntegerField(help_text='Game-DB item id (items.id)')),
                ('item_name', models.CharField(help_text='Denormalized name for display (game DB is read-only).', max_length=128)),
                ('role', models.CharField(
                    choices=[('introduced', 'Introduced'), ('updated', 'Updated')],
                    default='updated',
                    help_text=(
                        "Use 'Updated' for stat/flag/effect changes documented in the patch. "
                        "Only use 'Introduced' when the item was genuinely added mid-expansion "
                        "by this specific patch — ItemExpansion handles expansion-launch items."
                    ),
                    max_length=10,
                )),
                ('notes', models.TextField(blank=True, help_text='What changed and how this may differ from P99 wiki or Allakhazam.')),
                ('patch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_history', to='patch.patchmessage')),
            ],
            options={
                'verbose_name': 'Item Patch History',
                'verbose_name_plural': 'Item Patch Histories',
                'ordering': ['patch__patch_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='itempatchhistory',
            unique_together={('item_id', 'patch', 'role')},
        ),
    ]
