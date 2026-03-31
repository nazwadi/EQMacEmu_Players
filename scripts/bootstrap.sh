#!/usr/bin/env bash
# bootstrap.sh — run once after a fresh install to populate required app data.
# Must be run from the project root with the virtualenv active.
#
# Usage:
#   source .venv/bin/activate
#   bash scripts/bootstrap.sh

set -e

echo "==> Generating per-class spell data..."
python manage.py generate_spell_data

echo "==> Importing Best-in-Slot data from markdown..."
python manage.py import_bis_from_markdown

echo "==> Resolving item IDs on BIS entries..."
python manage.py resolve_bis_item_ids

echo "==> Seeding item expansion ID ranges..."
python manage.py compute_item_expansions --seed-ranges

echo "==> Computing item expansions..."
python manage.py compute_item_expansions

echo ""
echo "Bootstrap complete."
