# Manually written migration - idempotent for partially-applied state.
#
# 0001_initial was fake-applied against a pre-existing DB, so several tables
# and indexes were never actually created. This migration creates everything
# that is missing without touching anything that already exists.
from django.db import migrations


def create_missing_tables(apps, schema_editor):
    cursor = schema_editor.connection.cursor()

    def table_exists(name):
        cursor.execute(f"SHOW TABLES LIKE '{name}'")
        return cursor.fetchone() is not None

    def index_exists(table, index_name):
        cursor.execute(f"SHOW INDEX FROM `{table}` WHERE Key_name = '{index_name}'")
        return cursor.fetchone() is not None

    def constraint_exists(table, constraint_name):
        cursor.execute(
            "SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND CONSTRAINT_NAME = %s",
            [table, constraint_name]
        )
        return cursor.fetchone() is not None

    def column_exists(table, column):
        cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{column}'")
        return cursor.fetchone() is not None

    # -------------------------------------------------------------------------
    # QuestsRelatedNPC model table
    # -------------------------------------------------------------------------
    if not table_exists('quests_related_npc'):
        cursor.execute("""
            CREATE TABLE `quests_related_npc` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `npc_id` int NOT NULL UNIQUE,
                `name` varchar(64) NOT NULL DEFAULT ''
            )
        """)
    if table_exists('quests_related_npc') and not index_exists('quests_related_npc', 'npc_id_idx'):
        cursor.execute("CREATE INDEX `npc_id_idx` ON `quests_related_npc` (`npc_id`)")
    if table_exists('quests_related_npc') and not index_exists('quests_related_npc', 'npc_name_idx'):
        cursor.execute("CREATE INDEX `npc_name_idx` ON `quests_related_npc` (`name`)")

    # -------------------------------------------------------------------------
    # QuestsRelatedZone model table
    # -------------------------------------------------------------------------
    if not table_exists('quests_related_zone'):
        cursor.execute("""
            CREATE TABLE `quests_related_zone` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `zone_id` int NOT NULL DEFAULT 0,
                `long_name` longtext NOT NULL,
                `short_name` varchar(32) DEFAULT NULL UNIQUE
            )
        """)
    if table_exists('quests_related_zone') and not index_exists('quests_related_zone', 'short_name_idx'):
        cursor.execute("CREATE INDEX `short_name_idx` ON `quests_related_zone` (`short_name`)")
    if table_exists('quests_related_zone') and not index_exists('quests_related_zone', 'zone_id_idx'):
        cursor.execute("CREATE INDEX `zone_id_idx` ON `quests_related_zone` (`zone_id`)")

    # -------------------------------------------------------------------------
    # M2M junction: quests ↔ quests_related_npc  (Quests.related_npcs)
    # -------------------------------------------------------------------------
    if not table_exists('quests_related_npcs'):
        cursor.execute("""
            CREATE TABLE `quests_related_npcs` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `quests_id` int NOT NULL,
                `questsrelatednpc_id` bigint NOT NULL,
                UNIQUE KEY `quests_related_npcs_quests_id_questsrelatednpc_id_uniq`
                    (`quests_id`, `questsrelatednpc_id`),
                CONSTRAINT `quests_related_npcs_quests_id_fk`
                    FOREIGN KEY (`quests_id`) REFERENCES `quests` (`id`),
                CONSTRAINT `quests_related_npcs_questsrelatednpc_id_fk`
                    FOREIGN KEY (`questsrelatednpc_id`) REFERENCES `quests_related_npc` (`id`)
            )
        """)

    # -------------------------------------------------------------------------
    # M2M junction: quests ↔ quests_related_zone  (Quests.related_zones)
    # -------------------------------------------------------------------------
    if not table_exists('quests_related_zones'):
        cursor.execute("""
            CREATE TABLE `quests_related_zones` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `quests_id` int NOT NULL,
                `questsrelatedzone_id` bigint NOT NULL,
                UNIQUE KEY `quests_related_zones_quests_id_questsrelatedzone_id_uniq`
                    (`quests_id`, `questsrelatedzone_id`),
                CONSTRAINT `quests_related_zones_quests_id_fk`
                    FOREIGN KEY (`quests_id`) REFERENCES `quests` (`id`),
                CONSTRAINT `quests_related_zones_questsrelatedzone_id_fk`
                    FOREIGN KEY (`questsrelatedzone_id`) REFERENCES `quests_related_zone` (`id`)
            )
        """)

    # -------------------------------------------------------------------------
    # M2M junction: quests ↔ quests_questtag  (Quests.tags)
    # -------------------------------------------------------------------------
    if not table_exists('quests_tags'):
        cursor.execute("""
            CREATE TABLE `quests_tags` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `quests_id` int NOT NULL,
                `questtag_id` bigint NOT NULL,
                UNIQUE KEY `quests_tags_quests_id_questtag_id_uniq`
                    (`quests_id`, `questtag_id`),
                CONSTRAINT `quests_tags_quests_id_fk`
                    FOREIGN KEY (`quests_id`) REFERENCES `quests` (`id`),
                CONSTRAINT `quests_tags_questtag_id_fk`
                    FOREIGN KEY (`questtag_id`) REFERENCES `quests_questtag` (`id`)
            )
        """)

    # -------------------------------------------------------------------------
    # Reward tables (all share quest_id FK, is_optional, reward_group)
    # -------------------------------------------------------------------------

    if not table_exists('quests_itemreward'):
        cursor.execute("""
            CREATE TABLE `quests_itemreward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `item_id` int NOT NULL,
                `item_name` varchar(100) NOT NULL,
                `quantity` int unsigned NOT NULL DEFAULT 1,
                `charges` int unsigned DEFAULT NULL,
                `attuned` tinyint(1) NOT NULL DEFAULT 0,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_itemreward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)
    if table_exists('quests_itemreward') and not index_exists('quests_itemreward', 'reward_item_id_idx'):
        cursor.execute("CREATE INDEX `reward_item_id_idx` ON `quests_itemreward` (`item_id`)")
    if table_exists('quests_itemreward') and not index_exists('quests_itemreward', 'reward_item_name_idx'):
        cursor.execute("CREATE INDEX `reward_item_name_idx` ON `quests_itemreward` (`item_name`)")

    if not table_exists('quests_experiencereward'):
        cursor.execute("""
            CREATE TABLE `quests_experiencereward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `amount` int NOT NULL,
                `is_percentage` tinyint(1) NOT NULL DEFAULT 0,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_experiencereward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)

    if not table_exists('quests_currencyreward'):
        cursor.execute("""
            CREATE TABLE `quests_currencyreward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `platinum` int unsigned NOT NULL DEFAULT 0,
                `gold` int unsigned NOT NULL DEFAULT 0,
                `silver` int unsigned NOT NULL DEFAULT 0,
                `copper` int unsigned NOT NULL DEFAULT 0,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_currencyreward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)

    if not table_exists('quests_factionreward'):
        cursor.execute("""
            CREATE TABLE `quests_factionreward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `faction_id` int NOT NULL,
                `faction_name` varchar(100) NOT NULL,
                `amount` int NOT NULL,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_factionreward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)
    if table_exists('quests_factionreward') and not index_exists('quests_factionreward', 'reward_faction_id_idx'):
        cursor.execute("CREATE INDEX `reward_faction_id_idx` ON `quests_factionreward` (`faction_id`)")
    if table_exists('quests_factionreward') and not index_exists('quests_factionreward', 'reward_faction_name_idx'):
        cursor.execute("CREATE INDEX `reward_faction_name_idx` ON `quests_factionreward` (`faction_name`)")

    if not table_exists('quests_skillreward'):
        cursor.execute("""
            CREATE TABLE `quests_skillreward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `skill_id` int DEFAULT NULL,
                `skill_name` varchar(100) NOT NULL,
                `amount` int unsigned NOT NULL DEFAULT 1,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_skillreward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)

    if not table_exists('quests_spellreward'):
        cursor.execute("""
            CREATE TABLE `quests_spellreward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `spell_id` int NOT NULL,
                `spell_name` varchar(100) NOT NULL,
                `spell_level` smallint unsigned NOT NULL DEFAULT 1,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_spellreward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)
    if table_exists('quests_spellreward') and not index_exists('quests_spellreward', 'reward_spell_id_idx'):
        cursor.execute("CREATE INDEX `reward_spell_id_idx` ON `quests_spellreward` (`spell_id`)")

    if not table_exists('quests_titlereward'):
        cursor.execute("""
            CREATE TABLE `quests_titlereward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `title_text` varchar(200) NOT NULL,
                `is_prefix` tinyint(1) NOT NULL DEFAULT 1,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_titlereward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)

    if not table_exists('quests_aareward'):
        cursor.execute("""
            CREATE TABLE `quests_aareward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `aa_id` int DEFAULT NULL,
                `aa_name` varchar(100) NOT NULL,
                `aa_points` int unsigned NOT NULL DEFAULT 1,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_aareward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)

    if not table_exists('quests_accessreward'):
        cursor.execute("""
            CREATE TABLE `quests_accessreward` (
                `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `is_optional` tinyint(1) NOT NULL DEFAULT 0,
                `reward_group` smallint unsigned NOT NULL DEFAULT 0,
                `flag_name` varchar(100) NOT NULL,
                `flag_value` varchar(100) NOT NULL DEFAULT '',
                `description` longtext NOT NULL,
                `quest_id` int NOT NULL,
                CONSTRAINT `quests_accessreward_quest_id_fk`
                    FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
            )
        """)
    if table_exists('quests_accessreward') and not index_exists('quests_accessreward', 'reward_flag_name_idx'):
        cursor.execute("CREATE INDEX `reward_flag_name_idx` ON `quests_accessreward` (`flag_name`)")

    # -------------------------------------------------------------------------
    # Missing named indexes on quests table
    # -------------------------------------------------------------------------
    quests_named_indexes = [
        ('quest_name_idx', '`name`'),
        ('starting_zone_idx', '`starting_zone`'),
        ('starting_npc_idx', '`starting_npc_id`'),
        ('expansion_idx', '`expansion_introduced`'),
        ('level_range_idx', '`minimum_level`, `maximum_level`'),
        ('class_idx', '`class_restrictions`'),
        ('race_idx', '`race_restrictions`'),
    ]
    for idx_name, cols in quests_named_indexes:
        if not index_exists('quests', idx_name):
            cursor.execute(f"CREATE INDEX `{idx_name}` ON `quests` ({cols})")

    # -------------------------------------------------------------------------
    # Missing indexes on quests_questitem
    # -------------------------------------------------------------------------
    if not index_exists('quests_questitem', 'item_id_idx'):
        cursor.execute("CREATE INDEX `item_id_idx` ON `quests_questitem` (`item_id`)")
    # item_name_idx and unique constraint handled by 0002 already, but guard anyway
    if not index_exists('quests_questitem', 'item_name_idx'):
        cursor.execute("CREATE INDEX `item_name_idx` ON `quests_questitem` (`Name`)")


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0002_questfaction_remove_quests_factions_lowered_and_more'),
    ]

    operations = [
        migrations.RunPython(create_missing_tables, migrations.RunPython.noop),
    ]
