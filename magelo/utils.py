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
    _ = 1  # warrior
    cleric = 2
    paladin = 3
    ranger = 4
    shadowknight = 5
    druid = 6
    _ = 7  # monk
    bard = 8
    _ = 9  # rogue
    shaman = 10
    necromancer = 11
    wizard = 12
    magician = 13
    enchanter = 14
    beastlord = 15
    _ = 16  # berserker

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
    TODO: See Server source zone/client_mods.cpp

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
    total_hp = math.floor(base_hp) + math.floor(item_hp_bonus)

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
    level_multiplier = float(get_lm(character_class, level))

    # Calculate post-255 stamina penalty
    post_255_sta = max(0, (stamina - 255))

    # Calculate stamina gain with post-255 penalty
    sta_gain = math.floor((stamina - round(post_255_sta / 2)) * 10 / 3)

    # Calculate HP components
    hp_from_level = level * level_multiplier
    hp_from_sta = level * level_multiplier * sta_gain / 1000

    # Base HP calculation
    base_hp = 5 + hp_from_level + hp_from_sta

    return base_hp


def get_lm(character_class: int, level: int) -> float:
    """
    Get the level multiplier for a character class.
    """
    class_name = get_class_name(character_class)

    # Level multiplier configuration matching PHP exactly
    if class_name in ['Monk', 'Rogue', 'Beastlord', 'Bard']:
        if level > 57: return 20.0
        if level > 50: return 19.0
        return 18.0

    if class_name in ['Cleric', 'Druid', 'Shaman']:
        return 15.0

    if class_name in ['Magician', 'Necromancer', 'Enchanter', 'Wizard']:
        return 12.0

    if class_name == 'Ranger':
        if level > 57: return 21.0
        return 20.0

    if class_name in ['Shadow Knight', 'Shadowknight', 'Paladin']:
        if level > 59: return 26.0
        if level > 55: return 25.0
        if level > 50: return 24.0
        if level > 44: return 23.0
        if level > 34: return 22.0
        return 21.0

    if class_name == 'Warrior':
        if level > 59: return 30.0
        if level > 56: return 29.0
        if level > 52: return 28.0
        if level > 39: return 27.0
        if level > 29: return 25.0
        if level > 19: return 23.0
        return 22.0

    return 1.0  # Default for unknown classes


def get_class_name(character_class: int) -> str:
    """Get the class name from a character class ID, matching PHP exactly."""
    class_names = {
        1: "Warrior",
        2: "Cleric",
        3: "Paladin",
        4: "Ranger",
        5: "Shadow Knight",  # Note: with space to match PHP
        6: "Druid",
        7: "Monk",
        8: "Bard",
        9: "Rogue",
        10: "Shaman",
        11: "Necromancer",
        12: "Wizard",
        13: "Magician",
        14: "Enchanter",
        15: "Beastlord",
        16: "Berserker"
    }
    return class_names.get(character_class, "Unknown Class")


from dataclasses import dataclass


@dataclass
class Ability:
    name: str
    description: str


def get_aa_description_by_name(aa_name: str):
    aa_descriptions = {
        "First Aid": "This ability increases the maximum that you can bind wound by 10 percent for each ability level.",
        "Innate Agility": "This ability raises your base Agility by 2 points for each ability level.",
        "Innate Charisma": "This ability raises your base Charisma by 2 points for each ability level.",
        "Innate Cold Protection": "This ability raises your base Save Vs Cold by 2 points for each ability level.",
        "Innate Dexterity": "This ability raises your base Dexterity by 2 points for each ability level.",
        "Innate Disease Protection": "This ability raises your base Save Vs Disease by 2 points for each ability level.",
        "Innate Fire Protection": "This ability raises your base Save Vs Fire by 2 points for each ability level.",
        "Innate Intelligence": "This ability raises your base Intelligence by 2 points for each ability level.",
        "Innate Lung Capacity": "This ability increases the amount of air you have by 10, 25, and 50 percent.",
        "Innate Magic Protection": "This ability raises your base Save Vs Magic by 2 points for each ability level.",
        "Innate Metabolism": "This ability decreases your food consumption by 10, 25 and 50 percent.",
        "Innate Poison Protection": "This ability raises your base Save Vs Poison by 2 points for each ability level.",
        "Innate Regeneration": "This ability raises your regeneration ability by 1 point per ability level.",
        "Innate Run Speed": "This ability will slightly modify your base run speed. This modification does NOT stack with movement rate spell effects.",
        "Innate Stamina": "This ability raises your base Stamina by 2 points for each ability level.",
        "Innate Strength": "This ability raises your base Strength by 2 points for each ability level.",
        "Innate Wisdom": "This ability raises your base Wisdom by 2 points for each ability level.",
        "New Tanaan Crafting Mastery": "Training with the sages and merchants of New Tanaan gives adventurers the chance to hone their crafting skills. For each rank of this ability that you purchase, you are able to raise an additional trade skill past its Specialization level (200). (This ability applies to Baking, Blacksmithing, Brewing, Fletching, Jewelcraft, Pottery, and Tailoring.)",
        "Channeling Focus": "This ability reduces the chance of your spell casts being interrupted. The ability levels reduce your interrupts by 5, 10, and 15 percent.",
        "Combat Agility": "This ability increases your melee damage avoidance by 2, 5 and 10 percent.",
        "Combat Fury": "This ability increases your chance to land a critical hit. Non-Warriors will nearly match the original critical hit abilities of Warriors, while Warriors will remain significantly ahead of other classes.",
        "Combat Stability": "This ability increases melee damage mitigation by 2, 5, and 10 percent.",
        "Fear Resistance": "This ability grants you a resistance bonus to fear type spells of 5, 10, and 25 percent. It also increases the chance of breaking fear earlier.",
        "Finishing Blow": "This ability gives you a chance to finish off an NPC that is below 10 percent health and fleeing with a single blow. The first level works on NPCs below 50, the second on NPCs below 52, and the third on NPCs below 54. (Non-Warriors must first train one level of Combat Fury to use this ability.)",
        "Healing Adept": "This ability increases the maximum effectiveness of your healing spells by 2, 5, and 10 percent.",
        "Healing Gift": "This ability grants you a chance to score an exceptional heal at 3, 6, and 10 percent. An exceptional heal doubles the healing value of the spell.",
        "Mental Clarity": "This ability increases your natural mana regeneration by 1 point per ability level.",
        "Natural Durability": "This ability increases your maximum hitpoints by 2, 5, and 10 percent. (The percentages are based off of your base hitpoints, which include stamina and stamina effects.)",
        "Natural Healing": "This ability raises your natural regeneration by one point per ability level.",
        "Spell Casting Deftness": "This ability reduces the casting time of beneficial spells that have a duration longer than instant and a cast time greater than four seconds. The ability levels reduce these casting times by 5, 15, and 25 percent.",
        "Spell Casting Expertise": "This ability makes it impossible for you to fizzle a spell. The first level affects all spells below level 20. The second, on all spells below level 35. The third, on all spells below level 52.",
        "Spell Casting Fury": "This ability gives you a chance to land critical hits with your direct damage spells. The ability levels increase your chance to score a critical by 2, 4, and 7 percent.",
        "Spell Casting Mastery": "This ability gives you an increased chance of making your specialization checks. It also reduces your chance to fizzle and increases the chance to lower the mana cost for the spell by 5, 15, and 30 percent.",
        "Spell Casting Reinforcement": "This ability increases the duration of beneficial spells that you cast by 5, 15, and 30 percent.",
        "Spell Casting Subtlety": "After training in this ability, NPCs will notice your magical activities 5, 10, and 20 percent less.",
        "Acrobatics": "This ability will reduce the damage that you take from falling.",
        "Act of Valor": "This noble ability will allow you to transfer all of your hit points to a target player, killing you in the process.",
        "Advanced Trap Negotiation": "This ability will reduce the reuse time on your sense and disarm trap skills.",
        "Alchemy Mastery": "This ability reduces your chances of failing alchemy combinations by 10, 25, and 50 percent.",
        "Ambidexterity": "This ability increases your chance to use dual wield successfully.",
        "Archery Mastery": "This ability increases your archery damage 30, 60, and 100 percent.",
        "Area Taunt": "This ability will allow you to taunt everything in a small radius.",
        "Bandage Wound": "This ability will give you increased healing ability per bandage by 10, 25, and 50 percent.",
        "Bestow Divine Aura": "This ability gives you the ability to cast a Divine Aura spell on a Player target, temporarily rendering the target invulnerable.",
        "Body and Mind Rejuvenation": "This ability will give you one additional point of mana and hit point regeneration.",
        "Call to Corpse": "This ability allows you to cast a no component summon corpse spell.",
        "Cannibalization": "This ability will give the caster a new, massive Cannibalize spell.",
        "Celestial Regeneration": "This ability gives you the ability to cast a large heal over time spell at no mana cost.",
        "Chaotic Stab": "This ability will allow you to do minimal backstab damage on your backstab attempt, even if you are not positioned behind the monster.",
        "Critical Mend": "This ability gives you a chance to perform a superior mend 5, 10, and 25 percent of the time.",
        "Dead Mesmerization": "This ability allows you to cast an AE low resist mesmerization spell effective against the undead.",
        "Dire Charm": "This ability gives you the chance to permanently charm an NPC. (Enchanters: All. Druids: Animals only. Necromancers: Undead only.)",
        "Divine Resurrection": "This ability allows you to provide a resurrection that restores 100 percent experience, all hit points and mana, and causes no adverse resurrection effects.",
        "Divine Stun": "Training in this ability gives you a new, fast-casting spell that has the chance to interrupt Level 68 or lower NPCs. Normal resist rules apply.",
        "Double Riposte": "This ability will give you an increased chance to execute a double riposte 15, 35, and 50 percent of the time.",
        "Dragon Punch": "This ability augments Dragon Punch for human monks and Tail Rake for iksars with the chance to automatically perform a Knockback.",
        "Elemental Form: Air": "This ability will allow you to turn into an air elemental, gaining many of the innate benefits of the form, as well as some of the penalties.",
        "Elemental Form: Earth": "This ability will allow you to turn into an earth elemental, gaining many of the innate benefits of the form, as well as some of the penalties.",
        "Elemental Form: Fire": "This ability will allow you to turn into a fire elemental, gaining many of the innate benefits of the form, as well as some of the penalties.",
        "Elemental Form: Water": "This ability will allow you to turn into a water elemental, gaining many of the innate benefits of the form, as well as some of the penalties.",
        "Elemental Pact": "This ability will prevent components used in the summoning of pets from being expended.",
        "Endless Quiver": "This ability provides you a never-ending supply of arrows.",
        "Enhanced Root": "This ability reduces the chance that a rooted NPC will be freed by your damage spells by 50 percent.",
        "Escape": "This ability will cause all NPCs to forget about you. If you are out of immediate combat, this ability will also make you invisible similar to your hiding ability.",
        "Exodus": "This ability gives you the ability to cast an extremely fast-casting, no mana cost evacuation or succor spell.",
        "Extended Notes": "This ability will increased your song ranges by 10, 15, and 25 percent.",
        "Fearless": "This ability will make you permanently immune to fear spells.",
        "Fearstorm": "Allows you to cast an AE low resist fear spell.",
        "Flesh to Bone": "This ability allows you to turn any meat or body part item into bone chips. You must hold the item or stack on your cursor. *Warning* This ability will use magical or no trade items if they are held on the cursor.",
        "Flurry": "This ability will allow you to perform up to 2 additional attacks from your primary hand.",
        "Frenzied Burnout": "This ability allows you to cast a buff on your pet that will cause it to go berserk, doing increased damage.",
        "Frenzy of Spirit": "This ability gives Beastlords the power to send themselves into an animalistic frenzy, bent only on slaughter, for a brief period of time.",
        "Gather Mana": "This ability allows you to recover up to 10,000 points of mana nearly instantly.",
        "Hobble of Spirits": "Once you train this ability, you may imbue your pet with an attack that is reputed to slow an enemys walking.",
        "Holy Steed": "This ability provides you with the power to call the ultimate holy steed to your side.",
        "Improved Familiar": "This ability will summon an improved familiar that is an upgrade from the greater familiar. This improved familiar is higher in level, has more hitpoints, and is very resistant to all spells.",
        "Improved Harm Touch": "This ability gives you a low-resist Harm Touch. Using this ability also uses your existing Harm Touch timer.",
        "Improved Lay on Hands": "This ability will turn your Lay of Hands into a complete heal.",
        "Improved Reclaim Energy": "This ability will increase the amount of mana returned to you when reclaiming your pet.",
        "Innate Camouflage": "This ability allows you to become invisible, nearly at will, without the need to memorize a spell.",
        "Innate Invis to Undead": "This ability allows you to become invisible to the undead, nearly at will, without the need to memorize a spell.",
        "Instrument Mastery": "This ability allows for improved use of all instrument types.",
        "Jam Fest": "This ability allows you to sing your songs at a higher apparent level. Note: This does not allow you to sing songs that are actually higher than your level.",
        "Jewelcraft Mastery": "This ability reduces your chance of failing jewelcraft combinations by 10, 25, and 50 percent.",
        "Leech Touch": "This ability gives you a life tap harm touch. Using this ability also uses your existing Harm Touch timer.",
        "Lifeburn": "This ability allows you to cast a no-resist direct damage spell equal to that of your current hitpoints. The effect drains your life and provides a life bond effect that does 250 damage per tick, for 6 ticks.",
        "Mana Burn": "This ability allows you to do non-resistable damage in an amount based off of your current mana. This is calculated as a random 50-100% of the current mana pool (gear and buffs) is added to the current mana pool number. A debuff is left on the mob for one minute that blocks other manaburns. Cap is 9492.",
        "Mass Group Buff": "This ability turns the next group buff that you cast into a beneficial area effect spell, hitting everyone within its radius, at the cost of doubling the spells mana usage.",
        "Mend Companion": "This ability allows you to cast a Lay of Hands type spell on your pet.",
        "Nexus Gate": "This ability gives you an instant-cast self gate spell to the Nexus.",
        "Paragon of Spirit": "This ability allows the Beastlord to share some of his natural attunement with his party in the form of health and mana.",
        "Permanent Illusion": "This ability allows you to zone without losing your current illusion.",
        "Pet Discipline": "This ability will allow you to give your pet a hold command until explicitly told to attack. Usage: /pet hold.",
        "Physical Enhancement": "This ability will give you additional improvements in your Natural Durability, Avoidance Boost, and Mitigation Boost.",
        "Poison Mastery": "This ability reduces your chance of failing on a poison combination by 10, 25, and 50 percent. It also reduces the time to apply poison by 2.5 seconds per ability level. Once one point is applied to this ability, you will never again fail in poison application.",
        "Purge Poison": "This ability will remove all poisons from your body.",
        "Purify Body": "This ability removes all negative effects from your body except for fear, charm, and resurrection effects.",
        "Purify Soul": "This ability allows you to cast a spell that cures most ailments.",
        "Quick Buff": "This ability reduces the casting time of many beneficial spells that have a duration by 10, 25, and 50 percent.",
        "Quick Damage": "This ability reduces the casting time on your damage spells that have a casting time greater than four seconds by 2, 5 and 10 percent.",
        "Quick Evacuation": "This ability reduces the casting time on your evacuation and succor spells by 10, 25, and 50 percent.",
        "Quick Summoning": "This ability reduces the casting time of your summoning spells by 10, 25, and 50 percent. This includes CotH.",
        "Rabid Bear": "This ability turns you into a Rabid Bear, boosting all of your offensive capabilities.",
        "Rampage": "This ability will allow you to strike everything in a small radius.",
        "Rapid Feign": "This ability reduces your reuse time on feign death by 10, 25, and 50 percent.",
        "Return Kick": "This ability gives you the chance to automatically perform a bonus flying kick on ripostes 25, 35, and 50 percent of the time.",
        "Scribble Notes": "This ability will reduce the amount of time that it takes you to memorize a song.",
        "Singing Mastery": "This ability allows for specialization and improved use of your voice.",
        "Slay Undead": "This ability will cause your criticals to inflict greatly improved damage versus the undead.",
        "Soul Abrasion": "This ability gives you increased damage off of the lifetap procs that result from your self buffs.",
        "Spell Casting Fury Mastery": "This ability gives you an increased chance to score a critical hit with your direct damage spells.",
        "Spell Casting Reinforcement Mastery": "This ability increases the duration of beneficial buffs that you cast by an additional 20 percent.",
        "Strong Root": "This ability will grant you the ability to cast an extremely low resistance Root-type spell.",
        "Turn Summoned": "This ability infuses a summoned NPC with elemental energy, causing it to continually take damage for the next 30 seconds. Each additional level of this ability increases the damage done. Occasionally a summoned NPC will react violently to the infusion of energy, potentially destroying it outright.",
        "Turn Undead": "This ability infuses an undead NPC with holy energy, causing it to continually take damage for the next 30 seconds. Each additional level of this ability increases the damage done. Occasionally an undead NPC will react violently to the infusion of holy energy, potentially destroying it outright.",
        "Two Hand Bash": "This ability will allow you to use your Bash skill while wielding any 2-handed weapon.",
        "Unholy Steed": "This ability provides you with the power to call the ultimate unholy steed to your side.",
        "Warcry": "This ability will allow you to make your entire group immune to fear for 10 seconds per level of the ability.",
        "Advanced Innate Agility": "This ability raises your innate Agility by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Advanced Innate Charisma": "This ability raises your innate Charisma by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Advanced Innate Dexterity": "This ability raises your innate Dexterity by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Advanced Innate Intelligence": "This ability raises your innate Intelligence by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Advanced Innate Stamina": "This ability raises your innate Stamina by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Advanced Innate Strength": "This ability raises your innate Strength by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Advanced Innate Wisdom": "This ability raises your innate Wisdom by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Bertoxxulous' Gift": "This ability raises your base resistance to disease-based spells by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Blessing of E'ci": "This ability raises your base resistance to cold-based spells by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Innate Enlightenment": "Those who have meditated on the Plane of Tranquility find themselves able to expand their capacity of both Insight and Intellect. Each rank of this ability raises the maximum that you may raise your Intelligence and Wisdom by ten points. You may train in this ability once each level, beginning at level 61.",
        "Marr's Protection": "This ability raises your base resistance to magic-based spells by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Planar Durability": "The planes demand a certain hardiness of those who adventure within. Each rank of this ability adds an additional 1.5% to your maximum hit points. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Planar Power": "This ability raises the maximum that your statistics can be raised to, with items or spells, by 5 points per rank. You may train in this ability once each level, beginning at level 61.",
        "Shroud of The Faceless": "This ability raises your base resistance to poison-based spells by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Warding of Solusek": "This ability raises your base resistance to fire-based spells by two points per rank. You may train in this ability twice each level, beginning at level 61.",
        "Advanced Healing Adept": "This ability increases the maximum effectiveness of your healing spells by three percent per rank. You may train in this ability once each level, upon reaching levels 62, 63, and 64.",
        "Advanced Healing Gift": "This ability increases your chance to score an exceptional heal by two percent per rank. An exceptional heal doubles the healing value of the spell. You may train in this ability once each level, upon reaching levels 62, 63, and 64.",
        "Allegiant Familiar": "This ability will cause your existing Improved Familiar to summon an even more powerful companion. This familiar provides even greater benefits to its owner than its predecessor.",
        "Animation Empathy": "Progressive ranks of this ability grant you finer control over your animations. At its initial level, you are allowed to give your animations Guard and Follow commands. At the second rank, Attack and Go Away commands. At the final rank, back off, Taunt, and Sit commands. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Ayonae's Tutelage": "This ability allows for further improvements in the use of all instrument and singing types. The three ranks of this ability may be trained once each level for levels 63 and above.",
        "Bestial Frenzy": "This ability grants you a chance of performing a double attack in any given combat round. You may train in this ability once each level after reaching level 61.",
        "Boastful Bellow": "This ability allows you to bellow with a force that causes physical harm to your enemies as well as potentially interfering with their spell casting.",
        "Call of Xuzl": "This ability calls a number of swords of Xuzl into existence directed at a target. The swords attack the target until they dissipate 45 seconds later.",
        "Celestial Renewal": "This ability grants improvements to your existing Celestial Regeneration. You may train in the two ranks of this ability at or after levels 63 and 64.",
        "Consumption of the Soul": "The most advanced Shadow Knights can further enhance their Leech Touch ability. This ability adds 200 additional damage and healing to Leech Touch, per rank. You gain the ability to train an additional rank at levels 61, 63, and 65. The ability caps at 1500 hp.",
        "Coup de Grace": "This ability gives you a chance to immediately slay an NPC that is below ten percent health and fleeing with a single, well placed strike. The first level works on NPCs below level 55, the second on NPCs below 57, and the third on NPCs below 59. You may train in this ability once each level, upon reaching levels 62, 63, and 64.",
        "Divine Arbitration": "Using this ability balances the health of your group such that all group members end up with the same amount of damage taken. The first rank does so at a 20 percent penalty to the average, the second rank does so at a 10 percent penalty, and the final rank does so at no penalty. You may train the ranks of this ability at or after levels 61, 63, and 65.",
        "Eldritch Rune": "This ability provides Enchanters with an additional line of defense in the form of an added self-only rune. Each rank of this ability provides a stronger rune than the previous. You may train the ranks of this ability at or after levels 61, 63, and 65.",
        "Entrap": "This ability provides you an additional means of entrapping, or more specifically, ensnaring an opponent.",
        "Fading Memories": "This ability will cause all NPCs to forget about you. If you are out of immediate combat, this ability will also make you invisible. This ability is usable any time that you have 900 mana.",
        "Feigned Minion": "This ability allows you to instruct your pet to feign death via the /pet feign command. Three ranks of this skill are available, causing your pet to succeed 25%, 50%, and 75% of the time, respectively. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Ferocity": "This ability grants you an increased chance of performing a double attack in any given combat round. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Feverent Blessing": "This ability decreases the amount of time required between uses of Lay Hands by twelve minutes per rank. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Flash of Steel": "This ability further increases your chance of double riposting your opponent each time you score a successful riposte by ten percent per rank. You may train in this ability once each level, upon reaching levels 62, 63, and 64.",
        "Fleet of Foot": "This ability allows Bards to run at previously unheard of speeds. You may train in this ability at or after levels 62 and 64.",
        "Furious Rampage": "This ability decreases the amount of time required between uses of Rampage by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Fury of Magic": "This ability further increases your chance to score a critical hit with your direct damage spells.",
        "Fury of Magic Mastery": "This ability further increases your chance to score a critical hit with your direct damage spells.",
        "Fury of the Ages": "This ability further increases your chance to score a critical blow against your opponent. You may train in this ability once each level, upon reaching levels 62, 63, and 64.",
        "Guardian of the Forest": "This ability transforms you into an exceptionally bloodthirsty wolf that attacks with lightning speed, for a brief time. You may train the three ranks of this ability at or after levels 61, 63, and 65.",
        "Hand of Piety": "This ability invokes the direct blessing of your deity upon all of those nearby. All group members in range are healed 750 hit points in the first rank, and successive ranks each add 250. You may train in this ability at or after levels 61, 63, and 65.",
        "Harmonious Attack": "This ability grants you a chance of performing a double attack in any given combat round. You may train in this ability once each level after reaching level 61.",
        "Harvest of Druzzil": "This ability gathers streams of additional mana into your being. You may train this ability at or after level 62.",
        "Hastened Divinity": "This ability decreases the amount of time required between uses of Bestow Divine Aura by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Exodus": "This ability decreases the amount of time required between uses of Exodus by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Gathering": "This ability decreases the amount of time required between uses of Gather Mana by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Instigation": "This ability decreases the amount of time required between uses of Area Taunt by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Mending": "This ability decreases the amount of time required between uses of Mend Companion by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Purification": "This ability decreases the amount of time required between uses of Purge Poison by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Purification of Body": "This ability decreases the amount of time required between uses of Purify Body by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Purification of the Soul": "This ability decreases the amount of time required between uses of Purify Soul by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Rabidity": "This ability decreases the amount of time required between uses of Rabid Bear by four minutes per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Root": "This ability decreases the amount of time required between uses of Strong Root by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Hastened Stealth": "This ability reduces the time between which you may attempt to hide or evade by one second per rank. You may train the ranks of this ability at or after levels 61, 62, and 63.",
        "Hasty Exit": "This ability decreases the amount of time required between uses of Escape by ten percent per rank. You may train in this ability once each level, upon reaching level 63.",
        "Headshot": "This ability provides you the chance of instantly killing an opponent(humanoid only) who is too far below you in level to provide a challenge, when using a bow. (Deals 32,000 dmg on humanoid mobs lvl 46 and below.)",
        "Host of the Elements": "This ability calls an assault of elemental minions into existence directed at a target. The minions attack the target without question until they are called back to their plane 30 seconds later. The initial rank of this ability calls five elementals. Additional ranks add two elementals each. You may train the ranks of this ability at or after levels 63, 64, and 65.",
        "Ingenuity": "Years of experimentation have led to the discovery of how to gain additional performance (in the form of critical spell hits) from weapons and other items. You may train in this ability at or after levels 61, 63, and 65.",
        "Innate Defense": "This ability further increases your mitigation of incoming melee damage. You may train in this ability once each level after reaching level 61.",
        "Knight's Advantage": "This ability grants you an increased chance of performing a double attack in any given combat round. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Lightning Reflexes": "This ability further increases your chance of completely avoiding incoming melee damage. You may train in this ability once each level after reaching level 61.",
        "Living Shield": "This extends your capacity to act as a living shield, This ability adds twelve seconds per rank to the duration of your /shield. You may train the ranks of this ability at or after levels 61, 63, and 65.",
        "Mastery of the Past": "This ability makes it impossible for you to fizzle a spell. The first level affects all spells below level 54. The second, on all spells below level 56. The third, on all spells below level 58. You may train in this ability once each level, upon reaching levels 62, 63, and 64.",
        "Mending of the Tranquil": "This ability further increases the chance of performing a superior mend. The three ranks of this ability may be trained once each level for levels 63 and above.",
        "Mithaniel's Binding": "This ability further increases the amount of healing provided by a single bandage while binding wounds. The two ranks of this ability may be trained at or after levels 63 and 64.",
        "Nimble Evasion": "This ability grants you a chance to hide or evade while moving. Each rank provides an increasing chance. You may train in this ability once each level after reaching level 61.",
        "Project Illusion": "This ability allows you to project your innate talent with illusions upon others. (Activating this ability on a targeted group member causes your next illusion spell to affect that target.)",
        "Punishing Blade": "This ability increases the chance of scoring an extra hit with all two-handed weapons that you wield. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Radiant Cure": "This ability grants its wielder the ability to cure their party of many afflictions, poisons, curses, and harmful magics. You may train in the ranks of this ability at or after levels 61, 63, and 65.",
        "Raging Flurry": "This ability further increases the chance of performing a flurry attack upon successfully scoring a triple attack. The three ranks of this ability may be trained once each level for levels 63 and above.",
        "Rush to Judgment": "Training in this ability shortens the time between uses of Divine Stun by seven seconds per rank. The three ranks of this ability may be trained once each level for levels 63 and above.",
        "Servant of Ro": "This ability calls a loyal servant into being who will repeatedly hurl fire at your target. Each rank of this ability increases the amount of time that the servant is able to remain by your side (45, 70, and 90 seconds). You may train the ranks of this ability at or after levels 61, 63, and 65.",
        "Shroud of Stealth": "This ability provides a previously unheard of level of stealth. The Rogue is able to draw shadows about himself so completely, even creatures that are normally not fooled by such trickery are frequently unable to see him. You may train in this ability upon reaching level 63.",
        "Sionachie's Crescendo": "This ability provides an even greater extension to the range of group songs. The three ranks of this ability may be trained once each level for levels 63 and above.",
        "Speed of the Knight": "This ability grants you the chance to score an additional attack with two-handed weapons. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Spirit Call": "This ability calls a number of spirit companions into existence directed at a target. The companions attack the target without question until they are called back to their home plane 60 seconds later. The initial rank of this ability calls three companions. Additional ranks add one companion each. You may train the ranks of this ability at or after levels 61, 63, and 65.",
        "Spirit of the Wood": "For a brief time, you are able to commune with the woodland spirits who provide your party with exceptional regenerative abilities and a protective shield of armor and thorns. You may train in the three ranks of this ability at or after levels 61, 63, and 65.",
        "Stalwart Endurance": "This ability grants a chance to endure what would otherwise be a stunning blow, from any angle, without being stunned. You may train in the ranks of this ability at or after levels 61, 63, and 65.",
        "Suspended Minion": "This ability grants the summoner the ability to suspend and recall their existing pet at will, provided they remain in their current zone. The first rank suspends the pet at its current health only, while the second rank suspends the pet with all of its beneficial effects as well as its weapons and armor. You may cast a second pet while your first pet is Suspended. You may train the first rank upon reaching level 62 and the second rank upon reaching level 64.",
        "Tactical Mastery": "Studying ones opponent for weaknesses provides the knowledge and ability to pierce through advanced defenses. Each rank of this ability grants an increasing chance of bypassing an opponents special defenses, such as dodge, block, parry, and riposte. You may train in this ability at or after levels 61, 63, and 65.",
        "Technique of Master Wu": "Under the tutelage of Wu, Monks are able to hone their skills to the point of being able to execute a second and sometimes even third strike when scoring a hit with their special attacks. This ability grants a 20 percent increase in the chance of scoring multiple special attacks, per rank.",
        "Theft of Life": "This ability grants a chance that the healing effect on your lifetaps will provide an exceptional amount of healing.",
        "Total Domination": "This ability adds strength to your charm spells. Victims of your charm spells are less likely to break out of their charms early.",
        "Touch of the Wicked": "This ability decreases the amount of time required between uses of Harm Touch and its upgrades by twelve minutes per rank. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Unfailing Divinity": "The most devout find that their calls are answered with much greater frequency. This ability grants your Death Pact-type spells a second chance to successfully heal their target. Additional ranks of this ability cause said spells to do a portion of their healing value even on a complete failure. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Unholy Touch": "A further enhancement to Improved Harm Touch, this ability grants a considerable bonus to the amount of damage done by that ability. You gain the ability to train an additional rank at levels 61, 63, and 65.",
        "Virulent Paralysis": "This ability causes your target to succumb to a sudden, violent attack, after which they are frequently unable to move for a time. Each rank of this ability increases the amount of time that the victim remains immobile. You may train the ranks of this ability at or after levels 61, 63, and 65.",
        "Viscid Roots": "Root spells applied by the owner of this ability are significantly less likely to break when the victim takes damage initiated by anyone, unlike previous abilities which only affect damage caused by the caster.",
        "Wake the Dead": "This ability calls the shade of a nearby corpse back to life to serve the Necromancer. The soulless abomination will fight the target, until called back to the afterlife some time later. The slave summoned by the first rank of this ability serves for 60 seconds, and each increasing rank adds 15 additional seconds. You may train the ranks of this ability at or after levels 61, 63, and 65.",
        "Wrack Summoned": "This ability further improves the damage caused by your Turn Summoned ability.",
        "Wrack Undead": "This ability grants you a more damaging version of your Turn Undead ability.",
        "Wrath of the Wild": "Developed by the denizens of Tranquility as a deterrent to potential attackers, this ability will shield you with a single-hit, large damage barrier of thorns. Additional ranks of this ability increase the amount of damage that is inflicted by 350, 500, and 650 points of damage. You may train the ranks of this ability at or after levels 61, 63, and 65."
    }

    description = aa_descriptions.get(aa_name)
    if description:
        return Ability(name=aa_name, description=description)
    return None
