from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raid_scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='raidevent',
            name='timezone',
            field=models.CharField(
                default='America/New_York',
                max_length=50,
            ),
        ),
    ]
