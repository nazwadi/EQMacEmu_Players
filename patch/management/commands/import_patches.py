"""
Management command: import_patches

Parses patches_1999-2010_combined.txt and loads patch messages into the
PatchMessage table.

Usage:
    python manage.py import_patches
    python manage.py import_patches --file /path/to/file.txt
    python manage.py import_patches --dry-run
    python manage.py import_patches --clear
"""
import re
from datetime import date, datetime, timezone
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from patch.models import PatchMessage

# ---------------------------------------------------------------------------
# Patch type classification
# ---------------------------------------------------------------------------

_HOTFIX_RE = re.compile(r'hot\s*fix', re.IGNORECASE)
_PRESS_RE = re.compile(r'press release', re.IGNORECASE)
_NEWS_RE = re.compile(r'news bit|terrorist attack|follow.up|news story', re.IGNORECASE)


def classify_patch_type(title: str) -> str:
    if _HOTFIX_RE.search(title):
        return 'hotfix'
    if _PRESS_RE.search(title):
        return 'press_release'
    if _NEWS_RE.search(title):
        return 'news'
    return 'patch'


# ---------------------------------------------------------------------------
# Expansion assignment
# ---------------------------------------------------------------------------

def get_expansion(patch_date: datetime | None) -> str | None:
    if not patch_date:
        return None
    d = patch_date.date()
    if d < date(2000, 4, 24):  return 'classic'
    if d < date(2000, 12, 5):  return 'kunark'
    if d < date(2001, 12, 4):  return 'velious'
    if d < date(2002, 10, 22): return 'luclin'
    if d < date(2003, 2, 10):  return 'pop'
    if d < date(2003, 9, 9):   return 'ykesha'
    if d < date(2004, 2, 10):  return 'ldon'
    if d < date(2004, 9, 14):  return 'gates'
    if d < date(2005, 2, 15):  return 'omens'
    if d < date(2005, 9, 13):  return 'dragons'
    if d < date(2006, 2, 21):  return 'dod'
    if d < date(2006, 9, 19):  return 'por'
    if d < date(2007, 2, 13):  return 'tss'
    if d < date(2007, 11, 13): return 'tbs'
    if d < date(2008, 10, 21): return 'sof'
    if d < date(2009, 12, 15): return 'sod'
    if d < date(2010, 10, 12): return 'underfoot'
    return 'hot'

# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'dcember': 12,  # typo present in source file
}

_MONTH_PAT = '|'.join(sorted(MONTH_MAP, key=len, reverse=True))
_DATE_RE = re.compile(
    rf'({_MONTH_PAT})'           # month name (case-insensitive)
    r'\s+(\d{1,2}),?\s+'         # day
    r'(\d{4})'                   # year
    r'(?:\s+(\d{1,2}):(\d{2})\s*(am|pm))?',  # optional time
    re.IGNORECASE,
)


def parse_date(header: str) -> datetime | None:
    """Return a UTC-aware datetime parsed from the patch header line, or None."""
    m = _DATE_RE.search(header)
    if not m:
        return None
    month_str = m.group(1).lower()
    day = int(m.group(2))
    year = int(m.group(3))
    month = MONTH_MAP.get(month_str)
    if month is None:
        return None

    hour, minute = 0, 0
    if m.group(4):
        hour = int(m.group(4))
        minute = int(m.group(5))
        ampm = m.group(6).lower()
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0

    try:
        return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------

_BLOCK_RE = re.compile(
    r'-{30}\n([^\n]+)\n-{30}\n(.*?)(?=\n\.+\n|\Z)',
    re.DOTALL,
)

DEFAULT_FILE = Path(__file__).resolve().parents[3] / 'patches_1999-2010_combined.txt'


def parse_file(path: Path) -> list[dict]:
    """Return a list of patch dicts parsed from the combined text file."""
    content = path.read_text(encoding='latin-1')
    blocks = _BLOCK_RE.findall(content)

    # Track per-date counts to populate patch_number_this_date
    date_counts: dict[str, int] = {}
    # Track slugs to make them unique
    slug_counts: dict[str, int] = {}
    # Track titles to make them unique
    title_counts: dict[str, int] = {}

    patches = []
    for header, body in blocks:
        header = header.strip()
        body = body.strip()

        patch_date = parse_date(header)
        if patch_date is None:
            # Can't parse a date — store with a sentinel date and note
            patch_year = 0
        else:
            patch_year = patch_date.year

        # Unique title: append (2), (3) … for duplicates
        title = header
        if title in title_counts:
            title_counts[title] += 1
            title = f'{header} ({title_counts[header]})'
        else:
            title_counts[title] = 1

        # patch_number_this_date: how many patches have we seen on this date?
        date_key = patch_date.date().isoformat() if patch_date else header
        date_counts[date_key] = date_counts.get(date_key, 0) + 1
        patch_number = date_counts[date_key]

        # Unique slug
        base_slug = slugify(title)[:240]
        if base_slug in slug_counts:
            slug_counts[base_slug] += 1
            slug = f'{base_slug}-{slug_counts[base_slug]}'
        else:
            slug_counts[base_slug] = 1
            slug = base_slug

        patches.append({
            'title': title,
            'body_markdown': body,
            'body_plaintext': body,
            'patch_date': patch_date,
            'patch_number_this_date': patch_number,
            'patch_year': patch_year,
            'patch_type': classify_patch_type(title),
            'expansion': get_expansion(patch_date),
            'source_notes': 'Combined EverQuest live server patch archive, 1999\u20132010',
            'slug': slug,
        })

    return patches


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = 'Import EverQuest patch messages from the combined text file into PatchMessage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=str(DEFAULT_FILE),
            help='Path to the combined patch text file (default: patches_1999-2010_combined.txt in project root)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be imported without writing to the database',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing PatchMessage rows before importing',
        )

    def handle(self, *args, **options):
        path = Path(options['file'])
        dry_run = options['dry_run']
        clear = options['clear']

        if not path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {path}'))
            return

        self.stdout.write(f'Parsing {path} …')
        patches = parse_file(path)
        self.stdout.write(f'Found {len(patches)} patch entries.')

        if clear and not dry_run:
            deleted, _ = PatchMessage.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing PatchMessage rows.'))

        created = skipped = unparsed = 0

        for p in patches:
            if p['patch_date'] is None:
                unparsed += 1
                self.stdout.write(self.style.WARNING(f'  Could not parse date from: {p["title"]!r}'))

            if dry_run:
                date_str = p['patch_date'].strftime('%Y-%m-%d %H:%M') if p['patch_date'] else 'UNKNOWN'
                self.stdout.write(
                    f'  [dry-run] {date_str} #{p["patch_number_this_date"]}  {p["title"]!r}  slug={p["slug"]!r}'
                )
                continue

            _, was_created = PatchMessage.objects.get_or_create(
                slug=p['slug'],
                defaults={
                    'title': p['title'],
                    'body_markdown': p['body_markdown'],
                    'body_plaintext': p['body_plaintext'],
                    'patch_date': p['patch_date'],
                    'patch_number_this_date': p['patch_number_this_date'],
                    'patch_year': p['patch_year'],
                    'patch_type': p['patch_type'],
                    'expansion': p['expansion'],
                    'source_notes': p['source_notes'],
                },
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'Done. {created} created, {skipped} already existed, {unparsed} with unparseable dates.'
            ))
