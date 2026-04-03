from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Represents the CharacterPermissions table as it existed before Django
    migrations were set up for this app. Run with --fake on first deploy:

        python manage.py migrate magelo 0001 --fake
    """

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CharacterPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character_name', models.CharField(max_length=64, unique=True)),
                ('inventory', models.BooleanField(default=False)),
                ('bags', models.BooleanField(default=False)),
                ('bank', models.BooleanField(default=False)),
                ('coin_inventory', models.BooleanField(default=False)),
                ('coin_bank', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Character Permissions',
                'verbose_name_plural': 'Character Permissions',
            },
        ),
    ]
