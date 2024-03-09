from dataclasses import dataclass
from collections import namedtuple
from django.db import connections
from enum import Enum
from .models.faction import FactionListMod


class FactionValue(Enum):
    FACTION_MAX_ALLY = 0
    FACTION_ALLY = 1
    FACTION_WARMLY = 2
    FACTION_KINDLY = 3
    FACTION_AMIABLY = 4
    FACTION_INDIFFERENTLY = 5
    FACTION_APPREHENSIVELY = 6
    FACTION_DUBIOUSLY = 7
    FACTION_THREATENINGLY = 8
    FACTION_SCOWLS = 9
    FACTION_MAX_SCOWLS = 10


def faction_value_to_string(faction_value: FactionValue) -> str:
    """
    Converts a FactionValue enum to a string

    :param faction_value: a FactionValue enum
    :return: a string representation of the FactionValue enum
    """
    match faction_value:
        case FactionValue.FACTION_MAX_ALLY:
            return "Max Ally"
        case FactionValue.FACTION_ALLY:
            return "Ally"
        case FactionValue.FACTION_WARMLY:
            return "Warmly"
        case FactionValue.FACTION_KINDLY:
            return "Kindly"
        case FactionValue.FACTION_AMIABLY:
            return "Amiably"
        case FactionValue.FACTION_INDIFFERENTLY:
            return "Indifferently"
        case FactionValue.FACTION_APPREHENSIVELY:
            return "Apprehensively"
        case FactionValue.FACTION_DUBIOUSLY:
            return "Dubiously"
        case FactionValue.FACTION_THREATENINGLY:
            return "Threateningly"
        case FactionValue.FACTION_SCOWLS:
            return "Scowls"

    return "Unknown"


@dataclass
class NPCFactionList:
    id: int
    primary_faction: int
    assist_primary_faction: bool
    faction_id: list
    faction_value: list
    faction_npc_value: list
    faction_temp: list


@dataclass
class NPCFaction:
    faction_id: int
    value_mod: int
    npc_value: int
    temp: int


@dataclass
class Faction:
    id: int
    base: int
    name: str
    see_illusion: bool
    min_cap: int
    max_cap: int


@dataclass
class FactionMods:
    """Class to keep track of faction modifiers"""
    base_mod: int = 0
    class_mod: int = 0
    race_mod: int = 0
    deity_mod: int = 0


def calculate_faction_value(fmod: FactionMods, tmp_character_value: int) -> FactionValue:
    """
    Calculate the faction level given a set of faction modifiers and character base faction
    Values for each level were derived from EQMacEmu source code as of 8 March 2024.

    :param fmod: a FactionMods data class
    :param tmp_character_value: a character's base faction with any spell or item modifiers
    :return: the faction level as an enum
    """
    character_value: int = tmp_character_value + fmod.base_mod + fmod.class_mod + fmod.race_mod + fmod.deity_mod

    if character_value >= 2000:
        return FactionValue.FACTION_MAX_ALLY
    elif character_value >= 1100:
        return FactionValue.FACTION_ALLY
    elif 750 <= character_value <= 1099:
        return FactionValue.FACTION_WARMLY
    elif 500 <= character_value <= 749:
        return FactionValue.FACTION_KINDLY
    elif 100 <= character_value <= 499:
        return FactionValue.FACTION_AMIABLY
    elif 0 <= character_value <= 99:
        return FactionValue.FACTION_INDIFFERENTLY
    elif -100 <= character_value <= -1:
        return FactionValue.FACTION_APPREHENSIVELY
    elif -500 <= character_value <= -101:
        return FactionValue.FACTION_DUBIOUSLY
    elif -750 <= character_value <= -501:
        return FactionValue.FACTION_THREATENINGLY
    elif -1999 <= character_value <= -751:
        return FactionValue.FACTION_SCOWLS
    elif character_value <= -2000:
        return FactionValue.FACTION_MAX_SCOWLS
    else:
        return FactionValue.FACTION_INDIFFERENTLY


def get_faction_view(character_id: int, race_id: int, class_id: int, deity_id: int) -> list:
    cursor = connections['game_database'].cursor()
    cursor.execute(
        """SELECT fl.id, fl.name, fl.base, fl.min_cap, fl.max_cap, cfv.current_value
           FROM character_faction_values as cfv LEFT OUTER JOIN faction_list as fl ON fl.id  = cfv.faction_id
           WHERE cfv.id = '%s'
           ORDER BY fl.name;
        """, [character_id])
    character_faction_list = cursor.fetchall()
    final_faction = list()
    race_mod_name = ''.join(['r', str(race_id)])
    class_mod_name = ''.join(['c', str(class_id)])
    deity_mod_name = ''.join(['d', str(deity_id)])
    FactionTableRow = namedtuple("FactionTableRow", "id name base min_cap max_cap current_value")
    for faction in character_faction_list:
        faction_table_row = FactionTableRow(faction[0], faction[1], faction[2],
                                            faction[3], faction[4], faction[5])
        faction_modifiers = FactionListMod.objects.filter(faction_id=faction_table_row.id)
        fm = FactionMods()
        fm.base_mod = faction_table_row.base
        for modifier in faction_modifiers:
            if race_mod_name in modifier.mod_name:
                fm.race_mod = modifier.mod
            if class_mod_name in modifier.mod_name:
                fm.class_mod = modifier.mod
            if deity_mod_name in modifier.mod_name:
                fm.deity_mod = modifier.mod
        modifiers = fm.base_mod + fm.race_mod + fm.class_mod + fm.deity_mod
        row = faction[0], faction[1], modifiers, faction[3], faction[4], faction[5]
        if len(row) == 6:
            final_faction.append(row)

    return final_faction
