import json

from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist
from django.db import connections

from common.faction import FactionMods

from common.models.characters import CharacterSkills
from common.models.characters import CharacterSpells
from common.models.faction import FactionListMod
from common.models.guilds import Guilds
from common.models.guilds import GuildMembers


def get_character_inventory(character_id: int) -> tuple:
    cursor = connections['game_database'].cursor()
    cursor.execute("""SELECT ci.itemid, i.name, i.icon, ci.slotid, ci.charges, i.maxcharges, i.stackable
                      FROM character_inventory ci LEFT OUTER JOIN items i ON ci.itemid = i.id
                      WHERE ci.id = %s""", [character_id])
    character_inventory = cursor.fetchall()
    return character_inventory


def get_character_keyring(character_id: int) -> tuple:
    cursor = connections['game_database'].cursor()
    cursor.execute(
        """SELECT ck.item_id, i.Name 
           FROM character_keyring as ck LEFT OUTER JOIN items as i ON ck.item_id = i.id 
           WHERE ck.id  = '%s' 
           ORDER BY i.Name;""", [character_id])
    character_keyring = cursor.fetchall()
    return character_keyring


def get_faction_information(character_id: int, race_id: int, class_id: int, deity_id: int) -> list:
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


def get_guild_information(character_id: int):
    guild_members = GuildMembers.objects.filter(char_id=character_id).first()
    if guild_members is not None:
        guild_id = guild_members.guild_id
        guild = Guilds.objects.filter(id=int(guild_id.id)).first()
        guild_members = GuildMembers.objects.filter(guild_id=guild.id)
    else:
        guild = None

    return guild, guild_members


def get_skill_information(character_id: int):
    character_skills_unfiltered = CharacterSkills.objects.filter(id=character_id)
    character_magic_songs = []
    character_skills = []
    for skill in character_skills_unfiltered:
        if skill.skill_id in [4, 5, 12, 13, 14, 18, 24, 31, 41, 43, 44, 45, 46, 47, 49, 54, 70]:
            character_magic_songs.append(skill)
        else:
            character_skills.append(skill)
    return character_magic_songs, character_skills


def get_spell_information(character_id: int, class_id: int):
    scribed_spells = CharacterSpells.objects.filter(id=character_id)
    character_spells = list()
    for spell in scribed_spells:
        try:
            character_spells.append(spell.spell_id.id)
        except ObjectDoesNotExist:
            continue
    filename = f'static/spell_data/{class_id}.json'
    with open(filename, 'r') as json_file:
        spell_list = json.load(json_file)
    return character_spells, spell_list
