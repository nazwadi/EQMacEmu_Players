# Quest Data Population Script - Problem Specification

## Goal

Build a Django management command (`python manage.py populate_quests`) that populates the quests database from external sources (Allakhazam and/or P99 Wiki). The command should be idempotent (safe to re-run) and support incremental updates.

---

## Target Schema

The script needs to populate these models (defined in `quests/models.py`):

### Primary: `Quests`
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100), unique | Quest name |
| `description` | MDTextField | Markdown-formatted walkthrough/description |
| `starting_npc_id` | IntegerField | NPC ID from the `npc_types` table in game_database |
| `starting_zone` | CharField(100) | Short name from `ZONE_SHORT_TO_LONG` in `common/constants.py` |
| `expansion_introduced` | SmallIntegerField | 0=Vanilla, 1=Kunark, 2=Velious, 3=Luclin, 4=PoP, 5=Ykesha, 6=LDoN, 7=GoD, 8=OoW, 9=DoN, 10=DoDH |
| `minimum_level` | SmallIntegerField | Default 1 |
| `maximum_level` | SmallIntegerField | -1 means server max (60) |
| `class_restrictions` | IntegerField | -1=None, 0=Unknown, 1=WAR..15=BST (see `PLAYER_CLASS_RESTRICTION_CHOICES`) |
| `race_restrictions` | IntegerField | -1=None, 0=Unknown, 1=HUM..14=VAH (see `PLAYER_RACE_RESTRICTION_CHOICES`) |
| `deity_restrictions` | IntegerField | -1=None, see `PLAYER_DEITY_RESTRICTIONS` dict for IDs |
| `is_repeatable` | BooleanField | Default True |
| `monster_mission` | BooleanField | Default False |
| `difficulty_rating` | SmallIntegerField | 1-5 (Very Easy to Very Hard) |
| `estimated_time` | CharField(50) | e.g. "30 minutes", "2 hours" |
| `prerequisite` | FK to self | For quest chains, set after all quests are created |
| `category` | FK to QuestCategory | Optional |
| `tags` | M2M to QuestTag | Optional |

### Related: `QuestFaction`
| Field | Type | Notes |
|-------|------|-------|
| `quest` | FK to Quests | |
| `faction_id` | IntegerField | Faction ID from the game database |
| `name` | CharField(50) | Faction name |
| `role` | CharField(10) | 'required', 'raised', or 'lowered' |

### Related: `QuestItem`
| Field | Type | Notes |
|-------|------|-------|
| `item_id` | IntegerField | Item ID from game database |
| `name` | CharField(64) | Item name (db_column='Name') |

### Related: `QuestsRelatedNPC`
| Field | Type | Notes |
|-------|------|-------|
| `npc_id` | IntegerField, unique | NPC ID from game database |
| `name` | CharField(64) | NPC name |

### Related: `QuestsRelatedZone`
| Field | Type | Notes |
|-------|------|-------|
| `zone_id` | IntegerField | Zone ID from game database |
| `long_name` | TextField | |
| `short_name` | CharField(32), unique | Zone short name |

### Reward Models (all FK to Quests):
- `ItemReward`: item_id, item_name, quantity, charges, attuned, is_optional, reward_group
- `ExperienceReward`: amount, is_percentage
- `CurrencyReward`: platinum, gold, silver, copper
- `FactionReward`: faction_id, faction_name, amount (positive=gain, negative=loss)
- `SpellReward`: spell_id, spell_name, spell_level
- `SkillReward`: skill_id, skill_name, amount
- `AccessReward`: flag_name, flag_value, description

---

## Data Sources

### Option A: Allakhazam (everquest.allakhazam.com)

**Pros**: Most comprehensive classic EQ quest database, structured data.
**Cons**: Must scrape HTML, may have rate limiting, data includes all expansions (need to filter).

**Key URLs**:
- Quest detail: `https://everquest.allakhazam.com/db/quest.html?quest={QUEST_ID}`
- Zone quest list: `https://everquest.allakhazam.com/db/qsearch.html?zone={ZONE_ID}`
- Zone index: `https://everquest.allakhazam.com/db/zone.html?mode=questsbycont`

**Data available per quest page**:
- Quest name, description/walkthrough
- Starting NPC name + ID (in URL: `/db/npc.html?id=XXX`)
- Starting zone name + ID
- Level range (min/max)
- Expansion
- Class/race restrictions
- Repeatable flag, monster mission flag
- Quest items (with item IDs in links)
- Related NPCs (with IDs)
- Related zones (with IDs)
- Faction changes (faction name + numeric amount)
- Reward items (with IDs)
- Quest chain (ordered list of related quest links)

### Option B: P99 Wiki (wiki.project1999.com)

**Pros**: Community-curated for classic EQ specifically, wiki format is simpler to parse.
**Cons**: Less structured data, MediaWiki markup, may have gaps.

**Key URLs**:
- Quest pages: `https://wiki.project1999.com/QUEST_NAME`
- Quest categories: `https://wiki.project1999.com/Category:Quests`

**Recommendation**: Start with Allakhazam as primary source since it has structured IDs that map directly to the game database. Use P99 Wiki as a supplemental source for description/walkthrough content if Allakhazam's is thin.

---

## Implementation Requirements

### File Location
`quests/management/commands/populate_quests.py`

### Command Interface
```bash
# Populate all quests from a specific zone
python manage.py populate_quests --zone qeynos

# Populate a specific quest by Allakhazam ID
python manage.py populate_quests --alla-id 1234

# Populate all quests up to a specific expansion
python manage.py populate_quests --expansion 4  # Through PoP

# Dry run (parse and print, don't save)
python manage.py populate_quests --zone qeynos --dry-run

# Verbose output
python manage.py populate_quests --zone qeynos --verbosity 2
```

### Mapping Requirements

The script needs to map between Allakhazam IDs and local game database IDs:

1. **NPCs**: Allakhazam NPC IDs may not match EQEmu NPC IDs. The script should:
   - Try to match by NPC name against `npc_types` table in game_database
   - Store Allakhazam NPC ID as a fallback
   - Log unmatched NPCs for manual review

2. **Items**: Same issue — match by name against `items` table in game_database.

3. **Zones**: Map Allakhazam zone IDs to `ZONE_SHORT_TO_LONG` short names. A mapping dict will be needed. The `zone` table in game_database has `zone_id_number` and `short_name`.

4. **Factions**: Match by name against `faction_list` table in game_database.

### Zone ID Mapping (Allakhazam → game_database)

This mapping needs to be built. The script should:
1. First attempt: look up zones in the game_database `zone` table by long_name similarity
2. Fallback: maintain a manual `ALLA_ZONE_MAP` dict for known mappings
3. Log any zones that couldn't be mapped

### Parsing Strategy

For Allakhazam pages, use `BeautifulSoup` (bs4) to parse HTML:

1. **Quest detail page** (`/db/quest.html?quest=XXX`):
   - Quest name: `<title>` or main `<h1>` heading
   - Starting NPC: look for "Started By" or "Quest Giver" field, extract NPC link
   - Zone: extract from zone link
   - Level: extract min/max from metadata panel
   - Class/Race: parse restriction lists
   - Quest items: extract item links from the items section
   - Rewards: parse reward section for item links and currency
   - Faction: parse faction change table
   - Description: extract main content area text
   - Quest chain: extract ordered quest link list

2. **Zone quest index** (`/db/qsearch.html?zone=XXX`):
   - Parse the results table for quest IDs and names
   - Use these to build a list of quest IDs to fetch individually

### Rate Limiting

- Add a configurable delay between requests (default: 1-2 seconds)
- Use `--delay` flag to override
- Cache raw HTML responses to a local directory (`quests/cache/`) to avoid re-fetching
- Use `--no-cache` to force fresh fetches

### Idempotency

- Use `Quests.name` (unique) as the natural key for upsert logic
- `update_or_create` for all models
- For M2M relationships, clear and re-add on update
- Log whether each quest was created or updated

### Error Handling

- Log and skip individual quests that fail to parse
- Continue processing remaining quests
- Print summary at end: X created, Y updated, Z failed
- Save failed quest IDs/URLs to a log file for manual review

### Dependencies

```
beautifulsoup4
requests
```

These should already be available or added to requirements.txt.

---

## Data Transformation Rules

### Expansion Mapping
Allakhazam expansion names need to map to the integer choices:
```python
ALLA_EXPANSION_MAP = {
    "classic": 0, "original": 0, "vanilla": 0,
    "ruins of kunark": 1, "kunark": 1,
    "scars of velious": 2, "velious": 2,
    "shadows of luclin": 3, "luclin": 3,
    "planes of power": 4, "pop": 4,
    "legacy of ykesha": 5, "ykesha": 5,
    "lost dungeons of norrath": 6, "ldon": 6,
    "gates of discord": 7, "god": 7,
    "omens of war": 8, "oow": 8,
    "dragons of norrath": 9, "don": 9,
    "depths of darkhollow": 10, "dodh": 10,
}
```

### Class Restriction Mapping
Allakhazam class names need to map to integer IDs:
```python
ALLA_CLASS_MAP = {
    "warrior": 1, "cleric": 2, "paladin": 3, "ranger": 4,
    "shadow knight": 5, "shadowknight": 5,
    "druid": 6, "monk": 7, "bard": 8, "rogue": 9,
    "shaman": 10, "necromancer": 11, "wizard": 12,
    "magician": 13, "enchanter": 14, "beastlord": 15,
}
```

### Description Formatting
- Convert Allakhazam HTML content to Markdown
- Preserve NPC dialogue formatting (use blockquotes)
- Convert step-by-step instructions to Markdown task lists:
  ```markdown
  - [ ] Step 1: Hail NPC in zone
  - [ ] Step 2: Collect 4 items
  ```
  This integrates with the existing checkbox-cookie-manager.js on the detail page.

### Quest Chains
- Process quest chains in a second pass after all quests are created
- Match by quest name to set `prerequisite` FK

---

## Output Format

The command should print progress like:
```
Fetching quest list for zone: qeynos2 ...
  Found 12 quests
  [1/12] Creating "Stein of Moggok" ... CREATED
  [2/12] Creating "Bayle's Heraldic Crest" ... UPDATED (already existed)
  [3/12] Creating "Corrupt Guards" ... FAILED (could not match NPC "Guard_Smith")
  ...
  Linking quest chains ...
  [1/3] "Stein of Moggok" -> "Firebeetle Eyes" ... LINKED
  ...

Summary:
  Created: 9
  Updated: 2
  Failed: 1
  Chains linked: 3
```

---

## Testing

The command should support a `--dry-run` flag that:
1. Fetches and parses data normally
2. Prints what would be created/updated
3. Does not write to the database

---

## Key Files to Reference

- `quests/models.py` — All model definitions and choice constants
- `quests/managers.py` — Custom queryset methods
- `common/constants.py` — `ZONE_SHORT_TO_LONG` mapping
- `common/models/zones.py` — Zone model (game_database)
- `common/models/npcs.py` — NPCTypes model (game_database)
- `common/models/items.py` — Items model (game_database)
- Existing management commands in other apps for Django command patterns used in this project
