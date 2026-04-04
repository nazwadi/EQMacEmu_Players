from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0005_add_quest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='questpatchhistory',
            name='notes',
            field=models.TextField(blank=True, help_text='Staff note: what changed and how this may differ from P99 wiki or Allakhazam'),
        ),
        migrations.CreateModel(
            name='QuestIssueReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('reporter_name', models.CharField(blank=True, max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(
                    choices=[('open', 'Open'), ('resolved', 'Resolved')],
                    db_index=True,
                    default='open',
                    max_length=10,
                )),
                ('quest', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='issue_reports',
                    to='quests.quests',
                )),
            ],
            options={
                'verbose_name': 'Quest Issue Report',
                'verbose_name_plural': 'Quest Issue Reports',
                'ordering': ['-created_at'],
            },
        ),
    ]
