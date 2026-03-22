"""
Management command: import_bis_from_markdown

Seeds the BISEntry table from the static markdown files under
items/templates/items/best_in_slot/<class>/<expansion>.md

Run once after the initial migration:
    python manage.py import_bis_from_markdown

Use --dry-run to preview without writing to the database.
Use --clear to delete all existing BISEntry rows before importing.
"""
import re
from pathlib import Path

from django.core.management.base import BaseCommand

from items.models import BISEntry
from common.constants import PLAYER_CLASSES

EXPANSION_SLUGS = [
    'vanilla-pre-planar',
    'vanilla-planar',
    'kunark',
    'velious-group',
    'velious-raid',
    'luclin-group',
    'luclin-raid',
    'pop-group',
    'pop-raid',
]

_BULLET_RE = re.compile(r'^\*\s+(.+?)\s+-\s+(.+)$')


def parse_markdown(text, class_id, expansion):
    """Return a list of unsaved BISEntry objects parsed from markdown text."""
    entries = []
    for line in text.splitlines():
        m = _BULLET_RE.match(line.strip())
        if not m:
            continue
        slot = m.group(1).strip()
        items_raw = m.group(2).strip()
        items = [i.strip() for i in items_raw.split(',') if i.strip()]
        for rank, item_name in enumerate(items):
            entries.append(BISEntry(
                class_id=class_id,
                expansion=expansion,
                slot=slot,
                item_name=item_name,
                rank=rank,
            ))
    return entries


class Command(BaseCommand):
    help = 'Import BIS data from markdown files into the BISEntry database table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be imported without writing to the database',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing BISEntry rows before importing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clear = options['clear']

        base_dir = Path(__file__).resolve().parents[3] / 'items' / 'templates' / 'items' / 'best_in_slot'

        if clear and not dry_run:
            deleted, _ = BISEntry.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing BISEntry rows.'))

        total_created = 0
        total_skipped = 0

        for class_id, class_name in PLAYER_CLASSES.items():
            if class_id == 0:
                continue
            class_dir = base_dir / class_name.lower()
            if not class_dir.exists():
                self.stdout.write(self.style.WARNING(f'  No directory for {class_name}, skipping.'))
                continue

            for slug in EXPANSION_SLUGS:
                md_path = class_dir / f'{slug}.md'
                if not md_path.exists():
                    continue

                text = md_path.read_text(encoding='utf-8')
                entries = parse_markdown(text, class_id, slug)

                if not entries:
                    self.stdout.write(f'  {class_name} / {slug}: no items parsed')
                    continue

                if dry_run:
                    self.stdout.write(f'  [dry-run] {class_name} / {slug}: {len(entries)} entries')
                    for e in entries:
                        self.stdout.write(f'    rank={e.rank} slot={e.slot!r} item={e.item_name!r}')
                    continue

                created = 0
                skipped = 0
                for entry in entries:
                    _, was_created = BISEntry.objects.get_or_create(
                        class_id=entry.class_id,
                        expansion=entry.expansion,
                        slot=entry.slot,
                        item_name=entry.item_name,
                        defaults={'rank': entry.rank},
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1

                total_created += created
                total_skipped += skipped
                self.stdout.write(
                    f'  {class_name} / {slug}: {created} created, {skipped} already existed'
                )

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'Done. Total: {total_created} created, {total_skipped} skipped.'
            ))
