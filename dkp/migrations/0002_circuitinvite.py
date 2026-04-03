import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dkp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CircuitInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='Leave blank for no expiry', null=True)),
                ('max_uses', models.PositiveIntegerField(default=1, help_text='0 = unlimited')),
                ('use_count', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('note', models.CharField(blank=True, help_text='Optional label, e.g. who this is for', max_length=200)),
                ('circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='dkp.raidcircuit')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_circuit_invites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
