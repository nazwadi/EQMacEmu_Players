from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Initial migration capturing the pre-existing ZonePage table.
    Run with --fake-initial so Django marks it applied without
    attempting to CREATE TABLE on a table that already exists.
    """

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ZonePage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('short_name', models.CharField(blank=True, default=None, max_length=32, null=True)),
                ('level_of_monsters', models.TextField(blank=True, default=None, null=True)),
                ('types_of_monsters', models.TextField(blank=True, default=None, null=True)),
                ('description', models.TextField(blank=True)),
                ('map', models.TextField(blank=True)),
                ('dangers', models.TextField(blank=True)),
                ('benefits', models.TextField(blank=True)),
                ('travel_to_from', models.TextField(blank=True)),
                ('history_lore', models.TextField(blank=True)),
            ],
        ),
    ]
