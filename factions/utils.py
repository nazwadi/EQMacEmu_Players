"""
utils.py - reusable utility functions used in faction views
"""
from django.db import connections
from collections import namedtuple
from common.faction import FactionMods
from common.models.faction import FactionListMod

def get_specific_faction_information(character_id: int,
                                     race_id: int,
                                     class_id: int,
                                     deity_id: int,
                                     faction_name: str) -> namedtuple:
    cursor = connections['game_database'].cursor()
    faction_query = """SELECT fl.id, fl.name, fl.base, fl.min_cap, fl.max_cap, cfv.current_value
           FROM character_faction_values as cfv LEFT OUTER JOIN faction_list as fl ON fl.id  = cfv.faction_id
           WHERE cfv.id = %s AND fl.name = %s"""
    cursor.execute(faction_query, [character_id, faction_name])
    result = cursor.fetchone()
    FactionTableRow = namedtuple("FactionTableRow", "id name base min_cap max_cap current_value")
    CharacterFaction = namedtuple("FactionTableRow", "id name modified_base min_cap max_cap current_value")
    faction = ()
    if result is not None:
        race_mod_name = ''.join(['r', str(race_id)])
        class_mod_name = ''.join(['c', str(class_id)])
        deity_mod_name = ''.join(['d', str(deity_id)])
        faction_table_row = FactionTableRow(*result)
        faction_modifiers = FactionListMod.objects.filter(faction_id=faction_table_row.id)
        fm = FactionMods()
        fm.base_mod = faction_table_row.base
        for modifier in faction_modifiers:
            if race_mod_name == modifier.mod_name:
                fm.race_mod = modifier.mod
            if class_mod_name == modifier.mod_name:
                fm.class_mod = modifier.mod
            if deity_mod_name == modifier.mod_name:
                fm.deity_mod = modifier.mod
        modified_base = fm.base_mod + fm.race_mod + fm.class_mod + fm.deity_mod
        faction = CharacterFaction(result[0], result[1], modified_base, result[3], result[4], result[5])
    return faction

