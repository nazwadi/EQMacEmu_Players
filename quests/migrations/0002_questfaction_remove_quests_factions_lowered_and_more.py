# Manually written migration - idempotent for partially-applied state
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def apply_db_changes(apps, schema_editor):
    """
    Apply all DB-level changes idempotently.
    Some of these may have already been applied by previous partial runs.
    """
    cursor = schema_editor.connection.cursor()

    def table_exists(name):
        cursor.execute(f"SHOW TABLES LIKE '{name}'")
        return cursor.fetchone() is not None

    def column_exists(table, column):
        cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{column}'")
        return cursor.fetchone() is not None

    def index_exists(table, index_name):
        cursor.execute(f"SHOW INDEX FROM `{table}` WHERE Key_name = '{index_name}'")
        return cursor.fetchone() is not None

    # -- QuestItem: add unique_together if missing --
    if not index_exists('quests_questitem', 'quests_questitem_item_id_Name_dc2ae6cf_uniq'):
        # Check if any unique constraint on (item_id, Name) exists
        cursor.execute(
            "SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'quests_questitem' AND CONSTRAINT_TYPE = 'UNIQUE'"
        )
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE `quests_questitem` ADD UNIQUE `quests_questitem_item_id_Name_dc2ae6cf_uniq` (`item_id`, `Name`)")

    # -- QuestItem: add item_name_idx if missing --
    if not index_exists('quests_questitem', 'item_name_idx'):
        cursor.execute("CREATE INDEX `item_name_idx` ON `quests_questitem` (`Name`)")

    # -- QuestFaction: create table if not exists --
    if not table_exists('quests_questfaction'):
        cursor.execute("""
            CREATE TABLE `quests_questfaction` (
                `id` bigint AUTO_INCREMENT PRIMARY KEY,
                `faction_id` int NOT NULL,
                `name` varchar(50) NOT NULL,
                `role` varchar(10) NOT NULL,
                `quest_id` int NOT NULL,
                UNIQUE KEY `quests_questfaction_quest_id_faction_id_role_ee3d4d7f_uniq` (`quest_id`, `faction_id`, `role`),
                KEY `quest_faction_id_idx` (`faction_id`),
                KEY `quest_faction_role_idx` (`role`),
                CONSTRAINT `quests_questfaction_quest_id_fk` FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)

    # -- Drop faction M2M junction tables (may not exist) --
    for table in ['quests_factions_lowered', 'quests_factions_raised', 'quests_factions_required']:
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")

    # -- Drop old standalone faction tables --
    for table in ['quests_questfactionlowered', 'quests_questfactionraised', 'quests_questfactionrequired']:
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")

    # -- Remove quest_reward column if it still exists --
    if column_exists('quests', 'quest_reward'):
        cursor.execute("ALTER TABLE `quests` DROP COLUMN `quest_reward`")

    # -- Add created_at if missing --
    if not column_exists('quests', 'created_at'):
        cursor.execute("ALTER TABLE `quests` ADD COLUMN `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)")

    # -- Add updated_at if missing --
    if not column_exists('quests', 'updated_at'):
        cursor.execute("ALTER TABLE `quests` ADD COLUMN `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)")

    # -- Add prerequisite_id if missing --
    if not column_exists('quests', 'prerequisite_id'):
        cursor.execute("ALTER TABLE `quests` ADD COLUMN `prerequisite_id` int DEFAULT NULL")
        cursor.execute("ALTER TABLE `quests` ADD CONSTRAINT `quests_prerequisite_id_fk` FOREIGN KEY (`prerequisite_id`) REFERENCES `quests` (`id`)")


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0001_initial'),
    ]

    operations = [
        # Single RunPython handles all DB changes idempotently
        migrations.RunPython(apply_db_changes, migrations.RunPython.noop),

        # SeparateDatabaseAndState for everything else — tells Django about
        # state changes without touching the DB (RunPython already did it)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Rename QuestItem.Name → name
                migrations.RenameField(model_name='questitem', old_name='Name', new_name='name'),
                migrations.AlterField(
                    model_name='questitem', name='name',
                    field=models.CharField(db_column='Name', default='', max_length=64),
                ),
                migrations.AlterModelOptions(
                    name='questitem',
                    options={'ordering': ['name'], 'verbose_name': 'Quest Item', 'verbose_name_plural': 'Quest Items'},
                ),
                migrations.AlterUniqueTogether(name='questitem', unique_together={('item_id', 'name')}),
                migrations.RemoveIndex(model_name='questitem', name='item_name_idx'),
                migrations.AddIndex(
                    model_name='questitem',
                    index=models.Index(fields=['name'], name='item_name_idx'),
                ),

                # Create QuestFaction
                migrations.CreateModel(
                    name='QuestFaction',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('faction_id', models.IntegerField()),
                        ('name', models.CharField(max_length=50)),
                        ('role', models.CharField(choices=[('required', 'Required'), ('raised', 'Raised'), ('lowered', 'Lowered')], max_length=10)),
                        ('quest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quest_factions', to='quests.quests')),
                    ],
                    options={
                        'verbose_name': 'Quest Faction',
                        'verbose_name_plural': 'Quest Factions',
                        'ordering': ['role', 'name'],
                        'unique_together': {('quest', 'faction_id', 'role')},
                    },
                ),
                migrations.AddIndex(
                    model_name='questfaction',
                    index=models.Index(fields=['faction_id'], name='quest_faction_id_idx'),
                ),
                migrations.AddIndex(
                    model_name='questfaction',
                    index=models.Index(fields=['role'], name='quest_faction_role_idx'),
                ),

                # Remove old faction M2M fields and models
                migrations.RemoveField(model_name='quests', name='factions_lowered'),
                migrations.RemoveField(model_name='quests', name='factions_raised'),
                migrations.RemoveField(model_name='quests', name='factions_required'),
                migrations.DeleteModel(name='QuestFactionLowered'),
                migrations.DeleteModel(name='QuestFactionRaised'),
                migrations.DeleteModel(name='QuestFactionRequired'),

                # Quest model changes
                migrations.RemoveField(model_name='quests', name='quest_reward'),
                migrations.AddField(
                    model_name='quests', name='created_at',
                    field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='quests', name='prerequisite',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sequels', to='quests.quests'),
                ),
                migrations.AddField(
                    model_name='quests', name='updated_at',
                    field=models.DateTimeField(auto_now=True),
                ),
            ],
            database_operations=[],
        ),
    ]
