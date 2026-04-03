from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raid_scheduler', '0002_raidevent_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='raidevent',
            name='is_visible',
            field=models.BooleanField(
                default=True,
                help_text='Visible on the public board. Eligible for GM reservation protection.',
            ),
        ),
        migrations.AddField(
            model_name='raidevent',
            name='is_open',
            field=models.BooleanField(
                default=True,
                help_text='Open to all players. When False, attendance is restricted to circuit members.',
            ),
        ),
        # Data migration: is_public=True → visible+open, is_public=False → hidden+closed
        migrations.RunSQL(
            sql='UPDATE raid_scheduler_raidevent SET is_visible = is_public, is_open = is_public',
            reverse_sql='UPDATE raid_scheduler_raidevent SET is_public = is_visible',
        ),
        migrations.RemoveField(
            model_name='raidevent',
            name='is_public',
        ),
    ]
