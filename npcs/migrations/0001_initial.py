from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Initial migration capturing the pre-existing NpcPage table.
    Run with --fake-initial so Django marks it applied without
    attempting to CREATE TABLE on a table that already exists.
    """

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NpcPage',
            fields=[
                ('npc_id', models.IntegerField(default=None, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True)),
                ('portrait', models.TextField(blank=True)),
                ('related_quests', models.TextField(blank=True)),
            ],
        ),
    ]
