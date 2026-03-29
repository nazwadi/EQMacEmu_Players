"""
Management command to verify that Django model fields are in sync with the
actual database schema.

Particularly important for managed=False models (game_database, login_server)
where Django does not own the schema and drift can happen silently.

Usage:
    python manage.py check_db_schema
    python manage.py check_db_schema --database game_database
    python manage.py check_db_schema --app characters
"""

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connections, router


def get_db_columns(connection, table_name):
    """Return a set of lowercase column names for a table, or None if the table doesn't exist."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
            [table_name]
        )
        rows = cursor.fetchall()
    if not rows:
        return None
    # Lowercase for case-insensitive comparison (MySQL names are case-insensitive)
    return {row[0].lower() for row in rows}


def get_model_columns(model):
    """Return a dict of {lowercase_column_name: field_name} for all concrete fields.

    Excludes ManyToMany (live in junction tables) and reverse relations (no column).
    """
    columns = {}
    for field in model._meta.get_fields():
        if field.is_relation and not field.concrete:
            continue
        if field.many_to_many:
            continue
        if not hasattr(field, 'column') or field.column is None:
            continue
        # Strip backtick quoting used for reserved words (e.g. `class`, `int`)
        col = field.column.strip('`').lower()
        columns[col] = field.name
    return columns


class Command(BaseCommand):
    help = 'Check that Django model fields are in sync with the actual database schema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            default=None,
            help='Only check models on this database alias (e.g. game_database)',
        )
        parser.add_argument(
            '--app',
            default=None,
            help='Only check models in this app (e.g. characters, magelo)',
        )

    def handle(self, *args, **options):
        target_db = options['database']
        target_app = options['app']

        errors = []
        warnings = []
        checked = 0

        for model in apps.get_models():
            app_label = model._meta.app_label
            if target_app and app_label != target_app:
                continue

            db_alias = router.db_for_read(model) or 'default'
            if target_db and db_alias != target_db:
                continue

            table = model._meta.db_table.strip('`')
            connection = connections[db_alias]
            model_columns = get_model_columns(model)
            db_columns = get_db_columns(connection, table)

            if db_columns is None:
                if model._meta.managed:
                    warnings.append(
                        f"[{app_label}] {model.__name__}: "
                        f"table '{table}' not found on '{db_alias}' — unapplied migration?"
                    )
                else:
                    errors.append(
                        f"[{app_label}] {model.__name__}: "
                        f"table '{table}' not found on '{db_alias}'"
                    )
                continue

            checked += 1

            # Fields in model but missing from DB — these will cause runtime errors
            for col, field_name in model_columns.items():
                if col not in db_columns:
                    errors.append(
                        f"[{app_label}] {model.__name__}.{field_name}: "
                        f"column '{col}' missing from '{table}' on '{db_alias}'"
                    )

            # Columns in DB not in model — informational only, won't cause errors
            for col in db_columns:
                if col not in model_columns:
                    warnings.append(
                        f"[{app_label}] {model.__name__}: "
                        f"DB column '{col}' in '{table}' has no model field"
                    )

        self.stdout.write(f"\nChecked {checked} table(s).\n")

        if warnings:
            self.stdout.write(self.style.WARNING(f"Warnings ({len(warnings)}):"))
            for w in warnings:
                self.stdout.write(self.style.WARNING(f"  ! {w}"))

        if errors:
            self.stdout.write(self.style.ERROR(f"\nErrors ({len(errors)}):"))
            for e in errors:
                self.stdout.write(self.style.ERROR(f"  x {e}"))
            raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS(
                "\nNo errors found. Models are in sync with the database."
            ))
