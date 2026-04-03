from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magelo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='characterpermissions',
            name='wishlist_public',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='WishlistEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character_name', models.CharField(db_index=True, max_length=64)),
                ('item_id', models.IntegerField()),
                ('item_name', models.CharField(max_length=200)),
                ('priority', models.PositiveSmallIntegerField(default=0)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Wishlist Entry',
                'verbose_name_plural': 'Wishlist Entries',
                'ordering': ['priority', 'created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='wishlistentry',
            unique_together={('character_name', 'item_id')},
        ),
    ]
