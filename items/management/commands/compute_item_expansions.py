"""
Management command: compute_item_expansions

Populates the items_itemexpansion table by inferring which expansion each item
was first introduced in, using two strategies in priority order:

  1. Zone provenance — traverse the loot chain (item → loot drop → loot table →
     NPC → spawn → zone) and take the minimum zone.expansion value.

  2. Item ID range fallback — for items with no zone loot data (crafted items,
     quest rewards, vendor-only items, etc.) the item ID is matched against the
     ranges stored in items_itemexpansionidrange, which are editable via the
     Django admin.  One-off exceptions (a later item that happens to occupy an
     earlier ID, etc.) should be corrected by setting is_override=True on the
     specific ItemExpansion row rather than by adjusting the ranges.

Entries with is_override=True are never touched.

Usage:
    # Normal run — skips entries that already exist:
    python manage.py compute_item_expansions

    # Re-evaluate every non-override entry (use after adjusting ID ranges):
    python manage.py compute_item_expansions --force

    # Populate the ID ranges table with built-in defaults (safe to re-run):
    python manage.py compute_item_expansions --seed-ranges

    # Preview without writing:
    python manage.py compute_item_expansions --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import connections, connection

# ---------------------------------------------------------------------------
# Default ID range boundaries — loaded into ItemExpansionIdRange on first run
# (or when --seed-ranges is passed).  Edit the DB table via the Django admin
# and re-run with --force to apply changes.
# Each tuple: (min_item_id_inclusive, max_item_id_exclusive_or_None, expansion)
# ---------------------------------------------------------------------------
DEFAULT_ID_RANGES = [
    (0,      1000,  0),   # Original EverQuest
    (1000,   5000,  1),   # Ruins of Kunark
    (5000,   10000, 2),   # Scars of Velious
    (10000,  15000, 3),   # Shadows of Luclin
    (15000,  22000, 4),   # Planes of Power
    (22000,  25000, 5),   # Legacy of Ykesha
    (25000,  30000, 6),   # Lost Dungeons of Norrath
    (30000,  38000, 7),   # Gates of Discord
    (38000,  46000, 8),   # Omens of War
    (46000,  54000, 9),   # Dragons of Norrath
    (54000,  62000, 10),  # Depths of Darkhollow
    (62000,  70000, 11),  # Prophecy of Ro
    (70000,  None,  12),  # The Serpent's Spine and beyond
]

CREATE_RANGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS items_itemexpansionidrange (
    id          BIGINT  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    expansion   INT     NOT NULL,
    min_item_id INT     NOT NULL,
    max_item_id INT     NULL
)
"""

CREATE_EXPANSION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS items_itemexpansion (
    id          BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    item_id     INT          NOT NULL UNIQUE,
    expansion   INT          NOT NULL,
    source      VARCHAR(16)  NOT NULL DEFAULT 'zone',
    is_override TINYINT(1)   NOT NULL DEFAULT 0,
    INDEX idx_expansion (expansion)
)
"""

# Safe on MySQL 5.7+ and MariaDB: silently fails if the index already exists.
ADD_EXPANSION_INDEX_SQL = """
    ALTER TABLE items_itemexpansion ADD INDEX idx_expansion (expansion)
"""

# NPC IDs encode the zone: zone_id_number = FLOOR(npc_id / 1000).
# This lets us skip the spawnentry/spawn2 chain entirely, which is both faster
# and more reliable — it picks up NPCs that are scripted rather than spawned
# via traditional spawn tables (e.g. raid bosses in Vex Thal, Plane of Time).
ZONE_PROVENANCE_SQL = """
    SELECT lde.item_id, MIN(z.expansion) AS expansion
    FROM lootdrop_entries lde
    INNER JOIN lootdrop ld           ON ld.id            = lde.lootdrop_id
    INNER JOIN loottable_entries lte ON lte.lootdrop_id  = ld.id
    INNER JOIN loottable lt          ON lt.id            = lte.loottable_id
    INNER JOIN npc_types npc         ON npc.loottable_id = lt.id
    INNER JOIN zone z                ON z.zoneidnumber = FLOOR(npc.id / 1000)
    WHERE z.expansion >= 0
    GROUP BY lde.item_id
"""


def _load_ranges_from_db():
    """Return sorted list of (min_id, max_id_or_None, expansion) from the DB."""
    from items.models import ItemExpansionIdRange
    return [
        (r.min_item_id, r.max_item_id, r.expansion)
        for r in ItemExpansionIdRange.objects.all()  # ordered by min_item_id
    ]


def _expansion_from_id(item_id, ranges):
    for min_id, max_id, expansion in ranges:
        if max_id is None or item_id < max_id:
            return expansion
    return 0


class Command(BaseCommand):
    help = 'Populate items_itemexpansion from zone provenance and item ID range fallback'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be written without touching the database',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-evaluate and overwrite existing non-override entries. '
                 'Use this after editing ID ranges in the admin.',
        )
        parser.add_argument(
            '--seed-ranges',
            action='store_true',
            help='Populate items_itemexpansionidrange with built-in defaults. '
                 'Clears existing ranges first. Has no effect on ItemExpansion rows.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        seed_ranges = options['seed_ranges']

        # Ensure both tables exist.
        if not dry_run:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_RANGES_TABLE_SQL)
                cursor.execute(CREATE_EXPANSION_TABLE_SQL)
                # Add expansion index to existing tables that predate this change.
                try:
                    cursor.execute(ADD_EXPANSION_INDEX_SQL)
                    self.stdout.write('Added expansion index.')
                except Exception:
                    pass  # index already exists
            self.stdout.write('Tables ensured.')

        # Seed ID ranges from defaults if requested or if the table is empty.
        from items.models import ItemExpansion, ItemExpansionIdRange

        if seed_ranges:
            if not dry_run:
                ItemExpansionIdRange.objects.all().delete()
                ItemExpansionIdRange.objects.bulk_create([
                    ItemExpansionIdRange(min_item_id=mn, max_item_id=mx, expansion=exp)
                    for mn, mx, exp in DEFAULT_ID_RANGES
                ])
                self.stdout.write(f'Seeded {len(DEFAULT_ID_RANGES)} ID range entries.')
            else:
                self.stdout.write(self.style.WARNING(
                    f'[dry-run] Would seed {len(DEFAULT_ID_RANGES)} ID range entries.'
                ))

        ranges = _load_ranges_from_db()
        if not ranges:
            self.stdout.write(self.style.WARNING(
                'No ID ranges found in DB — run with --seed-ranges to populate defaults. '
                'ID range fallback will assign expansion 0 to all unmatched items.'
            ))

        # Load existing state.
        existing_map = {
            obj.item_id: obj
            for obj in ItemExpansion.objects.all()
        }
        override_ids = {item_id for item_id, obj in existing_map.items() if obj.is_override}
        existing_ids = set(existing_map.keys())
        self.stdout.write(
            f'Existing entries: {len(existing_ids)}  |  Protected overrides: {len(override_ids)}'
        )

        # Zone provenance query.
        self.stdout.write('Running zone provenance query…')
        with connections['game_database'].cursor() as cursor:
            cursor.execute(ZONE_PROVENANCE_SQL)
            zone_map = {row[0]: row[1] for row in cursor.fetchall()}
        self.stdout.write(f'Zone provenance: {len(zone_map)} items mapped.')

        # All item IDs from game DB.
        self.stdout.write('Fetching all item IDs…')
        with connections['game_database'].cursor() as cursor:
            cursor.execute("SELECT id FROM items")
            all_item_ids = [row[0] for row in cursor.fetchall()]
        self.stdout.write(f'Total items in game DB: {len(all_item_ids)}')

        # Build entries.
        to_create = []
        to_update = []
        skipped_override = 0
        skipped_existing = 0

        for item_id in all_item_ids:
            if item_id in override_ids:
                skipped_override += 1
                continue
            if item_id in existing_ids and not force:
                skipped_existing += 1
                continue

            if item_id in zone_map:
                expansion = zone_map[item_id]
                source = ItemExpansion.SOURCE_ZONE
            else:
                expansion = _expansion_from_id(item_id, ranges)
                source = ItemExpansion.SOURCE_ID_RANGE

            if item_id in existing_ids:
                obj = existing_map[item_id]
                obj.expansion = expansion
                obj.source = source
                to_update.append(obj)
            else:
                to_create.append(ItemExpansion(
                    item_id=item_id, expansion=expansion, source=source, is_override=False
                ))

        self.stdout.write(
            f'To create: {len(to_create)}  |  To update: {len(to_update)}  |  '
            f'Skipped (override): {skipped_override}  |  Skipped (exists): {skipped_existing}'
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run — no changes written.'))
            return

        if to_create:
            ItemExpansion.objects.bulk_create(to_create, batch_size=1000)
            self.stdout.write(f'Created {len(to_create)} entries.')

        if to_update:
            ItemExpansion.objects.bulk_update(
                to_update, ['expansion', 'source'], batch_size=1000
            )
            self.stdout.write(f'Updated {len(to_update)} entries.')

        # Invalidate cached expansion ID sets so the next search re-reads fresh data.
        from django.core.cache import cache
        cleared = 0
        for exp in range(32):
            if cache.delete(f'item_search:expansion_ids:{exp}'):
                cleared += 1
        if cleared:
            self.stdout.write(f'Cleared {cleared} expansion ID cache entries.')

        self.stdout.write(self.style.SUCCESS('Done.'))
