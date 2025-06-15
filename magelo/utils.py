"""
Utility functions for calculating character profile data

These functions are generally used by the magelo view but didn't belong in that file
"""
from enum import IntEnum
from enum import Enum
import math
from typing import Union

from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from .models import CharacterPermissions

class CasterClass(Enum):
    INTELLIGENCE = 'I'
    WISDOM = 'W'
    NONE = 'N'

def get_permissions(user, character_name, gm_level, anon_level):
    """
    Calculate viewing permissions based on stored user permissions, GM level, and anonymity level

    Args:
        user: The Django user object
        character_name: The name of the character
        gm_level: Integer representing GM level
        anon_level: Integer representing anonymity level

    Returns:
        dict: Permission states for various features
    """
    # Start with default false permissions
    base_permissions = {
        'inventory': False,
        'bags': False,
        'bank': False,
        'coin_inventory': False,
        'coin_bank': False
    }

    try:
        # Get user's stored permissions
        character_permissions = CharacterPermissions.get_or_create_permissions(character_name)

        # Update base permissions with stored permissions
        for permission in base_permissions.keys():
            base_permissions[permission] = getattr(character_permissions, permission, False)

        # If user is GM or anonymous, override permissions
        if gm_level > 0 or anon_level > 0:
            return base_permissions

        # For normal users (non-GM, non-anonymous), use their stored permissions
        return base_permissions

    except Exception as e:
        # Log the error and return base permissions if something goes wrong
        print(f"Error getting permissions for user {user}: {str(e)}")
        return base_permissions

class FlowingThoughtEffects(Enum):
    """Spell IDs for all known item-based Flowing Thought Spell Effects"""
    FLOWING_THOUGHT_I = 1298
    FLOWING_THOUGHT_II = 1299
    FLOWING_THOUGHT_III = 1300
    FLOWING_THOUGHT_IV = 1301
    FLOWING_THOUGHT_V = 1302
    FLOWING_THOUGHT_VI = 1303
    FLOWING_THOUGHT_VII = 1304
    FLOWING_THOUGHT_VIII = 1305
    FLOWING_THOUGHT_IX = 1306
    FLOWING_THOUGHT_X = 1307

    @classmethod
    def has_value(cls, value):
        return value in [e.value for e in cls]

    @classmethod
    def get_tier(cls, spell_id):
        """Convert spell ID to its tier (1-9)"""
        return {
            cls.FLOWING_THOUGHT_I.value: 1,
            cls.FLOWING_THOUGHT_II.value: 2,
            cls.FLOWING_THOUGHT_III.value: 3,
            cls.FLOWING_THOUGHT_IV.value: 4,
            cls.FLOWING_THOUGHT_V.value: 5,
            cls.FLOWING_THOUGHT_VI.value: 6,
            cls.FLOWING_THOUGHT_VII.value: 7,
            cls.FLOWING_THOUGHT_VIII.value: 8,
            cls.FLOWING_THOUGHT_IX.value: 9,
            cls.FLOWING_THOUGHT_X.value: 10,
        }.get(spell_id)


class ItemStats:
    """Helper class to track item statistics and bonuses"""

    def __init__(self):
        self.items = []
        self.total_weight = 0
        self.total_ac = 0
        self.total_hp = 0
        self.total_mana = 0
        self.stat_bonuses = {
            'str': 0, 'sta': 0, 'agi': 0, 'dex': 0,
            'int': 0, 'wis': 0, 'cha': 0,
            'fr': 0, 'cr': 0, 'mr': 0, 'dr': 0, 'pr': 0
        }
        self.str_cap = 255
        self.sta_cap = 255
        self.agi_cap = 255
        self.dex_cap = 255
        self.int_cap = 255
        self.wis_cap = 255
        self.cha_cap = 255
        self.fr_cap = 300
        self.cr_cap = 300
        self.mr_cap = 300
        self.dr_cap = 300
        self.pr_cap = 300
        self.ft_cap = 15
        self.atk_cap = 250
        self.ds = 0
        self.haste = 0
        self.haste_cap = 100
        self.regen = 0
        self.ft = 0
        self.atk = 0

    def add_item(self, item):
        """Add item and accumulate its stats"""
        self.items.append(item)
        self.total_weight += item.weight
        self.total_ac += item.ac
        self.total_hp += item.hp
        self.total_mana += item.mana

        if item.worn_effect == 998:  # Haste
            self.haste += item.worn_level + 1

        if FlowingThoughtEffects.has_value(item.worn_effect):
            self.ft += FlowingThoughtEffects.get_tier(item.worn_effect)

        # Add stat bonuses
        self.stat_bonuses['str'] += item.astr
        self.stat_bonuses['sta'] += item.asta
        self.stat_bonuses['agi'] += item.aagi
        self.stat_bonuses['dex'] += item.adex
        self.stat_bonuses['int'] += item.aint
        self.stat_bonuses['wis'] += item.awis
        self.stat_bonuses['cha'] += item.acha
        self.stat_bonuses['fr'] += item.fr
        self.stat_bonuses['cr'] += item.cr
        self.stat_bonuses['mr'] += item.mr
        self.stat_bonuses['dr'] += item.dr
        self.stat_bonuses['pr'] += item.pr



class CharacterClass(IntEnum):
    """Character class constants using IntEnum for better type safety"""
    WARRIOR = 1
    CLERIC = 2
    PALADIN = 3
    RANGER = 4
    SHADOWKNIGHT = 5
    DRUID = 6
    MONK = 7
    BARD = 8
    ROGUE = 9
    SHAMAN = 10
    NECROMANCER = 11
    WIZARD = 12
    MAGICIAN = 13
    ENCHANTER = 14
    BEASTLORD = 15
    BERSERKER = 16

class Race(IntEnum):
    """Race constants"""
    HUMAN = 1
    BARBARIAN = 2
    ERUDITE = 3
    DWARF = 8
    TROLL = 9
    HALFLING = 11
    IKSAR = 128


def level_regen(level: int, is_sitting: bool, is_resting: bool, is_feigned: bool, is_famished: bool,
                has_racial_regen_bonus: bool) -> int:
    """
    Calculates base HP Regen bonus while standing based primarily on level
    Taken from Server source at zone/client_mods.cpp

    :param level:
    :param is_sitting: True or False
    :param is_resting: True or False
    :param is_feigned: True or False
    :param is_famished: True or False
    :param has_racial_regen_bonus: True if Iksar or Troll, otherwise False
    :return: the base regen rate while standing
    """
    # Base Regen Amount is 1
    hp_regen_amount = 1

    if is_sitting:
        hp_regen_amount += 1

    if level > 50 and is_feigned:
        hp_regen_amount += 1

    # being either hungry or thirsty negates the passive regen from standing/sitting/feigning but can still benefit from level bonuses and resting
    if is_famished:
        hp_regen_amount = 0

    # additional point of regen is gained at levels 51, 56, 60, 61, 63 and 65
    if level >= 51:
        hp_regen_amount += 1
    if level >= 56:
        hp_regen_amount += 1
    if level >= 60:
        hp_regen_amount += 1
    if level >= 61:
        hp_regen_amount += 1
    if level >= 63:
        hp_regen_amount += 1
    if level >= 65:
        hp_regen_amount += 1

    # resting begins after sitting for 1 minute.
    #  1 additional point of regen is gained at levels 20 and 50
    if is_sitting and is_resting:
        if level >= 20:
            hp_regen_amount += 1
        if level >= 50:
            hp_regen_amount += 1

    # racial trait adds to then doubles regen bonuses
    if has_racial_regen_bonus:
        if level >= 51:
            hp_regen_amount += 1
        if level >= 56:
            hp_regen_amount += 1

        hp_regen_amount *= 2

    return hp_regen_amount

def calc_hp_regen_cap(character_level: int) -> int:
    """
    Calculates HP Regen Cap based on character_level
    Taken from server source at zone/client_mods.cpp

    :param character_level:
    :return:
    """
    base = 30
    if character_level > 60:
        base = character_level - 30
    return base

def calc_base_mana(caster_class: Union[str, CasterClass], intelligence: int, wisdom: int, level: int) -> int:
    """
    Calculate base mana for a character based on their class and stats.

    Args:
        caster_class: Character class ('I' for Intelligence, 'W' for Wisdom, 'N' for None)
        intelligence: Character's intelligence stat
        wisdom: Character's wisdom stat
        level: Character's level

    Returns:
        Calculated base mana value

    Raises:
        ValueError: If caster_class is invalid or stats are negative
    """
    # Input validation
    if isinstance(caster_class, CasterClass):
        class_char = caster_class.value
    else:
        class_char = caster_class

    if class_char not in ['I', 'W', 'N']:
        raise ValueError(f"Invalid caster class '{class_char}'. Must be 'I', 'W', or 'N'")

    if intelligence < 0 or wisdom < 0 or level < 0:
        raise ValueError("Stats and level must be non-negative")

    # Non-caster classes return 0 mana
    if class_char == 'N':
        return 0

    # Select the appropriate stat based on class
    primary_stat = intelligence if class_char == 'I' else wisdom

    return _calculate_mana_from_stat(primary_stat, level)

def _calculate_mana_from_stat(stat_value: int, level: int) -> int:
    """Helper function to calculate mana from a primary stat and level."""
    # Calculate mind lesser factor (penalty for very high stats)
    mind_lesser_factor = max(0, (stat_value - 199) // 2)
    mind_factor = stat_value - mind_lesser_factor

    # Different formulas based on stat threshold
    if stat_value > 100:
        # High stat formula
        return ((5 * (mind_factor + 20)) // 2) * 3 * level // 40
    else:
        # Low stat formula
        return ((5 * (mind_factor + 200)) // 2) * 3 * level // 100


def rate_limit_by_user(user_id, key_prefix, max_requests=5, time_window=60):
    cache_key = f"rate_limit:{key_prefix}:{user_id}"
    requests = cache.get(cache_key, 0)
    if requests >= max_requests:
        raise PermissionDenied("Too many requests. Please try again later.")
    cache.set(cache_key, requests + 1, time_window)

def calc_max_mana(character_class: Union[int, 'CharacterClass'],
                  intelligence: int, wisdom: int, level: int, item_mana_bonus: int = 0,
                  spell_mana_bonus: int = 0, current_mana: int = 0) -> tuple[int, int]:
    """
    Calculate maximum mana for a character and adjust current mana if needed.

    Args:
        character_class: Character's class (use CharacterClass enum values or int)
        intelligence: Character's intelligence stat
        wisdom: Character's wisdom stat
        level: Character's level
        item_mana_bonus: Bonus mana from items (default: 0)
        spell_mana_bonus: Bonus mana from spells (default: 0)
        current_mana: Character's current mana (default: 0)

    Returns:
        Tuple of (max_mana, adjusted_current_mana)

    Raises:
        ValueError: If inputs are invalid
    """
    # Update these next two lines when AA's lift the stat cap (or detect those AA's)
    intelligence = min(255, intelligence)
    wisdom = min(255, wisdom)

    # Get character class ID as integer
    if hasattr(character_class, 'value'):  # scenario 1: Enum instance passed in
        char_class_id = character_class.value
    else:  # scenario 2: raw integer passed in
        char_class_id = character_class

    # Determine caster class using the existing function
    caster_class = get_caster_class(char_class_id)

    # Calculate max mana based on caster class
    if caster_class in ['I', 'W']:
        # Special case: Hybrid classes get no mana until level 9
        # Using the actual enum values: RANGER=4, PALADIN=3, BEASTLORD=15
        if char_class_id in [3, 4, 15] and level < 9:  # PALADIN, RANGER, BEASTLORD
            max_mana = 0
        else:
            base_mana = calc_base_mana(caster_class, intelligence, wisdom, level)
            max_mana = base_mana + item_mana_bonus + spell_mana_bonus
    else:  # caster_class == 'N'
        max_mana = 0

    # Apply constraints
    max_mana = max(0, max_mana)  # Ensure non-negative
    max_mana = min(max_mana, 32767)  # Cap at 32767

    # Adjust current mana if it exceeds maximum
    adjusted_current_mana = min(current_mana, max_mana)

    return max_mana, adjusted_current_mana


def get_max_attack(item_atk: int, strength: int, offense: int) -> int:
    """
    Calculate maximum ATK value for a character.

    This function combines item attack with character stats to determine
    the total attack value using the game's formula.

    Args:
        item_atk: Base attack value from equipped items
        strength: Character's strength stat (base + items)
        offense: Character's offense skill level

    Returns:
        Total maximum attack value (floored to integer)

    Formula:
        max_attack = item_attack + ((strength + offense) * 0.9)
    """
    stat_bonus = (strength + offense) * 0.9
    total_attack = item_atk + stat_bonus
    return math.floor(total_attack)

def pr_by_race(race):
    """Calculate Poison Resistance by race"""
    if race in (Race.DWARF, Race.HALFLING):
        return 20
    return 15


def mr_by_race(race):
    """Calculate Magic Resistance by race"""
    if race in (Race.ERUDITE, Race.DWARF):
        return 30
    return 25


def dr_by_race(race):
    """Calculate Disease Resistance by race"""
    if race == Race.ERUDITE:
        return 10
    elif race == Race.HALFLING:
        return 20
    return 15


def fr_by_race(race):
    """Calculate Fire Resistance by race"""
    if race == Race.TROLL:
        return 5
    elif race == Race.IKSAR:
        return 30
    return 25


def cr_by_race(race):
    """Calculate Cold Resistance by race"""
    if race == Race.BARBARIAN:
        return 35
    elif race == Race.IKSAR:
        return 15
    return 25


def pr_by_class(char_class, char_level):
    """Calculate Poison Resistance by class and level"""
    if char_class == CharacterClass.SHADOWKNIGHT:
        return (char_level - 49) + 4 if char_level >= 50 else 4
    elif char_class == CharacterClass.ROGUE:
        return (char_level - 49) + 8 if char_level >= 50 else 8
    return 0


def mr_by_class(char_class, char_level):
    """Calculate Magic Resistance by class and level"""
    if char_class == CharacterClass.WARRIOR:
        return char_level // 2
    return 0


def dr_by_class(char_class, char_level):
    """Calculate Disease Resistance by class and level"""
    if char_class == CharacterClass.PALADIN:
        return (char_level - 49) + 8 if char_level >= 50 else 8
    elif char_class in (CharacterClass.SHADOWKNIGHT, CharacterClass.BEASTLORD):
        return (char_level - 49) + 4 if char_level >= 50 else 4
    return 0


def fr_by_class(char_class, char_level):
    """Calculate Fire Resistance by class and level"""
    if char_class == CharacterClass.RANGER:
        return (char_level - 49) + 4 if char_level >= 50 else 4
    elif char_class == CharacterClass.MONK:
        return (char_level - 49) + 8 if char_level >= 50 else 8
    return 0


def cr_by_class(char_class, char_level):
    """Calculate Cold Resistance by class and level"""
    if char_class in (CharacterClass.RANGER, CharacterClass.BEASTLORD):
        return (char_level - 49) + 4 if char_level >= 50 else 4
    return 0

def get_max_ac(agility: int, level: int, defense: int,
               char_class: Union[int, CharacterClass],
               iac: int, race: Union[int, Race]) -> int:
    """
    Calculate maximum AC for a character.

    Args:
        agility: Character's agility stat
        level: Character level
        defense: Defense skill value
        char_class: Character class (int or CharacterClass enum)
        iac: Item AC value
        race: Character race (int or Race enum)

    Returns:
        Maximum AC value (floored)
    """
    # Calculate avoidance component
    avoidance = max(0, int(acmod(agility, level) + (defense * 16 / 9)))

    # Calculate mitigation based on class
    caster_classes = {CharacterClass.WIZARD, CharacterClass.MAGICIAN,
                      CharacterClass.NECROMANCER, CharacterClass.ENCHANTER}

    if char_class in caster_classes:
        mitigation = defense / 4 + (iac + 1) - 4
    else:
        mitigation = defense / 3 + (iac * 4 / 3)
        if char_class == CharacterClass.MONK:
            mitigation += level * 1.3  # More readable than 13/10

    # Calculate natural AC
    natural_ac = (avoidance + mitigation) * 1000 / 847

    # Apply racial bonuses
    if race == Race.IKSAR:
        natural_ac += 12
        # Iksar level bonus (capped at 25 levels above 10)
        iksar_bonus_levels = min(25, max(0, level - 10))
        natural_ac += iksar_bonus_levels * 1.2  # More readable than 12/10

    return math.floor(natural_ac)

def _calculate_medium_agility_modifier(agility: int, level: int) -> int:
    """Helper function for agility 75-137 range."""
    # Define level-based modifier tables
    level_modifiers = {
        (75, 75): [9, 23, 33, 39],
        (76, 79): [10, 23, 33, 40],
        (80, 80): [11, 24, 34, 41],
        (81, 85): [12, 25, 35, 42],
        (86, 90): [12, 26, 36, 42],
        (91, 95): [13, 26, 36, 43],
        (96, 99): [14, 27, 37, 44],
        (100, 100): [None, 28, 38, 45],  # Special case for level <= 6
        (101, 105): [15, 29, 39, 45],
        (106, 110): [15, 29, 39, 46],
        (111, 115): [15, 30, 40, 47],
        (116, 119): [15, 31, 41, 47],
        (120, 120): [15, 32, 42, 48],
        (121, 125): [15, 32, 42, 49],
        (126, 135): [15, 32, 42, 50],
        (136, 137): [15, 32, 42, 51],
    }

    # Determine level bracket (0: <=6, 1: <=19, 2: <=39, 3: >=40)
    level_bracket = 0 if level <= 6 else (1 if level <= 19 else (2 if level <= 39 else 3))

    for (min_agi, max_agi), modifiers in level_modifiers.items():
        if min_agi <= agility <= max_agi:
            if agility == 100 and level <= 6:
                return 15  # Special case
            elif agility == 100 and level < 7:
                return 15
            return modifiers[level_bracket]

    return 0

def _calculate_high_agility_modifier(agility: int, level: int) -> int:
    """Helper function for agility 138-300 range."""
    # Define agility breakpoints and their corresponding modifiers
    agility_breakpoints = [
        (139, [21, 34, 44, 51]),
        (140, [22, 35, 45, 52]),
        (145, [23, 36, 46, 53]),
        (150, [23, 37, 47, 53]),
        (155, [24, 37, 47, 54]),
        (159, [25, 38, 48, 55]),
        (160, [26, 39, 49, 56]),
        (165, [26, 40, 50, 56]),
        (170, [27, 40, 50, 57]),
        (175, [28, 41, 51, 58]),
        (179, [28, 42, 52, 58]),
        (180, [29, 43, 53, 59]),
        (185, [30, 43, 53, 60]),
        (190, [31, 44, 54, 61]),
        (195, [31, 45, 55, 61]),
        (199, [32, 45, 55, 62]),
        (219, [33, 46, 56, 63]),
        (239, [34, 47, 57, 64]),
        (300, [35, 48, 58, 65]),
    ]

    # Determine level bracket (0: <=6, 1: <=19, 2: <=39, 3: >=40)
    level_bracket = 0 if level <= 6 else (1 if level <= 19 else (2 if level <= 39 else 3))

    for max_agi, modifiers in agility_breakpoints:
        if agility <= max_agi:
            return modifiers[level_bracket]

    return 0

def acmod(agility: int, level: int) -> float:
    """
    Calculate agility modifier for AC based on agility and level.

    This function implements complex game logic for calculating AC modifiers
    based on character agility and level ranges.

    Args:
        agility: Character's agility stat
        level: Character level

    Returns:
        Agility modifier value for AC calculation
    """
    if agility < 1 or level < 1:
        return 0

    # Define lookup tables for cleaner code
    low_agility_map = {
        1: -24, 2: -23, 3: -23, 4: -22, 5: -21, 6: -21,
        7: -20, 8: -20, 9: -19, 10: -18, 11: -18, 12: -17,
        13: -16, 14: -16, 15: -15, 16: -15, 17: -14, 18: -13,
        19: -13, 20: -12, 21: -11, 22: -11, 23: -10, 24: -10,
        25: -9, 26: -8, 27: -8, 28: -7, 29: -6, 30: -6,
        31: -5, 32: -5, 33: -4, 34: -3, 35: -3, 36: -2,
        37: -1, 38: -1
    }

    # Handle low agility values (1-74)
    if agility <= 74:
        if agility in low_agility_map:
            return low_agility_map[agility]
        elif agility <= 65:
            return 0  # 39-65
        elif agility <= 70:
            return 1  # 66-70
        else:
            return 5  # 71-74

    # Handle medium agility values (75-137)
    elif agility <= 137:
        return _calculate_medium_agility_modifier(agility, level)

    # Handle high agility values (138-300)
    elif agility <= 300:
        return _calculate_high_agility_modifier(agility, level)

    # Handle very high agility (300+)
    else:
        return 65 + ((agility - 300) / 21)

def get_caster_class(class_id):
    """
    Determine caster type based on class ID.
    Function copied/converted from EQEMU sourcecode May 2, 2009
    """
    # Class constants
    _ = 1 # warrior
    cleric = 2
    paladin = 3
    ranger = 4
    shadowknight = 5
    druid = 6
    _ = 7 # monk
    bard = 8
    _ = 9 # rogue
    shaman = 10
    necromancer = 11
    wizard = 12
    magician = 13
    enchanter = 14
    beastlord = 15
    _ = 16 # berserker

    caster_types = {
        # Wisdom-based casters
        cleric: 'W',
        paladin: 'W',
        ranger: 'W',
        druid: 'W',
        shaman: 'W',
        beastlord: 'W',

        # Intelligence-based casters
        shadowknight: 'I',
        bard: 'I',
        necromancer: 'I',
        wizard: 'I',
        magician: 'I',
        enchanter: 'I',
    }

    return caster_types.get(class_id, 'N')  # Default to 'N' for non-casters

def get_max_hp(level: int, character_class: int, stamina: int, item_hp_bonus: int,
               stat_cap: int = 255) -> int:
    """
    Calculate maximum hit points for a character.

    This function will need to be modified in Luclin for the ND and PE AAs.
    The stat_cap parameter should be removed when the 255 stat cap is lifted.

    Args:
        level: Character's level
        character_class: Character's class ID
        stamina: Character's stamina stat
        item_hp_bonus: HP bonus from items
        stat_cap: Maximum allowed stamina value (default: 255)

    Returns:
        Total maximum hit points

    Raises:
        ValueError: If any parameter is negative
    """
    # Input validation
    if level < 0 or character_class < 0 or stamina < 0 or item_hp_bonus < 0:
        raise ValueError("All parameters must be non-negative")

    # Apply stat cap (will be removed in future when 255 cap is lifted)
    capped_stamina = min(stat_cap, stamina)

    # Calculate base HP and add item bonuses
    base_hp = get_hp_base(level, character_class, capped_stamina)
    total_hp = int(base_hp) + int(item_hp_bonus)

    return total_hp


def get_hp_base(level: int, character_class: int, stamina: int) -> float:
    """
    Calculate base hit points for a character.

    This function will need to be modified in Luclin for the ND and PE AAs.

    Args:
        level: Character's level
        character_class: Character's class ID
        stamina: Character's stamina stat

    Returns:
        Base hit points as a float
    """
    # Get level multiplier for the class
    lm = float(get_lm(character_class, level))

    # Calculate post-255 stamina penalty
    post_255_sta = max(0, (stamina - 255))

    # Calculate stamina gain with post-255 penalty
    sta_gain = (stamina - round(post_255_sta / 2)) * 10 // 3

    # Calculate HP components
    hp_from_level = level * lm
    hp_from_sta = level * lm * sta_gain / 1000

    # Base HP calculation
    base_hp = 5 + hp_from_level + hp_from_sta

    return base_hp

def get_lm(character_class: int, level: int) -> float:
    """
    Get the level multiplier for a character class.

    Args:
        character_class: Character's class ID
        level: Character's level

    Returns:
        Level multiplier as a float
    """
    class_name = get_class_name(character_class)

    # Level multiplier configuration: class_names -> [(min_level, multiplier), ...]
    # Ordered from the highest level requirement to lowest
    level_multipliers = {
        frozenset(['Monk', 'Rogue', 'Beastlord', 'Bard']): [
            (58, 20.0), (51, 19.0), (0, 18.0)
        ],
        frozenset(['Cleric', 'Druid', 'Shaman']): [
            (0, 15.0)
        ],
        frozenset(['Magician', 'Necromancer', 'Enchanter', 'Wizard']): [
            (0, 12.0)
        ],
        frozenset(['Ranger']): [
            (58, 21.0), (0, 20.0)
        ],
        frozenset(['Shadow Knight', 'Shadowknight', 'Paladin']): [
            (60, 26.0), (56, 25.0), (51, 24.0), (45, 23.0), (35, 22.0), (0, 21.0)
        ],
        frozenset(['Warrior']): [
            (60, 30.0), (57, 29.0), (53, 28.0), (40, 27.0), (30, 25.0), (20, 23.0), (0, 22.0)
        ]
    }

    # Find the class group and return the appropriate multiplier
    for class_group, multipliers in level_multipliers.items():
        if class_name in class_group:
            for min_level, multiplier in multipliers:
                if level >= min_level:
                    return multiplier

    # Default case if class not found
    return 1.0


def get_class_name(character_class: int) -> str:
    """
    Get the class name from a character class ID.

    Args:
        character_class: Character's class ID

    Returns:
        Class name as a string, or 'Unknown' if class ID is invalid
    """
    try:
        return CharacterClass(character_class).name.title()
    except ValueError:
        return 'Unknown'



