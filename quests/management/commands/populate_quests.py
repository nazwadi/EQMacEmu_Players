"""
Management command: populate_quests

Populates the quests database from Allakhazam (scraping) or the P99 Wiki
(XML export). Idempotent — safe to re-run; uses quest name as natural key.

--- Allakhazam usage ---
    python manage.py populate_quests --source alla --alla-id 1234
    python manage.py populate_quests --source alla --zone qeynos
    python manage.py populate_quests --source alla --expansion 4
    python manage.py populate_quests --source alla --zone qeynos --dry-run
    python manage.py populate_quests --source alla --zone qeynos --delay 2.0 --no-cache

--- P99 Wiki XML usage ---
    python manage.py populate_quests --source p99 --xml ~/Downloads/Project+1999+Wiki-*.xml
    python manage.py populate_quests --source p99 --xml export.xml --dry-run
    python manage.py populate_quests --source p99 --xml export.xml --quest "Stein of Moggok"
"""
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.models.items import Items
from common.models.npcs import NPCTypes
from common.models.zones import Zone
from quests.models import (
    EXPANSION_INTRODUCED_CHOICES,
    CurrencyReward,
    ExperienceReward,
    FactionReward,
    ItemReward,
    QuestFaction,
    QuestItem,
    Quests,
    QuestsRelatedNPC,
    QuestsRelatedZone,
)

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

ALLA_BASE = "https://everquest.allakhazam.com"
CACHE_DIR = Path(__file__).resolve().parents[3] / "cache"

ALLA_CLASS_MAP = {
    "warrior": 1, "cleric": 2, "paladin": 3, "ranger": 4,
    "shadow knight": 5, "shadowknight": 5,
    "druid": 6, "monk": 7, "bard": 8, "rogue": 9,
    "shaman": 10, "necromancer": 11, "wizard": 12,
    "magician": 13, "enchanter": 14, "beastlord": 15,
}

ALLA_RACE_MAP = {
    "human": 1, "barbarian": 2, "erudite": 3,
    "wood elf": 4, "woodelf": 4,
    "high elf": 5, "highelf": 5,
    "dark elf": 6, "darkelf": 6,
    "half elf": 7, "halfelf": 7,
    "dwarf": 8, "troll": 9, "ogre": 10,
    "halfling": 11, "gnome": 12, "iksar": 13,
    "vah shir": 14, "vahshir": 14,
}

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

# P99 Wiki era template → expansion int
P99_ERA_EXPANSION_MAP = {
    "Classic Era": 0,
    "Temple Era": 0,       # Temple of Solusek Ro — classic content
    "Paineel Era": 0,      # Paineel opened with Kunark client patch, considered classic
    "HoleVP Era": 0,       # The Hole / VP — classic
    "Warrens Era": 0,      # The Warrens — classic
    "WarrensFearHateRevamp Era": 0,
    "Sky Era": 0,          # Plane of Sky — classic
    "EpicQuests Era": 1,   # Epic 1.0 quests introduced with Kunark
    "Epics Era": 1,
    "Kunark Era": 1,
    "Stonebrunt Era": 1,   # Stonebrunt Mountains — Kunark era
    "Chardok Era": 1,
    "Chardok Revamp Era": 1,
    "Velious Era": 2,
    "Luclin Era": 3,
    "Unknown Era": 0,
}

# P99 Wiki zone long names → short names (supplement DB lookup for common mismatches)
P99_ZONE_NAME_MAP: dict[str, str] = {
    "Ak'Anon": "akanon",
    "Befallen": "befallen",
    "Blackburrow": "blackburrow",
    "Castle Mistmoore": "mistmoore",
    "Cazic-Thule": "cazicthule",
    "City of Mist": "citymist",
    "Crushbone": "crushbone",
    "Crystal Caverns": "crystalcaverns",
    "Dagnor's Cauldron": "cauldron",
    "Dragon Necropolis": "dragonscale",
    "East Commonlands": "ecommons",
    "East Freeport": "freporte",
    "East Karana": "eastkarana",
    "Eastern Wastelands": "eastwastes",
    "Erudin": "erudin",
    "Erudin Palace": "erudnint",
    "Everfrost Peaks": "everfrost",
    "Feerrott": "feerrott",
    "Field of Bone": "fieldofbone",
    "Firiona Vie": "firiona",
    "Frontier Mountains": "frontiermtns",
    "Gorge of King Xorbb": "beholder",
    "Greater Faydark": "gfaydark",
    "Grobb": "grobb",
    "Highpass Hold": "highpass",
    "High Keep": "highkeep",
    "Iceclad Ocean": "iceclad",
    "Innothule Swamp": "innothule",
    "Kaesora": "kaesora",
    "Kael Drakkel": "kael",
    "Kedge Keep": "kedge",
    "Kithicor Forest": "kithicor",
    "Kurn's Tower": "kurn",
    "Lake of Ill Omen": "lakeofillomen",
    "Lake Rathetear": "lakerathe",
    "Lesser Faydark": "lfaydark",
    "Lower Guk": "guktop",
    "Najena": "najena",
    "Neriak - Commons": "neriakb",
    "Neriak - Foreign Quarter": "neriaka",
    "Neriak - Third Gate": "neriakc",
    "North Freeport": "freportn",
    "North Karana": "northkarana",
    "North Qeynos": "qeynos",
    "Northern Desert of Ro": "nro",
    "Northern Felwithe": "felwithea",
    "Ocean of Tears": "oot",
    "Oggok": "oggok",
    "Old Sebilis": "sebilis",
    "Overthere": "overthere",
    "Paineel": "paineel",
    "Plane of Air": "airplane",
    "Plane of Fear": "fearplane",
    "Plane of Growth": "growth",
    "Plane of Hate": "hateplane",
    "Plane of Sky": "airplane",
    "Plane of Mischief": "mischiefplane",
    "Plane of Valor": "povalor",
    "Qeynos Hills": "qeynoshire",
    "Rathe Mountains": "rathemtn",
    "Rivervale": "rivervale",
    "Runnyeye Citadel": "runnyeye",
    "Shadeweaver's Thicket": "shadeweavers",
    "Siren's Grotto": "sirens",
    "Skyfire Mountains": "skyfire",
    "Sleeper's Tomb": "sleeper",
    "South Karana": "southkarana",
    "Southern Desert of Ro": "sro",
    "Southern Felwithe": "felwitheb",
    "Splitpaw Lair": "paw",
    "Steamfont Mountains": "steamfont",
    "Surefall Glade": "qrg",
    "Temple of Solusek Ro": "soltemple",
    "Temple of Veeshan": "templeveeshan",
    "The Arena": "arena",
    "The Burning Wood": "burningwood",
    "The Commonlands": "commons",
    "The Estate of Unrest": "unrest",
    "The Feerott": "feerrott",
    "The Great Divide": "greatdivide",
    "The Hole": "hole",
    "The Lair of Terris Thule": "thulefore",
    "The Ruins of Old Guk": "gukbottom",
    "The Warrens": "warrens",
    "Timorous Deep": "timorous",
    "Trakanon's Teeth": "trakanon",
    "Tunare's Children": "nexus",
    "Upper Guk": "guktop",
    "Veeshan's Peak": "vp",
    "Velketor's Labyrinth": "velketor",
    "Wakening Land": "wakening",
    "West Commonlands": "commons",
    "West Freeport": "freportw",
    "West Karana": "westkarana",
    "Warslik's Woods": "warslikswood",
    "Plane of Tranquility": "potranquility",
    "Nexus": "nexus",
    "Ssraeshza Temple": "ssratemple",
    "Acrylia Caverns": "acrylia",
    "Fungus Grove": "fungusgrove",
    "Grieg's End": "griegsend",
    "The Scarlet Desert": "scarlet",
    "Umbral Plains": "umbral",
    "Vex Thal": "vexthal",
    "Ruins of Lxanvom": "kodtaz",
}

# Manual Allakhazam zone_id → game_database short_name overrides.
ALLA_ZONE_MAP: dict[int, str] = {}


# ---------------------------------------------------------------------------
# HTTP / cache helpers (Allakhazam)
# ---------------------------------------------------------------------------

def _cache_path(url: str) -> Path:
    key = hashlib.md5(url.encode()).hexdigest()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{key}.html"


def fetch(url: str, *, use_cache: bool, delay: float, session: requests.Session) -> str:
    if use_cache:
        path = _cache_path(url)
        if path.exists():
            return path.read_text(encoding="utf-8")

    time.sleep(delay)
    response = session.get(url, timeout=20)
    response.raise_for_status()
    html = response.text

    if use_cache:
        _cache_path(url).write_text(html, encoding="utf-8")

    return html


# ---------------------------------------------------------------------------
# Game DB lookup helpers (shared)
# ---------------------------------------------------------------------------

def _lookup_npc_id(alla_npc_id: int | None, npc_name: str) -> int:
    if npc_name:
        clean = npc_name.replace("_", " ").strip()
        match = NPCTypes.objects.filter(name__iexact=clean).first()
        if not match:
            match = NPCTypes.objects.filter(name__icontains=clean).first()
        if match:
            return match.id
    return alla_npc_id or 0


def _lookup_item_id(alla_item_id: int | None, item_name: str) -> int:
    if item_name:
        match = Items.objects.filter(Name__iexact=item_name).first()
        if match:
            return match.id
    return alla_item_id or 0


def _lookup_zone_short_name(alla_zone_id: int | None, zone_long_name: str) -> str | None:
    # Manual P99 override map first
    if zone_long_name and zone_long_name in P99_ZONE_NAME_MAP:
        return P99_ZONE_NAME_MAP[zone_long_name]

    if alla_zone_id and alla_zone_id in ALLA_ZONE_MAP:
        return ALLA_ZONE_MAP[alla_zone_id]

    if zone_long_name:
        clean = zone_long_name.strip()
        match = Zone.objects.filter(long_name__iexact=clean).first()
        if not match:
            match = Zone.objects.filter(long_name__icontains=clean).first()
        if match:
            return match.short_name

    return None


def _lookup_faction_id(faction_name: str) -> int:
    try:
        from django.db import connections
        cursor = connections["game_database"].cursor()
        cursor.execute("SELECT id FROM faction_list WHERE name = %s LIMIT 1", [faction_name])
        row = cursor.fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# DB save logic (shared)
# ---------------------------------------------------------------------------

def _get_or_create_quest_item(item_id: int, name: str) -> QuestItem:
    obj, _ = QuestItem.objects.get_or_create(item_id=item_id, name=name[:64])
    return obj


def _get_or_create_related_npc(npc_id: int, name: str) -> QuestsRelatedNPC:
    obj, _ = QuestsRelatedNPC.objects.get_or_create(npc_id=npc_id, defaults={"name": name[:64]})
    return obj


def _get_or_create_related_zone(zone_id: int, short_name: str, long_name: str) -> QuestsRelatedZone:
    obj, _ = QuestsRelatedZone.objects.get_or_create(
        short_name=short_name,
        defaults={"zone_id": zone_id, "long_name": long_name},
    )
    return obj


def save_quest(data: dict, dry_run: bool, verbosity: int, stdout) -> str:
    """
    Upsert a quest from a normalized data dict.
    Returns 'CREATED', 'UPDATED', or 'SKIPPED' (dry-run).
    """
    if dry_run:
        if verbosity >= 2:
            stdout.write(f"    [DRY RUN] Would upsert: {data['name']!r}")
            stdout.write(f"      Zone: {data.get('starting_zone_name')} → {data.get('_resolved_zone', '?')}")
            stdout.write(f"      NPC:  {data.get('starting_npc_name')} → {data.get('_resolved_npc_id', '?')}")
            stdout.write(f"      Items: {[i['name'] for i in data.get('quest_items', [])]}")
            stdout.write(f"      Reward items: {[i['name'] for i in data.get('rewards_items', [])]}")
        return "SKIPPED"

    starting_npc_eqemu_id = _lookup_npc_id(data.get("starting_npc_id"), data.get("starting_npc_name") or "")
    starting_zone_short = _lookup_zone_short_name(
        data.get("starting_zone_alla_id"), data.get("starting_zone_name") or ""
    )

    quest_defaults = {
        "description": data.get("description", ""),
        "starting_npc_id": starting_npc_eqemu_id,
        "starting_zone": starting_zone_short or "",
        "expansion_introduced": data.get("expansion_introduced", 0),
        "minimum_level": data.get("minimum_level", 1),
        "maximum_level": data.get("maximum_level", -1),
        "class_restrictions": data.get("class_restriction", -1),
        "race_restrictions": data.get("race_restriction", -1),
        "is_repeatable": data.get("is_repeatable", True),
        "monster_mission": data.get("monster_mission", False),
        "difficulty_rating": data.get("difficulty_rating", 3),
        "status": "draft",
    }

    with transaction.atomic():
        quest, created = Quests.objects.update_or_create(
            name=data["name"],
            defaults=quest_defaults,
        )

        # Quest items
        quest_item_objs = []
        for qi in data.get("quest_items", []):
            eid = _lookup_item_id(qi.get("alla_item_id"), qi["name"])
            quest_item_objs.append(_get_or_create_quest_item(eid, qi["name"][:64]))
        quest.quest_items.set(quest_item_objs)

        # Related NPCs
        related_npc_objs = []
        for rn in data.get("related_npcs", []):
            eid = _lookup_npc_id(rn.get("alla_npc_id"), rn["name"])
            if eid:
                related_npc_objs.append(_get_or_create_related_npc(eid, rn["name"][:64]))
        quest.related_npcs.set(related_npc_objs)

        # Related zones
        related_zone_objs = []
        for rz in data.get("related_zones", []):
            short = _lookup_zone_short_name(rz.get("alla_zone_id"), rz["name"])
            if short:
                db_zone = Zone.objects.filter(short_name=short).first()
                zone_id_num = db_zone.zone_id_number if db_zone else 0
                related_zone_objs.append(_get_or_create_related_zone(zone_id_num, short, rz["name"]))
        quest.related_zones.set(related_zone_objs)

        # Factions
        quest.quest_factions.all().delete()
        for role, faction_list in (
            ("required", data.get("factions_required", [])),
            ("raised", data.get("factions_raised", [])),
            ("lowered", data.get("factions_lowered", [])),
        ):
            for f in faction_list:
                faction_id = _lookup_faction_id(f["name"])
                QuestFaction.objects.create(
                    quest=quest,
                    faction_id=faction_id,
                    name=f["name"][:50],
                    role=role,
                )

        # Item rewards
        quest.itemreward_rewards.all().delete()
        for ri in data.get("rewards_items", []):
            eid = _lookup_item_id(ri.get("alla_item_id"), ri["name"])
            ItemReward.objects.create(
                quest=quest,
                item_id=eid,
                item_name=ri["name"][:100],
                quantity=ri.get("quantity", 1),
            )

        # Currency rewards
        cur = data.get("rewards_currency", {})
        if any(cur.get(c, 0) for c in ("platinum", "gold", "silver", "copper")):
            quest.currencyreward_rewards.all().delete()
            CurrencyReward.objects.create(
                quest=quest,
                platinum=cur.get("platinum", 0),
                gold=cur.get("gold", 0),
                silver=cur.get("silver", 0),
                copper=cur.get("copper", 0),
            )

        # XP rewards
        if data.get("rewards_xp"):
            quest.experiencereward_rewards.all().delete()
            ExperienceReward.objects.create(
                quest=quest,
                amount=data["rewards_xp"],
                is_percentage=False,
            )

    return "CREATED" if created else "UPDATED"


# ---------------------------------------------------------------------------
# Quest chain linking (shared, second pass)
# ---------------------------------------------------------------------------

def link_quest_chains(chain_data: list[tuple[str, list[str]]], dry_run: bool, stdout) -> int:
    linked = 0
    for quest_name, chain in chain_data:
        if len(chain) < 2:
            continue
        for i, name in enumerate(chain):
            if i == 0:
                continue
            prev_name = chain[i - 1]
            if dry_run:
                stdout.write(f"  [DRY RUN] Would link: {prev_name!r} -> {name!r}")
                linked += 1
                continue
            try:
                current = Quests.objects.get(name=name)
                previous = Quests.objects.get(name=prev_name)
                if current.prerequisite_id != previous.pk:
                    current.prerequisite = previous
                    current.save(update_fields=["prerequisite"])
                    linked += 1
            except Quests.DoesNotExist:
                pass
    return linked


# ===========================================================================
# ALLAKHAZAM PARSER
# ===========================================================================

def _extract_id_from_href(href: str, param: str) -> int | None:
    m = re.search(rf'[?&]{re.escape(param)}=(\d+)', href or "")
    return int(m.group(1)) if m else None


def _alla_text(el) -> str:
    return el.get_text(separator=" ", strip=True) if el else ""


def _parse_currency(text: str) -> dict:
    result = {"platinum": 0, "gold": 0, "silver": 0, "copper": 0}
    for coin in ("platinum", "gold", "silver", "copper"):
        m = re.search(rf'(\d+)\s+{coin}', text, re.IGNORECASE)
        if m:
            result[coin] = int(m.group(1))
    return result


def _html_to_markdown(el) -> str:
    lines = []
    for child in el.children:
        if hasattr(child, "name"):
            tag = child.name
            text = child.get_text(separator=" ", strip=True)
            if not text:
                continue
            if tag in ("h1", "h2", "h3", "h4"):
                lines.append(f"{'#' * int(tag[1])} {text}")
            elif tag == "p":
                lines.append(text)
            elif tag in ("ul", "ol"):
                for li in child.find_all("li"):
                    lines.append(f"- {li.get_text(strip=True)}")
            elif tag == "blockquote":
                lines.append(f"> {text}")
            else:
                lines.append(text)
        else:
            t = str(child).strip()
            if t:
                lines.append(t)
    return "\n\n".join(lines)


def parse_zone_quest_list(html: str) -> list[int]:
    soup = BeautifulSoup(html, "html.parser")
    quest_ids = []
    for a in soup.select('a[href*="quest.html"]'):
        qid = _extract_id_from_href(a.get("href", ""), "quest")
        if qid:
            quest_ids.append(qid)
    return list(dict.fromkeys(quest_ids))


def parse_alla_quest_detail(html: str, alla_quest_id: int) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    name = _alla_text(h1).strip()
    if not name:
        title = soup.find("title")
        name = _alla_text(title).split("-")[0].strip()
    if not name:
        return None

    data: dict = {
        "alla_quest_id": alla_quest_id,
        "name": name,
        "description": "",
        "starting_npc_id": None,
        "starting_npc_name": None,
        "starting_zone_alla_id": None,
        "starting_zone_name": None,
        "expansion_introduced": 0,
        "minimum_level": 1,
        "maximum_level": -1,
        "class_restriction": -1,
        "race_restriction": -1,
        "is_repeatable": True,
        "monster_mission": False,
        "difficulty_rating": 3,
        "quest_items": [],
        "related_npcs": [],
        "related_zones": [],
        "factions_required": [],
        "factions_raised": [],
        "factions_lowered": [],
        "rewards_items": [],
        "rewards_currency": {},
        "rewards_xp": None,
        "quest_chain": [],
    }

    for row in soup.select("table tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        key = _alla_text(cells[0]).lower().rstrip(":")
        val_cell = cells[1]
        val = _alla_text(val_cell)

        if "started by" in key or "quest giver" in key or "given by" in key:
            a = val_cell.find("a", href=re.compile(r'npc\.html'))
            if a:
                data["starting_npc_name"] = _alla_text(a)
                data["starting_npc_id"] = _extract_id_from_href(a.get("href", ""), "id")

        elif ("zone" in key and "starting" in key) or key in ("zone", "location"):
            a = val_cell.find("a", href=re.compile(r'zone\.html'))
            if a:
                data["starting_zone_name"] = _alla_text(a)
                data["starting_zone_alla_id"] = _extract_id_from_href(a.get("href", ""), "id")

        elif "expansion" in key:
            exp_lower = val.lower()
            for exp_name, exp_id in ALLA_EXPANSION_MAP.items():
                if exp_name in exp_lower:
                    data["expansion_introduced"] = exp_id
                    break

        elif "level" in key:
            nums = re.findall(r'\d+', val)
            if len(nums) >= 2:
                data["minimum_level"] = int(nums[0])
                data["maximum_level"] = int(nums[1])
            elif len(nums) == 1:
                data["minimum_level"] = int(nums[0])

        elif "class" in key:
            class_lower = val.lower()
            for cls_name, cls_id in ALLA_CLASS_MAP.items():
                if cls_name in class_lower:
                    data["class_restriction"] = cls_id
                    break

        elif "race" in key:
            race_lower = val.lower()
            for race_name, race_id in ALLA_RACE_MAP.items():
                if race_name in race_lower:
                    data["race_restriction"] = race_id
                    break

        elif "repeatable" in key:
            data["is_repeatable"] = val.lower() not in ("no", "false", "0")

        elif "monster mission" in key:
            data["monster_mission"] = val.lower() in ("yes", "true", "1")

    for a in soup.select('a[href*="item.html"]'):
        item_id = _extract_id_from_href(a.get("href", ""), "item")
        if item_id:
            data["quest_items"].append({"alla_item_id": item_id, "name": _alla_text(a)})

    for a in soup.select('a[href*="npc.html"]'):
        npc_id = _extract_id_from_href(a.get("href", ""), "id")
        if npc_id:
            data["related_npcs"].append({"alla_npc_id": npc_id, "name": _alla_text(a)})

    for a in soup.select('a[href*="zone.html"]'):
        zone_id = _extract_id_from_href(a.get("href", ""), "id")
        if zone_id:
            data["related_zones"].append({"alla_zone_id": zone_id, "name": _alla_text(a)})

    desc_el = (
        soup.find(id=re.compile(r'walkthrough|description|content', re.I))
        or soup.find(class_=re.compile(r'walkthrough|description|content', re.I))
    )
    if desc_el:
        data["description"] = _html_to_markdown(desc_el)
    else:
        paragraphs = soup.find_all("p")
        if paragraphs:
            largest = max(paragraphs, key=lambda p: len(p.get_text()))
            data["description"] = _alla_text(largest)

    for row in soup.select("table tr"):
        row_text = _alla_text(row).lower()
        if any(c in row_text for c in ("platinum", "gold", "silver", "copper")):
            data["rewards_currency"] = _parse_currency(_alla_text(row))
            break

    for row in soup.select("table tr"):
        row_text = _alla_text(row).lower()
        if "experience" in row_text:
            m = re.search(r'(\d[\d,]*)\s*(?:experience|xp)', row_text)
            if m:
                data["rewards_xp"] = int(m.group(1).replace(",", ""))
                break

    reward_section = soup.find(string=re.compile(r'reward', re.I))
    if reward_section:
        reward_container = reward_section.find_parent()
        if reward_container:
            for a in reward_container.find_all_next("a", href=re.compile(r'item\.html')):
                item_id = _extract_id_from_href(a.get("href", ""), "item")
                if item_id:
                    qty_m = re.search(r'(\d+)x?\s*$', _alla_text(a.parent))
                    qty = int(qty_m.group(1)) if qty_m else 1
                    data["rewards_items"].append({
                        "alla_item_id": item_id,
                        "name": _alla_text(a),
                        "quantity": qty,
                    })
                if len(data["rewards_items"]) > 20:
                    break

    chain_section = soup.find(string=re.compile(r'quest chain|related quests', re.I))
    if chain_section:
        chain_container = chain_section.find_parent()
        if chain_container:
            for a in chain_container.find_all_next("a", href=re.compile(r'quest\.html')):
                data["quest_chain"].append(_alla_text(a))
                if len(data["quest_chain"]) > 20:
                    break

    return data


# ===========================================================================
# P99 WIKI XML PARSER
# ===========================================================================

MW_NS = "http://www.mediawiki.org/xml/export-0.8/"

# Wikitext link: [[Some Name]] or [[Some Name|display]]
_WIKI_LINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
# Item template: {{:Item Name}} or {{Item Name}}
_ITEM_TEMPLATE_RE = re.compile(r'\{\{:?([^}|]+?)\}\}')
# Section header: == Section ==
_SECTION_RE = re.compile(r'^==+\s*(.+?)\s*==+$', re.MULTILINE)
# Wiki table row: ! key or | value
_TABLE_ROW_RE = re.compile(r'^[!|]\s*(.+)$', re.MULTILINE)


def _strip_wiki_markup(text: str) -> str:
    """Remove common wikitext markup, returning plain text."""
    # Remove templates like {{...}} — simple non-nested pass
    text = re.sub(r'\{\{[^{}]*\}\}', '', text)
    # Extract link display text [[Target|Display]] → Display, or [[Target]] → Target
    text = re.sub(r'\[\[(?:[^\]|]+\|)?([^\]]+)\]\]', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def _wikitext_to_markdown(wikitext: str) -> str:
    """
    Convert a wikitext walkthrough section to Markdown.
    Handles: headings, bullet lists, NPC dialogue (colon-indented lines),
    wiki links, and the CheckboxList / End templates.
    """
    lines = []
    for raw_line in wikitext.splitlines():
        line = raw_line.rstrip()

        # Skip template markers we don't need in the description
        if re.match(r'^\{\{(CheckboxList|end|End|Classic Era|Kunark Era|Velious Era|Luclin Era|\w+\s*Era)\}\}', line):
            continue

        # Section headers === Foo === → ### Foo
        m = re.match(r'^(=+)\s*(.+?)\s*=+$', line)
        if m:
            level = min(len(m.group(1)), 4)
            lines.append(f"{'#' * level} {_strip_wiki_markup(m.group(2))}")
            continue

        # Bullet list items * text → - text, with nesting
        m = re.match(r'^(\*+)\s*(.+)$', line)
        if m:
            depth = len(m.group(1)) - 1
            indent = "  " * depth
            content = _strip_wiki_markup(m.group(2))
            lines.append(f"{indent}- {content}")
            continue

        # NPC dialogue: colon-indented lines → blockquote
        m = re.match(r'^(:+)\s*(.+)$', line)
        if m:
            content = _strip_wiki_markup(m.group(2))
            lines.append(f"> {content}")
            continue

        # Definition list terms ; term → **term**
        m = re.match(r'^;\s*(.+)$', line)
        if m:
            lines.append(f"**{_strip_wiki_markup(m.group(1))}**")
            continue

        # Numbered list # item → 1. item
        m = re.match(r'^(#+)\s*(.+)$', line)
        if m:
            content = _strip_wiki_markup(m.group(2))
            lines.append(f"1. {content}")
            continue

        # Wiki table syntax — skip row separators
        if line in ('|-', '{|', '|}') or line.startswith('{| '):
            continue

        # Plain line (may still have markup)
        stripped = _strip_wiki_markup(line)
        if stripped:
            lines.append(stripped)

    # Collapse consecutive blank lines
    result = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank

    return "\n".join(result).strip()


def _parse_p99_top_table(wikitext: str) -> dict:
    """
    Parse the questTopTable wikitext block into a dict of field → value strings.
    Returns e.g. {'Start Zone': 'Rivervale', 'Quest Giver': 'Marshal Anrey', ...}
    """
    m = re.search(r'\{\|[^\n]*questTopTable.*?\|\}', wikitext, re.DOTALL)
    if not m:
        return {}

    table_text = m.group(0)
    fields = {}
    current_key = None

    for line in table_text.splitlines():
        line = line.strip()
        if line.startswith("!"):
            # Key cell: ! ''' Start Zone: '''
            current_key = re.sub(r"'''|[!|]", '', line).strip().rstrip(":").strip()
        elif line.startswith("|") and not line.startswith("|-") and not line.startswith("|{") and not line.startswith("|}"):
            if current_key:
                raw_val = line.lstrip("|").strip()
                fields[current_key] = raw_val
                current_key = None

    return fields


def _get_section(wikitext: str, section_name: str) -> str:
    """Extract the content of a == Section == from wikitext.
    Handles inline templates on the heading line (e.g. == Checklist =={{CheckboxList}}).
    """
    # .*? after the closing == consumes any inline content (e.g. {{CheckboxList}}) before \n
    pattern = rf'==\s*{re.escape(section_name)}\s*==.*?\n(.*?)(?=\n==|\Z)'
    m = re.search(pattern, wikitext, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def parse_p99_page(title: str, wikitext: str) -> dict | None:
    """
    Parse a single P99 Wiki quest page (wikitext) into a normalized data dict.
    Returns None if the page doesn't look like a parseable quest.
    """
    if not wikitext or "questTopTable" not in wikitext:
        return None

    # Strip the page title's trailing " Quest" if present, for cleaner DB names
    name = title.rstrip()

    fields = _parse_p99_top_table(wikitext)
    if not fields:
        return None

    data: dict = {
        "name": name,
        "description": "",
        "starting_npc_id": None,
        "starting_npc_name": None,
        "starting_zone_alla_id": None,
        "starting_zone_name": None,
        "expansion_introduced": 0,
        "minimum_level": 1,
        "maximum_level": -1,
        "class_restriction": -1,
        "race_restriction": -1,
        "is_repeatable": True,
        "monster_mission": False,
        "difficulty_rating": 3,
        "quest_items": [],
        "related_npcs": [],
        "related_zones": [],
        "factions_required": [],
        "factions_raised": [],
        "factions_lowered": [],
        "rewards_items": [],
        "rewards_currency": {},
        "rewards_xp": None,
        "quest_chain": [],
    }

    # --- Era → expansion ---
    era_m = re.match(r'\{\{(\w[\w\s]*Era)\}\}', wikitext.strip())
    if era_m:
        era = era_m.group(1)
        data["expansion_introduced"] = P99_ERA_EXPANSION_MAP.get(era, 0)

    # --- questTopTable fields ---
    for raw_key, raw_val in fields.items():
        key = raw_key.strip().lower()
        val_plain = _strip_wiki_markup(raw_val).strip()

        if "start zone" in key or "starting zone" in key:
            # Extract zone name from [[Zone Name]] link
            link_m = re.search(r'\[\[([^\]|]+)', raw_val)
            data["starting_zone_name"] = link_m.group(1).strip() if link_m else val_plain

        elif "quest giver" in key or "started by" in key or "given by" in key:
            link_m = re.search(r'\[\[([^\]|]+)', raw_val)
            data["starting_npc_name"] = link_m.group(1).strip() if link_m else val_plain

        elif "minimum level" in key or "min level" in key or key == "level":
            nums = re.findall(r'\d+', val_plain)
            if nums:
                data["minimum_level"] = int(nums[0])

        elif "classes" in key or "class" in key:
            val_lower = val_plain.lower()
            if val_lower in ("all", "all classes", "any"):
                data["class_restriction"] = -1
            else:
                for cls_name, cls_id in ALLA_CLASS_MAP.items():
                    if cls_name in val_lower:
                        data["class_restriction"] = cls_id
                        break

        elif "related zones" in key or "related zone" in key:
            for link_m in _WIKI_LINK_RE.finditer(raw_val):
                zone_name = link_m.group(1).strip()
                data["related_zones"].append({"alla_zone_id": None, "name": zone_name})

        elif "related npcs" in key or "related npc" in key:
            for link_m in _WIKI_LINK_RE.finditer(raw_val):
                npc_name = link_m.group(1).strip()
                data["related_npcs"].append({"alla_npc_id": None, "name": npc_name})

        elif key == "faction":
            # Required faction: [[Faction Name]] (description)
            for link_m in _WIKI_LINK_RE.finditer(raw_val):
                faction_name = link_m.group(1).strip()
                data["factions_required"].append({"name": faction_name})

    # --- Reward section: item names from {{:Item Name}} templates ---
    reward_section = _get_section(wikitext, "Reward")
    if reward_section:
        for tmpl_m in _ITEM_TEMPLATE_RE.finditer(reward_section):
            item_name = tmpl_m.group(1).strip()
            if item_name and not item_name.startswith("#"):
                data["rewards_items"].append({"alla_item_id": None, "name": item_name})

    # --- Checklist / Walkthrough sections → quest_items ---
    checklist_section = _get_section(wikitext, "Checklist")
    walkthrough_section = _get_section(wikitext, "Walkthrough")

    # Build exclusion sets: known zone names and related NPC names already captured
    known_zones = set(P99_ZONE_NAME_MAP.keys()) | set(P99_ZONE_NAME_MAP.values())
    known_npcs = {n["name"].lower() for n in data["related_npcs"]}
    # Also exclude anything linked after "to [[", "from [[", "give [[", "hand [[", "hail [["
    # These are NPC turn-in targets, not quest items
    npc_context_re = re.compile(
        r'(?:to|from|give|hand|hail|speak|talk)\s+\[\[([^\]|]+)\]\]', re.IGNORECASE
    )

    checklist_items: set[str] = set()
    # Only scan the Checklist section — Walkthrough has too many incidental links
    for line in checklist_section.splitlines():
        line_stripped = line.strip().lstrip("*# ").strip()
        # Skip lines that are clearly about turning in to an NPC (not obtaining items)
        if re.match(r'(?:turn\s+in|give|hand|speak|hail|talk)', line_stripped, re.IGNORECASE):
            continue
        # Collect links on "obtain/get/loot/kill/find/collect/bring" lines
        is_obtain_line = bool(re.search(
            r'\b(?:obtain|get|loot|kill|find|collect|bring|farm|buy|purchase|craft|combine)\b',
            line_stripped, re.IGNORECASE
        ))
        # Also include lines that just list items without a verb (common in short checklists)
        has_link = bool(_WIKI_LINK_RE.search(line_stripped))
        if not (is_obtain_line or has_link):
            continue

        for link_m in _WIKI_LINK_RE.finditer(line_stripped):
            item_name = link_m.group(1).strip()
            if (
                item_name not in known_zones
                and item_name.lower() not in known_npcs
                and not item_name.startswith("User:")
                and not item_name.startswith("File:")
                # Skip lowercase-starting names — likely monsters/NPCs not items
                # (EQ items are almost always Title Case)
                and (item_name[0].isupper() if item_name else False)
            ):
                checklist_items.add(item_name)

    for item_name in checklist_items:
        data["quest_items"].append({"alla_item_id": None, "name": item_name})

    # --- Faction changes in walkthrough text ---
    # Pattern: "Your faction standing with [[Faction Name]] got better/worse"
    for faction_m in re.finditer(
        r'[Yy]our faction standing with \[\[([^\]]+)\]\] got (better|worse)',
        wikitext
    ):
        faction_name = faction_m.group(1).strip()
        direction = faction_m.group(2)
        entry = {"name": faction_name}
        if direction == "better":
            # Only add if not already in required (avoid duplication)
            if not any(f["name"] == faction_name for f in data["factions_raised"]):
                data["factions_raised"].append(entry)
        else:
            if not any(f["name"] == faction_name for f in data["factions_lowered"]):
                data["factions_lowered"].append(entry)

    # --- Description: combine Walkthrough + Checklist sections as Markdown ---
    desc_parts = []
    if checklist_section:
        desc_parts.append("## Checklist\n\n" + _wikitext_to_markdown(checklist_section))
    if walkthrough_section:
        desc_parts.append("## Walkthrough\n\n" + _wikitext_to_markdown(walkthrough_section))
    data["description"] = "\n\n---\n\n".join(desc_parts)

    return data


def load_p99_xml(xml_path: Path) -> list[dict]:
    """
    Parse the full P99 Wiki XML export and return a list of normalized quest dicts.
    Pages that don't parse as quests are silently skipped.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"mw": MW_NS}

    quests = []
    for page in root.findall("mw:page", ns):
        title_el = page.find("mw:title", ns)
        text_el = page.find(".//mw:text", ns)
        if title_el is None or text_el is None:
            continue
        title = title_el.text or ""
        wikitext = text_el.text or ""
        parsed = parse_p99_page(title, wikitext)
        if parsed:
            quests.append(parsed)

    return quests


# ===========================================================================
# Management command
# ===========================================================================

class Command(BaseCommand):
    help = "Populate quests from Allakhazam (--source alla) or P99 Wiki XML (--source p99)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source", choices=["alla", "p99"], default="p99",
            help="Data source: 'alla' for Allakhazam scraping, 'p99' for P99 Wiki XML (default: p99)",
        )

        # P99-specific
        p99_group = parser.add_argument_group("P99 Wiki options")
        p99_group.add_argument(
            "--xml", metavar="FILE",
            help="Path to P99 Wiki XML export file (required for --source p99)",
        )
        p99_group.add_argument(
            "--quest", metavar="QUEST_NAME",
            help="Process only the P99 page with this exact title (useful for testing)",
        )

        # Allakhazam-specific
        alla_group = parser.add_argument_group("Allakhazam options")
        alla_source = alla_group.add_mutually_exclusive_group()
        alla_source.add_argument("--zone", metavar="ZONE_SHORT_NAME",
                                 help="Populate all quests for this zone (e.g. qeynos)")
        alla_source.add_argument("--alla-id", type=int, metavar="QUEST_ID",
                                 help="Populate a single quest by Allakhazam quest ID")
        alla_source.add_argument("--expansion", type=int, metavar="EXP_ID",
                                 help="Populate all quests up to this expansion (0-10)")

        # Shared
        parser.add_argument("--dry-run", action="store_true",
                            help="Parse and display without writing to the database")
        parser.add_argument("--delay", type=float, default=1.5,
                            help="Seconds between Allakhazam requests (default: 1.5)")
        parser.add_argument("--no-cache", action="store_true",
                            help="Skip disk cache (Allakhazam only)")

    # -----------------------------------------------------------------------

    def handle(self, *args, **options):
        source = options["source"]
        dry_run = options["dry_run"]
        verbosity = options["verbosity"]

        if source == "p99":
            self._handle_p99(options, dry_run, verbosity)
        else:
            self._handle_alla(options, dry_run, verbosity)

    # -----------------------------------------------------------------------
    # P99 handler
    # -----------------------------------------------------------------------

    def _handle_p99(self, options, dry_run, verbosity):
        xml_path_str = options.get("xml")
        if not xml_path_str:
            raise CommandError("--xml FILE is required when using --source p99")

        xml_path = Path(xml_path_str).expanduser()
        if not xml_path.exists():
            raise CommandError(f"XML file not found: {xml_path}")

        self.stdout.write(f"Loading P99 Wiki XML: {xml_path} ...")
        all_quests = load_p99_xml(xml_path)
        self.stdout.write(f"  Parsed {len(all_quests)} quest pages")

        # Optional single-quest filter
        filter_title = options.get("quest")
        if filter_title:
            all_quests = [q for q in all_quests if q["name"] == filter_title]
            if not all_quests:
                raise CommandError(f"No quest found with title {filter_title!r}")

        total = len(all_quests)
        counts = {"CREATED": 0, "UPDATED": 0, "SKIPPED": 0, "FAILED": 0}
        failed_names: list[str] = []
        chain_data: list[tuple[str, list[str]]] = []

        for idx, data in enumerate(all_quests, 1):
            prefix = f"  [{idx}/{total}]"
            quest_name = data["name"]
            self.stdout.write(f"{prefix} Processing {quest_name!r} ...", ending=" ")
            try:
                result = save_quest(data, dry_run=dry_run, verbosity=verbosity, stdout=self.stdout)
                counts[result] += 1
                self.stdout.write(result)
                if data.get("quest_chain"):
                    chain_data.append((quest_name, data["quest_chain"]))
            except Exception as exc:
                self.stdout.write(f"FAILED ({exc})")
                counts["FAILED"] += 1
                failed_names.append(quest_name)
                if verbosity >= 2:
                    import traceback
                    self.stderr.write(traceback.format_exc())

        self._print_summary(counts, chain_data, failed_names, dry_run, is_ids=False)

    # -----------------------------------------------------------------------
    # Allakhazam handler
    # -----------------------------------------------------------------------

    def _handle_alla(self, options, dry_run, verbosity):
        delay = options["delay"]
        use_cache = not options["no_cache"]

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; EQArchives quest importer; educational use)"
        })

        alla_quest_ids: list[int] = []

        if options.get("alla_id"):
            alla_quest_ids = [options["alla_id"]]

        elif options.get("zone"):
            zone_short = options["zone"].lower()
            zone_obj = Zone.objects.filter(short_name__iexact=zone_short).first()
            if not zone_obj:
                raise CommandError(f"Zone '{zone_short}' not found in game database.")
            alla_zone_id = next((k for k, v in ALLA_ZONE_MAP.items() if v == zone_short), None)
            if alla_zone_id is None:
                raise CommandError(
                    f"No Allakhazam zone ID mapping found for '{zone_short}'.\n"
                    f"Add it to ALLA_ZONE_MAP in populate_quests.py and re-run."
                )
            url = f"{ALLA_BASE}/db/qsearch.html?zone={alla_zone_id}"
            self.stdout.write(f"Fetching quest list for zone: {zone_short} ...")
            html = fetch(url, use_cache=use_cache, delay=delay, session=session)
            alla_quest_ids = parse_zone_quest_list(html)
            self.stdout.write(f"  Found {len(alla_quest_ids)} quests")

        elif options.get("expansion") is not None:
            exp_max = options["expansion"]
            if exp_max not in EXPANSION_INTRODUCED_CHOICES:
                raise CommandError(f"Expansion ID {exp_max} is not valid (0-10).")
            self.stdout.write(f"Fetching quests up to expansion {exp_max} ({EXPANSION_INTRODUCED_CHOICES[exp_max]}) ...")
            seen: set[int] = set()
            for alla_zone_id, short_name in ALLA_ZONE_MAP.items():
                url = f"{ALLA_BASE}/db/qsearch.html?zone={alla_zone_id}"
                try:
                    html = fetch(url, use_cache=use_cache, delay=delay, session=session)
                    ids = parse_zone_quest_list(html)
                    new_ids = [i for i in ids if i not in seen]
                    alla_quest_ids.extend(new_ids)
                    seen.update(new_ids)
                    if verbosity >= 2:
                        self.stdout.write(f"  Zone {short_name}: {len(new_ids)} quests")
                except Exception as exc:
                    self.stderr.write(f"  Warning: failed to fetch zone {short_name}: {exc}")
            self.stdout.write(f"  Total quests to process: {len(alla_quest_ids)}")

        else:
            raise CommandError("Provide --alla-id, --zone, or --expansion when using --source alla")

        total = len(alla_quest_ids)
        counts = {"CREATED": 0, "UPDATED": 0, "SKIPPED": 0, "FAILED": 0}
        failed_ids: list[int] = []
        chain_data: list[tuple[str, list[str]]] = []

        for idx, alla_qid in enumerate(alla_quest_ids, 1):
            url = f"{ALLA_BASE}/db/quest.html?quest={alla_qid}"
            prefix = f"  [{idx}/{total}]"
            try:
                html = fetch(url, use_cache=use_cache, delay=delay, session=session)
                data = parse_alla_quest_detail(html, alla_qid)
                if not data:
                    self.stdout.write(f"{prefix} FAILED (could not parse quest {alla_qid})")
                    counts["FAILED"] += 1
                    failed_ids.append(alla_qid)
                    continue

                quest_name = data["name"]
                self.stdout.write(f"{prefix} Processing {quest_name!r} ...", ending=" ")
                result = save_quest(data, dry_run=dry_run, verbosity=verbosity, stdout=self.stdout)
                counts[result] += 1
                self.stdout.write(result)

                if data.get("quest_chain"):
                    chain_data.append((quest_name, data["quest_chain"]))

            except Exception as exc:
                self.stdout.write(f"{prefix} FAILED ({exc})")
                counts["FAILED"] += 1
                failed_ids.append(alla_qid)
                if verbosity >= 2:
                    import traceback
                    self.stderr.write(traceback.format_exc())

        self._print_summary(counts, chain_data, failed_ids, dry_run, is_ids=True)

    # -----------------------------------------------------------------------

    def _print_summary(self, counts, chain_data, failed, dry_run, is_ids):
        if chain_data:
            self.stdout.write("\nLinking quest chains ...")
            linked = link_quest_chains(chain_data, dry_run=dry_run, stdout=self.stdout)
            self.stdout.write(f"  Chains linked: {linked}")

        self.stdout.write("\nSummary:")
        self.stdout.write(f"  Created:  {counts['CREATED']}")
        self.stdout.write(f"  Updated:  {counts['UPDATED']}")
        if dry_run:
            self.stdout.write(f"  Skipped:  {counts['SKIPPED']}  (dry run)")
        self.stdout.write(f"  Failed:   {counts['FAILED']}")

        if failed:
            log_path = CACHE_DIR / ("failed_quest_ids.json" if is_ids else "failed_quest_names.json")
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            log_path.write_text(json.dumps(failed, indent=2))
            self.stderr.write(f"\nFailed entries saved to: {log_path}")
