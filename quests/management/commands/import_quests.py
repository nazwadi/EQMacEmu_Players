"""
Management command to import quests from a dumpdata JSON export using natural keys,
avoiding PK conflicts when transferring between environments.

Usage:
    python manage.py import_quests quests_export.json
    python manage.py import_quests quests_export.json --update   # overwrite existing quests
"""

import json

from django.core.management.base import BaseCommand, CommandError

from quests.models import QuestFaction, QuestItem, Quests


class Command(BaseCommand):
    help = "Import quests from a dumpdata JSON file using natural keys (safe for cross-environment transfer)"

    def add_arguments(self, parser):
        parser.add_argument("fixture", help="Path to the JSON fixture file")
        parser.add_argument(
            "--update",
            action="store_true",
            help="Overwrite existing quests that match by name (default: skip existing)",
        )

    def handle(self, *args, **options):
        fixture_path = options["fixture"]
        do_update = options["update"]

        try:
            with open(fixture_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"File not found: {fixture_path}")
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON: {e}")

        records_by_model = {}
        for record in data:
            records_by_model.setdefault(record["model"], []).append(record)

        # Step 1: resolve QuestItems by natural key (item_id + name), build PK map
        self.stdout.write("Resolving quest items...")
        item_pk_map = {}  # export PK -> local QuestItem instance
        for record in records_by_model.get("quests.questitem", []):
            export_pk = record["pk"]
            item_id = record["fields"]["item_id"]
            name = record["fields"]["name"]
            obj, created = QuestItem.objects.get_or_create(item_id=item_id, name=name)
            item_pk_map[export_pk] = obj
            if created:
                self.stdout.write(f"  Created QuestItem: {name} ({item_id})")

        # Step 2: import Quests by natural key (name), build PK map
        self.stdout.write("Importing quests...")
        quest_pk_map = {}  # export PK -> local Quests instance
        quest_records = records_by_model.get("quests.quests", [])
        created_count = updated_count = skipped_count = 0

        for record in quest_records:
            export_pk = record["pk"]
            fields = record["fields"]
            name = fields["name"]

            quest_fields = {
                k: fields[k]
                for k in (
                    "description",
                    "starting_npc_id",
                    "starting_zone",
                    "expansion_introduced",
                    "minimum_level",
                    "maximum_level",
                    "class_restrictions",
                    "race_restrictions",
                    "deity_restrictions",
                    "is_repeatable",
                    "monster_mission",
                    "difficulty_rating",
                    "estimated_time",
                    "status",
                )
                if k in fields
            }

            existing = Quests.objects.filter(name=name).first()

            if existing and not do_update:
                self.stdout.write(f"  Skipping existing quest: {name}")
                quest_pk_map[export_pk] = existing
                skipped_count += 1
                continue

            if existing and do_update:
                for attr, value in quest_fields.items():
                    setattr(existing, attr, value)
                existing.save()
                quest = existing
                updated_count += 1
                self.stdout.write(f"  Updated quest: {name}")
            else:
                quest = Quests.objects.create(name=name, **quest_fields)
                created_count += 1
                self.stdout.write(f"  Created quest: {name}")

            quest_pk_map[export_pk] = quest

            # Set quest_items M2M using the resolved local instances
            export_item_pks = fields.get("quest_items", [])
            local_items = [
                item_pk_map[pk] for pk in export_item_pks if pk in item_pk_map
            ]
            missing = [pk for pk in export_item_pks if pk not in item_pk_map]
            if missing:
                self.stderr.write(
                    f"  WARNING: quest '{name}' references unknown QuestItem PKs: {missing}"
                )
            quest.quest_items.set(local_items)

        # Step 3: import QuestFactions by natural key (quest + faction_id + role)
        self.stdout.write("Importing quest factions...")
        faction_created = faction_skipped = 0
        for record in records_by_model.get("quests.questfaction", []):
            fields = record["fields"]
            export_quest_pk = fields["quest"]
            quest = quest_pk_map.get(export_quest_pk)
            if quest is None:
                self.stderr.write(
                    f"  WARNING: QuestFaction references unknown quest PK {export_quest_pk}, skipping"
                )
                continue
            _, created = QuestFaction.objects.get_or_create(
                quest=quest,
                faction_id=fields["faction_id"],
                role=fields["role"],
                defaults={"name": fields["name"]},
            )
            if created:
                faction_created += 1
            else:
                faction_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Quests: {created_count} created, {updated_count} updated, {skipped_count} skipped. "
                f"Factions: {faction_created} created, {faction_skipped} already existed."
            )
        )
