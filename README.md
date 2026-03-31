# EQMacEmu Players Website

A self-contained Django web application for [EverQuest Emulator](https://www.eqemulator.org/) servers. A live instance runs at [www.eqarchives.com](https://www.eqarchives.com).

## Features

- **Account management** — Login Server account registration, password reset, and self-service character transfers between accounts you own
- **Inventory search** — Account-wide search across all characters' banks and inventories
- **Magelo-style character profiles**
- **Alla-clone database browser:**
  - Items, Discovered Items, and Best-in-Slot lists
  - NPCs, Factions, Pets
  - Spells (search + per-class listings)
  - Tradeskill recipes
  - Zone pages (items, NPCs, foraged items, ground spawns, lore)
  - Patch messages
- **Quest pages** linking to/from Items, NPCs, and Zones *(in progress)*

## Requirements

- Python 3.11+
- MySQL (three databases — see [Configuration](#configuration))
- Redis (for caching)
- An EverQuest Emulator server with its Login Server and game databases accessible

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-org/EQMacEmu_Players.git
cd EQMacEmu_Players
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy the template and fill in your values:

```bash
cp .env.template .env
```

Edit `.env` — see [Configuration](#configuration) below for a description of each variable.

### 3. Set up the database

```bash
python manage.py migrate
```

### 4. Populate app data

After migrating, run the bootstrap script to generate spell data, import Best-in-Slot entries, and build the item expansion table:

```bash
bash scripts/bootstrap.sh
```

This runs the following commands in order — you can also run them individually if you need to refresh a specific dataset:

| Command | What it does |
|---|---|
| `generate_spell_data` | Builds per-class spell JSON files used by character spell tabs |
| `import_bis_from_markdown` | Seeds the Best-in-Slot table from `items/templates/items/best_in_slot/` |
| `resolve_bis_item_ids` | Matches BIS entry names to item IDs in the game database |
| `compute_item_expansions --seed-ranges` | Populates the item ID → expansion range table with defaults |
| `compute_item_expansions` | Infers each item's expansion from zone provenance and ID ranges |

**Re-running after game DB updates:** `generate_spell_data` and `compute_item_expansions --force` should be re-run whenever the game database receives a significant content update.

**Adjusting item expansion ranges:** Edit the ranges via the Django admin (*Item Expansion ID Ranges*), then run `python manage.py compute_item_expansions --force` to recompute. Individual item exceptions can be pinned by setting `is_override=True` on the item's *Item Expansion* admin entry.

### 5. Collect static files

```bash
python manage.py collectstatic
```

This assembles all static assets (including Django admin and third-party app assets) into `staticfiles/`. Your web server should be pointed at that directory.

### 6. Run (development)

```bash
python manage.py runserver
```

For production, use Gunicorn or uWSGI behind Nginx or Apache. Configure your web server to serve the `staticfiles/` directory at `/static/`.

## Configuration

All configuration is done via environment variables. Copy `.env.template` to `.env` and set the following:

### Databases

This app connects to three MySQL databases:

| Variable | Description |
|---|---|
| `DJANGO_APP_DB_NAME` | Django app database name |
| `DJANGO_APP_DB_USER` | Django app database user |
| `DJANGO_APP_DB_PASSWORD` | Django app database password |
| `DJANGO_APP_DB_HOST` | Django app database host (default: `127.0.0.1`) |
| `DJANGO_APP_DB_PORT` | Django app database port (default: `3306`) |
| `GAME_DB_NAME` | EverQuest game database name |
| `GAME_DB_USER` | Game database user |
| `GAME_DB_PASSWORD` | Game database password |
| `GAME_DB_HOST` | Game database host (default: `127.0.0.1`) |
| `GAME_DB_PORT` | Game database port (default: `3306`) |
| `LS_DB_NAME` | Login Server database name |
| `LS_DB_USER` | Login Server database user |
| `LS_DB_PASSWORD` | Login Server database password |
| `LS_DB_HOST` | Login Server database host (default: `127.0.0.1`) |
| `LS_DB_PORT` | Login Server database port (default: `3306`) |

### Application

| Variable | Description |
|---|---|
| `DJANGO_APP_SECRET_KEY` | Django secret key — generate a unique value for production |
| `DEBUG` | Set to `TRUE` for development, `FALSE` for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames (e.g. `myserver.com,www.myserver.com`) |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated list of trusted origins (e.g. `https://myserver.com`) |
| `ADMIN_URL` | URL path for the Django admin (default: `admin/`) — change this in production |

### Email

| Variable | Description |
|---|---|
| `DJANGO_EMAIL_BACKEND` | Django email backend class |
| `DJANGO_EMAIL_HOST` | SMTP host |
| `DJANGO_EMAIL_PORT` | SMTP port |
| `DJANGO_EMAIL_USE_TLS` | `True` or `False` |
| `DJANGO_EMAIL_HOST_USER` | SMTP username |
| `DJANGO_EMAIL_HOST_PASSWORD` | SMTP password |
| `DJANGO_DEFAULT_FROM_EMAIL` | From address for outgoing mail |

## Static Files

Source assets live in `static/` and are tracked in git — no extra download needed. The `staticfiles/` directory is generated by `collectstatic` and is intentionally excluded from version control.

## Contributing

Pull requests are welcome. Please open an issue first to discuss significant changes.
