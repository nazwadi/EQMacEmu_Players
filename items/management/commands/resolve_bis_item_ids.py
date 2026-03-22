"""
Management command: resolve_bis_item_ids

Attempts to match BISEntry rows that have no item_id to Items in the game
database by exact name, with progressive fallbacks:

  1. Exact match on stored name
  2. Unescape backtick: remove backslash before `` ` ``, then convert
     possessive `` `s `` → ``'s`` — e.g. Sal\\`Varae`s → Sal`Varae's
     (also fixes stored item_name)
  3. All backticks → apostrophe fallback (also fixes stored item_name)
  4. Strip trailing asterisk                   (also fixes stored item_name)
  5. Strip inline parenthetical note, e.g. "Item (Chardok 2.0)"  (id only)
  6. Strip " // …" alternative notation        (id only)
  7. Strip "prefix: " prefix                   (id only)

Run after import_bis_from_markdown:
    python manage.py resolve_bis_item_ids

Use --dry-run to preview matches without writing.
"""
import re

from django.core.management.base import BaseCommand

from items.models import BISEntry
from common.models.items import Items


def _unescape_backtick(name):
    """
    Remove backslashes that precede backticks, then convert possessive `s → 's.
    e.g. Sal\\`Varae`s → Sal`Varae's
    """
    name = name.replace("\\`", "`")       # \` → ` (unescape)
    name = re.sub(r"`s\b", "'s", name)    # `s → 's (possessive only)
    return name


def _all_apostrophe(name):
    """Replace all remaining backticks with apostrophes."""
    return name.replace("\\`", "'").replace("`", "'")


def _lookup(name):
    """Return (item, count) for exact name match against Items table."""
    hits = Items.objects.filter(Name=name)
    count = hits.count()
    return (hits.first() if count == 1 else None), count


def _candidates(raw_name):
    """
    Yield (candidate_name, fix_stored_name) pairs from most to least specific.
    fix_stored_name=True means the stored item_name should also be updated.
    """
    # Step 2: unescape \` then apostrophize possessive `s
    unescaped = _unescape_backtick(raw_name)
    if unescaped != raw_name:
        yield unescaped, True

    # Step 3: all backticks → apostrophe
    full_apostrophe = _all_apostrophe(raw_name)
    if full_apostrophe not in (raw_name, unescaped):
        yield full_apostrophe, True

    # Work from the cleanest base we have
    base = unescaped if unescaped != raw_name else full_apostrophe

    # Step 4: strip trailing asterisk
    stripped = base.rstrip('*').strip()
    if stripped != base:
        yield stripped, True

    base = stripped

    # Step 5: strip inline parenthetical note  "Name (note…)"
    m = re.match(r'^(.+?)\s+\(', base)
    if m:
        yield m.group(1).strip(), False   # keep original display name

    # Step 6: strip " // …" alternative notation
    if '//' in base:
        yield base.split('//')[0].strip(), False

    # Step 7: strip "prefix: name" (e.g. "resists: Item Name")
    if ':' in base:
        yield base.split(':', 1)[1].strip(), False


class Command(BaseCommand):
    help = 'Resolve item_id on BISEntry rows by matching item names to the game Items table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print matches without updating the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        unresolved = BISEntry.objects.filter(item_id__isnull=True)
        total = unresolved.count()
        self.stdout.write(f'{total} BISEntry rows without item_id.')

        matched = 0
        ambiguous = 0
        not_found = 0

        for entry in unresolved:
            # Try exact match first
            item, count = _lookup(entry.item_name)
            if item:
                if not dry_run:
                    entry.item_id = item.id
                    entry.save(update_fields=['item_id'])
                else:
                    self.stdout.write(f'  [match] {entry.item_name!r} → id={item.id}')
                matched += 1
                continue
            if count > 1:
                ids = list(Items.objects.filter(Name=entry.item_name).values_list('id', flat=True)[:5])
                self.stdout.write(self.style.WARNING(
                    f'  [ambiguous] {entry.item_name!r} — {count} items: {ids}'
                ))
                ambiguous += 1
                continue

            # Try progressive fallbacks
            resolved = False
            for candidate, fix_name in _candidates(entry.item_name):
                item, count = _lookup(candidate)
                if item:
                    if dry_run:
                        tag = 'match+fix' if fix_name else 'match'
                        self.stdout.write(
                            f'  [{tag}] {entry.item_name!r} → {candidate!r} id={item.id}'
                        )
                    else:
                        entry.item_id = item.id
                        if fix_name:
                            entry.item_name = candidate
                            entry.save(update_fields=['item_id', 'item_name'])
                        else:
                            entry.save(update_fields=['item_id'])
                    matched += 1
                    resolved = True
                    break
                if count > 1:
                    ids = list(Items.objects.filter(Name=candidate).values_list('id', flat=True)[:5])
                    self.stdout.write(self.style.WARNING(
                        f'  [ambiguous via fallback] {candidate!r} — {count} items: {ids}'
                    ))
                    ambiguous += 1
                    resolved = True
                    break

            if not resolved:
                self.stdout.write(self.style.WARNING(f'  [no match] {entry.item_name!r}'))
                not_found += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Matched: {matched}, Ambiguous: {ambiguous}, Not found: {not_found}'
        ))
