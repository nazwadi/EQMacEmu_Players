"""
Management command to clean wikitext remnants from quest descriptions.

Fixes:
  - '''bold'''  →  **bold**
  - ''italic''  →  *italic*
  - Category:Foo lines  →  removed
  - Trailing whitespace / blank lines at start/end

Usage:
  python manage.py clean_quest_descriptions          # dry run (default)
  python manage.py clean_quest_descriptions --apply  # write changes to DB
"""
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from quests.models import Quests

_WIKITEXT_BOLD = re.compile(r"'''(.+?)'''", re.DOTALL)
_WIKITEXT_ITALIC = re.compile(r"''(.+?)''", re.DOTALL)
_CATEGORY_TAG = re.compile(r'\n?Category:[^\n]+', re.MULTILINE)
_TRAILING_BLANK = re.compile(r'\n{3,}')


def _clean(text: str) -> str:
    text = _WIKITEXT_BOLD.sub(r'**\1**', text)
    text = _WIKITEXT_ITALIC.sub(r'*\1*', text)
    text = _CATEGORY_TAG.sub('', text)
    text = _TRAILING_BLANK.sub('\n\n', text)
    return text.strip()


class Command(BaseCommand):
    help = "Clean wikitext remnants (bold/italic/Category tags) from quest descriptions."

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            default=False,
            help='Write changes to the database. Without this flag the command is a dry run.',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        dry_run = not apply

        if dry_run:
            self.stdout.write(self.style.WARNING(
                'DRY RUN — no changes will be written. Pass --apply to save.\n'
            ))

        quests = Quests.objects.exclude(description='').only('id', 'name', 'description')
        changed = []
        unchanged = 0

        for quest in quests.iterator():
            cleaned = _clean(quest.description)
            if cleaned == (quest.description or '').strip():
                unchanged += 1
                continue

            changed.append((quest, cleaned))

            if options['verbosity'] >= 2:
                self.stdout.write(f'\n--- {quest.name} (id={quest.id}) ---')
                # Show a diff-style summary: lines removed/changed
                old_lines = set(quest.description.splitlines())
                new_lines = set(cleaned.splitlines())
                for line in sorted(old_lines - new_lines):
                    if line.strip():
                        self.stdout.write(self.style.ERROR(f'  - {line[:120]}'))
                for line in sorted(new_lines - old_lines):
                    if line.strip():
                        self.stdout.write(self.style.SUCCESS(f'  + {line[:120]}'))

        self.stdout.write(
            f'\nFound {len(changed)} quest(s) needing cleanup, {unchanged} already clean.'
        )

        if not changed:
            self.stdout.write(self.style.SUCCESS('Nothing to do.'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nRun with --apply to write these {len(changed)} changes.'
            ))
            return

        with transaction.atomic():
            for quest, cleaned in changed:
                quest.description = cleaned
                quest.save(update_fields=['description'])

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully cleaned {len(changed)} quest description(s).'
        ))
