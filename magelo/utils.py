"""
Utility functions for calculating character profile data

These functions are generally used by the magelo view but didn't belong in that file
"""

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

