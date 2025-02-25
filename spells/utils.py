import random
import math
from common.models.items import Items
from common.models.spells import SpellsNew
from common.constants import SE
from common.constants import RACES
from common.constants import ZONE_SHORT_TO_LONG
from common.constants import SPELL_TARGETS
from .se_utils import describe_se_ac

FEAR_MAX_LEVEL = 52

spell_effects = {
    0: "Hitpoints",
    1: "AC",
    2: "ATK",
    3: "Movement Rate",
    4: "STR",
    5: "DEX",
    6: "AGI",
    7: "STA",
    8: "INT",
    9: "WIS",
    10: "CHA",
    11: "Melee Speed",
    12: "Invisibility",
    13: "See Invis",
    14: "Enduring Breath",
    15: "Mana",
    16: "NPC Frenzy",
    17: "NPC Awareness",
    18: "NPC Aggro",
    19: "NPC Faction",
    20: "Blindness",
    21: "Stun",
    22: "Charm",
    23: "Fear",
    24: "Fatigue",
    25: "Bind Affinity",
    26: "Gate",
    27: "Dispel Magic",
    28: "Invis vs Undead",
    29: "Invis vs Animals",
    30: "Frenzy Radius",
    31: "Enthrall (Mez)",
    32: "Create Item",
    33: "Spawn NPC",
    34: "Confuse",
    35: "Disease Counter",
    36: "Poison Counter",
    37: "Detect Hostile",
    38: "Detect Magic",
    39: "Detect Poison",
    40: "Invulnerability",
    41: "Banish",
    42: "Shadow Step",
    43: "Berserk",
    44: "Lycanthropy",
    45: "Vampirism",
    46: "Resist Fire",
    47: "Resist Cold",
    48: "Resist Poison",
    49: "Resist Disease",
    50: "Resist Magic",
    51: "Detect Traps",
    52: "Detect Undead",
    53: "Detect Summoned",
    54: "Detect Animals",
    55: "Stoneskin",
    56: "True North",
    57: "Levitation",
    58: "Illusion",
    59: "Reflect Damage",
    60: "Transfer Item",
    61: "Identify",
    62: "Item ID",
    63: "NPC Wipe Hate List",
    64: "Spin Stun",
    65: "Infravision",
    66: "Ultravision",
    67: "NPC POV",
    68: "Reclaim Energy",
    69: "Max Hitpoints",
    70: "Corpse Bomb",
    71: "Create Undead",
    72: "Preserve Corpse",
    73: "Targets View",
    74: "Feign Death",
    75: "Ventriloquism",
    76: "Sentinel",
    77: "Locate Corpse",
    78: "Spell Shield",
    79: "HP when cast",
    80: "Enchant: Light",
    81: "Resurrect",
    82: "Summon Player",
    83: "Teleport",
    84: "TossUP",
    85: "Add Proc:",
    86: "Reaction Radius",
    87: "Telescope",
    88: "Combat Portal",
    89: "Player Size",
    90: "Ignore Pet",
    91: "Summon Corpse",
    92: "Instant Hate",
    93: "Weather Control",
    94: "Fragile",
    95: "Sacrifice",
    96: "Silence",
    97: "Max Mana",
    98: "Bard Haste",
    99: "Root",
    100: "DoT Heals",
    101: "Complete Heal",
    102: "Pet No Fear",
    103: "Summon Pet",
    104: "Translocate",
    105: "Anti-Gate",
    106: "Beastlord Pet",
    107: "Alter NPC Level",
    108: "Familiar",
    109: "Create Item In Bag",
    110: "Increase Archery",
    111: "Resistances",
    112: "Set Casting Level",
    113: "Summon Mount",
    114: "Modify Hate",
    115: "Cornucopia",
    116: "Curse",
    117: "Hit Magic",
    118: "Amplification",
    119: "Bard Haste 2",
    120: "Heal Mod",
    121: "Iron Maiden",
    122: "Reduce Skill",
    123: "Immunity",
    124: "Focus Damage Percent",
    125: "Focus Heal Mod",
    126: "Focus Resist Mod",
    127: "Focus Cast Time Mod",
    128: "Focus Duration Mod",
    129: "Focus Range Mod",
    130: "Focus Hate Mod",
    131: "Focus Reagent Mod",
    132: "Focus Mana Mod",
    133: "Focus Stun Time Mod",
    134: "Limit: Level Max",
    135: "Limit: Resist Type",
    136: "Limit: Target Type",
    137: "Limit: Effect",
    138: "Limit: Spell Type",
    139: "Limit: Spell",
    140: "Limit: Min Duration",
    141: "Limit: Instant Only",
    142: "Limit: Level Min",
    143: "Limit: Cast Time Min",
    144: "Limit: Cast Time Max",
    145: "NPC Warder Banish",
    146: "Resist Electricity",
    147: "Percent Heal",
    148: "Stacking Blocker",
    149: "Strip Virtual Slot",
    150: "Death Pact",
    151: "Pocket Pet",
    152: "Pet Swarm",
    153: "Balance Party Health",
    154: "Cancel Negative",
    155: "PoP Resurrect",
    156: "Mirror",
    157: "Feedback",
    158: "Reflect",
    159: "Mod All Stats",
    160: "Sobriety",
    161: "Spell Guard",
    162: "Melee Guard",
    163: "Absorb Hit",
    164: "Object - Sense Trap",
    165: "Object - Disarm Trap",
    166: "Object - Picklock",
    167: "Focus Pet Power",
    168: "Defensive",
    169: "Critical Melee",
    170: "Critical Spell",
    171: "Crippling Blow",
    172: "Evasion",
    173: "Riposte",
    174: "Dodge",
    175: "Parry",
    176: "Dual Wield",
    177: "Double Attack",
    178: "Melee Lifetap",
    179: "Puretone",
    180: "Sanctification",
    181: "Fearless",
    182: "Hundred Hands",
    183: "Skill Increase Chance",
    184: "Accuracy Percent",
    185: "Skill Damage Mod",
    186: "Min Damage Done Mod",
    187: "Mana Balance",
    188: "Block",
    189: "Endurance",
    190: "Max Endurance",
    191: "Amnesia",
    192: "Hate",
    193: "Skill Attack",
    194: "Fade",
    195: "Stun Resist",
    196: "Strikethrough",
    197: "Skill Damage Taken",
    198: "Instant Endurance",
    199: "Taunt",
    200: "Proc Chance",
    201: "Ranged Proc",
    202: "Illusion Other",
    203: "Mass Buff",
    204: "Group Fear Immunity",
    205: "Rampage",
    206: "AE Taunt",
    207: "Flesh to Bone",
    208: "Purge Poison",
    209: "Cancel Beneficial",
    210: "Pet Shield",
    211: "AE Melee",
    212: "Frenzied Devastation",
    213: "Pet Percent HP",
    214: "HP Max Percent",
    216: "Accuracy Amount",
    218: "Pet Crit Melee",
    219: "Slay Undead",
    220: "Skill Damage Amount",
    221: "Reduce Weight",
    222: "Block Behind",
    223: "Double Riposte",
    224: "Add Riposte",
    225: "Give Double Attack",
    226: "2H Bash",
    227: "Reduce Skill Timer",
    228: "Reduce Fall Damage",
    229: "Cast Through Stun",
    230: "Increase Shield Dist",
    231: "Stun Bash Chance",
    232: "Divine Save",
    233: "Metabolism",
    234: "Poison Mastery",
    235: "Focus Channeling",
    236: "Free Pet",
    237: "Pet Affinity",
    238: "Permanent Illusion",
    239: "Stonewall",
    240: "String Unbreakable",
    241: "Improve Reclaim Energy",
    242: "Increase Chance Memwipe",
    243: "No Break Charm Chance",
    244: "Root Break Chance",
    245: "Trap Circumvention",
    246: "Lung Capacity",
    247: "Increase Skill Cap",
    248: "Extra Specialization",
    249: "Offhand Min",
    250: "Spell Proc Chance",
    251: "Endless Quiver",
    252: "Backstab Front",
    253: "Chaotic Stab",
    254: "No Spell",
    255: "Shielding Duration Mod",
    256: "Shroud of Stealth",
    257: "Give Pet Hold",
    258: "Triple Backstab",
    259: "AC Limit Mod",
    260: "Add Instrument Mod",
    261: "Song Mod Cap",
    262: "Stats Cap",
    263: "Tradeskill Masteries",
    264: "Reduce AA Timer",
    265: "No Fizzle",
    266: "Add Extra Attack Chance (2H)",
    267: "Add Pet Commands",
    268: "Alchemy Fail Rate",
    269: "Bandage Percent Limit",
    270: "Bard Song Range",
    271: "Base Run Mod",
    272: "Casting Level",
    273: "Critical DoT",
    274: "Critical Heal",
    275: "Critical Mend",
    276: "Dual Wield Amount",
    277: "Extra DI Chance",
    278: "Finishing Blow",
    279: "Flurry Chance",
    280: "Pet Flurry Chance",
    281: "Give Pet Feign",
    282: "Increase Bandage Amount",
    283: "Special Attack Chain",
    284: "LoH Set Heal",
    285: "No Move Check Sneak",
    286: "Focus Damage Amount",
    287: "Focus Duration Mod (static)",
    288: "Add Proc Hit",
    289: "Improved Spell Effect",
    290: "Increase Movement Cap",
    291: "Purify",
    292: "Strikethrough 2",
    293: "Stun Resist 2",
    294: "Spell Crit Chance",
    295: "Reduce Timer Special",
    296: "Focus Damage Percent Incoming",
    297: "Focus Damage Amount Incoming",
    298: "Height (Small)",
    299: "Wake the Dead",
    300: "Doppelganger",
    301: "Increase Range Damage",
    302: "Focus Damage Percent Crit",
    303: "Focus Damage Amount Crit",
    304: "Secondary Riposte Mod",
    305: "Mitigate Damage Shield",
    306: "Wake the Dead 2",
    307: "Appraisal",
    308: "Zone Suspend Minion",
    309: "Gate Casters Bindpoint",
    310: "Focus Reuse Timer",
    311: "Limit: Combat Skill",
    312: "Observer",
    313: "Forage Master",
    314: "Improved Invis",
    315: "Improved Invis Undead",
    316: "Improved Invis Animals",
    317: "Worn Regen Cap",
    318: "Worn Mana Cap",
    319: "Critical HP Regen",
    320: "Shield Block Chance",
    321: "Reduce Target Hate",
    322: "Gate Starting City",
    323: "Defensive Proc",
    324: "HP for Mana",
    325: "No Break AE Sneak",
    326: "Spell Slots",
    327: "Buff Slots",
    328: "Negative HP Limit",
    329: "Mana Absorb Percent Damage",
    330: "Critical Melee Damage Mod",
    331: "Alchemy Item Recovery",
    332: "Summon to Corpse",
    333: "Doom Rune Effect",
    334: "HP No Move",
    335: "Focus Immunity Focus",
    336: "Illusionary Target",
    337: "Increase Exp Percent",
    338: "Expedient Recovery",
    339: "Focus Cast Proc",
    340: "Chance Spell",
    341: "Worn Attack Cap",
    342: "No Panic",
    343: "Spell Interrupt",
    344: "Item Channeling",
    345: "Assassinate Max",
    346: "Headshot Max",
    347: "Double Ranged Attack",
    348: "Limit: Mana Min",
    349: "Increase Damage with Shield",
    350: "Manaburn",
    351: "Spawn Interactive Object",
    352: "Increase Trap Count",
    353: "Increase SOI Count",
    354: "Deactivate All Traps",
    355: "Learn Trap",
    356: "Change Trigger Type",
    357: "Focus Mute",
    358: "Instant Mana",
    359: "Passive Sense Trap",
    360: "Proc on Kill Shot",
    361: "Proc on Death",
    362: "Potion Belt",
    363: "Bandolier",
    364: "Add Triple Attack Chance",
    365: "Proc on Spell Kill Shot",
    366: "Group Shielding",
    367: "Modify Body Type",
    368: "Modify Faction",
    369: "Corruption",
    370: "Resist Corruption",
    371: "Slow",
    372: "Grant Foraging",
    373: "Doom Always",
    374: "Trigger Spell",
    375: "Critical DoT Damage Mod",
    376: "Fling",
    377: "Doom Entity",
    378: "Resist Other Spell Effect",
    379: "Directional Shadow Step",
    380: "Knockback Explosive",
    381: "Fling to Self",
    382: "Suppression",
    383: "Focus Cast Proc Normalized",
    384: "Fling to Target",
    385: "Limit: Which Spell Group",
    386: "Doom Dispeller",
    387: "Doom Dispellee",
    388: "Summon All Corpses",
    389: "Focus Timer Refresh",
    390: "Focus Timer Lockout",
    391: "Limit: Mana Max",
    392: "Focus Heal Amt",
    393: "Focus Heal Percent Incoming",
    394: "Focus Heal Amt Incoming",
    395: "Focus Heal Percent Crit",
    396: "Focus Heal Amt Crit",
    397: "Pet Amt Mitigation",
    398: "Focus Swarm Pet Duration",
    399: "Focus Twincast",
    400: "Healburn",
    401: "Mana Ignite",
    402: "Endurance Ignite",
    403: "Limit: Spell Class",
    404: "Limit: Spell Subclass",
    405: "Staff Block Chance",
    406: "Doom Limit Use",
    407: "Doom Focus Used",
    408: "Limit HP",
    409: "Limit Mana",
    410: "Limit Endurance",
    411: "Limit: Class Player",
    412: "Limit: Race",
    413: "Focus Base Effects",
    414: "Limit: Casting Skill",
    415: "Limit: Item Class",
    416: "AC 2",
    417: "Mana 2",
    418: "Increased Skill Damage 2",
    419: "Contact Ability 2",
    420: "Focus Limit Use",
    421: "Focus Limit Use Amt",
    422: "Limit: Limit Use Min",
    423: "Limit: Limit Use Type",
    424: "Gravitate",
    425: "Fly",
    426: "Add Ext Target Slots",
    427: "Skill Proc",
    428: "Skill Proc Modifier",
    429: "Skill Proc Success",
    430: "Post Effect",
    431: "Post Effect Data",
    432: "Expand Max Active Trophy Benefits",
    433: "Critical DoT Decay",
    434: "Critical Heal Decay",
    435: "Critical Regen Decay",
    436: "Beneficial Countdown Hold",
    437: "Teleport to Anchor",
    438: "Translocate to Anchor",
    439: "Assassinate",
    440: "Finishing Blow Max",
    441: "Distance Removal",
    442: "Doom Req Target",
    443: "Doom Req Caster",
    444: "Improved Taunt",
    445: "Add Merc Slot",
    446: "A Stacker",
    447: "B Stacker",
    448: "C Stacker",
    449: "D Stacker",
    450: "DoT Guard",
    451: "Melee Threshold Guard",
    452: "Spell Threshold Guard",
    453: "Doom Melee Threshold",
    454: "Doom Spell Threshold",
    455: "Add Hate Percent",
    456: "Add Hate Over Time Percent",
    457: "Resource Tap",
    458: "Faction Mod Percent"
}


def calc_spell_effect_value1(formula, base_value, max_value, level):
    sign = 1
    ubase = abs(base_value)
    result = 0
    if max_value < base_value and max_value != 0:
        sign = -1
    match formula:
        case 0 | 100:
            result = ubase
        case 101:
            result = ubase + sign * (level / 2)
        case 102:
            result = ubase + sign * level
        case 103:
            result = ubase + sign * level * 2
        case 104:
            result = ubase + sign * level * 3
        case 105 | 107:
            result = ubase + sign * level * 4
        case 108:
            result = math.floor(ubase + sign * level / 3)
        case 109:
            result = math.floor(ubase + sign * level / 4)
        case 110:
            result = math.floor(ubase + level / 5)
        case 111:
            result = ubase + 5 * (level - 16)
        case 112:
            result = ubase + 8 * (level - 24)
        case 113:
            result = ubase + 12 * (level - 34)
        case 114:
            result = ubase + 15 * (level - 44)
        case 115:
            result = ubase + 15 * (level - 54)
        case 116:
            result = math.floor(ubase + 8 * (level - 24))
        case 117:
            result = ubase + 11 * (level - 34)
        case 118:
            result = ubase + 17 * (level - 44)
        case 119:
            result = math.floor(ubase + level / 8)
        case 121:
            result = math.floor(ubase + level / 3)
        case _:
            if formula < 100:
                result = ubase + (level * formula)

    if max_value != 0:
        if sign == 1:
            if result > max_value:
                result = max_value
        else:
            if result < max_value:
                result = max_value
        if base_value < 0 < result:
            result *= -1

    return result


def calc_spell_effect_value(formula, base_value, max_value, level):
    """
    Calculates the raw value for a spell effect associated with a spell

    :param formula:
    :param base_value:
    :param max_value:
    :param level:
    :return:
    """
    result = 0
    abs_base_value = abs(base_value)
    negation = -1 if max_value < base_value and max_value != 0 else 1

    match formula:
        case 0 | 100:
            result = abs_base_value
        case 101:
            result = negation * (abs_base_value + (level / 2))
        case 102:
            result = negation * (abs_base_value + level)
        case 103:
            result = negation * (abs_base_value + (level * 2))
        case 104:
            result = negation * (abs_base_value + (level * 3))
        case 105:
            result = negation * (abs_base_value + (level * 4))
        case 107 | 108:
            result = negation * abs_base_value
        case 109:
            result = negation * (abs_base_value + (level / 4))
        case 110:
            result = negation * (abs_base_value + (level / 6))
        case 111:
            result = negation * (abs_base_value + 6 * (level - 16))
        case 112:
            result = negation * (abs_base_value + 8 * (level - 24))
        case 113:
            result = negation * (abs_base_value + 10 * (level - 34))
        case 114:
            result = negation * (abs_base_value + 15 * (level - 44))
        case 115:  # only used in Symbol of Transal
            result = abs_base_value
            if level > 15:
                result += 7 * (level - 15)
        case 116:  # only used in Symbol of Ryltan
            result = abs_base_value
            if level > 24:
                result += 10 * (level - 24)
        case 117:  # only used in Symbol of Pinzarn
            result = abs_base_value
            if level > 34:
                result += 13 * (level - 34)
        case 118:  # mainly used in Symbol of Naltron, but a couple others also
            result = abs_base_value
            if level > 44:
                result += 20 * (level - 44)

        case 119:
            result = abs_base_value + (level / 8)
        case 120 | 122:  # client duration extension focus effects are disabled for spells that use this formula
            result = negation * abs_base_value
        case 121:
            result = abs_base_value + (level / 3)
        case 123:
            result = random.randint(abs_base_value, abs(max_value))
        case 124:
            result = abs_base_value
            if level > 50:
                result += negation * (level - 50)
        case 125:
            result = abs_base_value
            if level > 50:
                result += negation * 2 * (level - 50)
        case 126:
            result = abs_base_value
            if level > 50:
                result += negation * 3 * (level - 50)
        case 127:
            result = abs_base_value
            if level > 50:
                result += negation * 4 * (level - 50)
        case 128:
            result = abs_base_value
            if level > 50:
                result += negation * 5 * (level - 50)
        case 129:
            result = abs_base_value
            if level > 50:
                result += negation * 10 * (level - 50)
        case 130:
            result = abs_base_value
            if level > 50:
                result += negation * 15 * (level - 50)
        case 131:
            result = abs_base_value
            if level > 50:
                result += negation * 20 * (level - 50)
        case 150 | 201 | 202 | 203 | 204 | 205:
            result = max_value
        case _:
            if formula < 100:
                result = abs_base_value + (level * formula)

    # now check result against the allowed maximum
    if max_value != 0:
        if negation == 1:
            if result > max_value:
                result = max_value
        else:
            if result < max_value:
                result = max_value

    # if base value is less than zero, then the result needs to be negative too
    if base_value < 0 < result:
        result *= -1
    return result


def determine_spell_effect_max_level(formula: int, effect_base_value: int, max_value: int, start_level: int) -> int:
    """
    Determines the level where the spell effect reaches its max value (based on the formula)

    There is plenty of room here to optimize how this is done.  However, this is good enough for now.

    :param formula:
    :param effect_base_value:
    :param max_value:
    :param start_level:
    :return: int: the player level where the spell effect reaches its max_value
    """
    temp_max_level = start_level
    while True:
        temp_max_value = calc_spell_effect_value(formula, effect_base_value, max_value, temp_max_level)
        if temp_max_value > 0:
            if temp_max_value >= max_value:
                break
            temp_max_level += 1
        else:
            if temp_max_value <= max_value:
                break
            temp_max_level += 1
    return temp_max_level


def prep_spell_data(spell_data: SpellsNew):
    # Calculate the minimum level for this spell for spell effect description and spell_min_duration purposes
    min_level = 65 # Server max level
    for i in range(1, 16):
        if getattr(spell_data, 'classes' + str(i)) < min_level:
            min_level = getattr(spell_data, 'classes' + str(i))

    spell_max_duration = calc_buff_duration(65, spell_data.buff_duration_formula, spell_data.buff_duration)

    # Extract slot_id, effect_id, base_value, max_value from spell data
    sp_effects = list()
    for slot_id in range(1, 13):
        if spell_data.__getattribute__(f'effectid{slot_id}') != 254:
            sp_effects.append(
                (slot_id,
                 getattr(spell_data, f'effectid{slot_id}'),
                 getattr(spell_data, f'formula{slot_id}'),
                 getattr(spell_data, f'effect_base_value{slot_id}'),
                 getattr(spell_data, f'max{slot_id}'))
            )

    sp_effects = build_effect_descriptions(spell_data, sp_effects, spell_max_duration, min_level)
    return sp_effects

def build_effect_descriptions(spell_data: object, effects: list, spell_duration: int, min_level: int) -> list:
    """
    Convert a list of raw spell effect tuple values into human-readable spell description

    :param spell_data:
    :param effects:
    :param spell_duration:
    :param min_level: the minimum level that any class can scribe this spell
    :return: a list of spell effect descriptions for each of 12 slots as necessary
    """
    server_max_level = 65
    spell_descriptions = list()
    for slot_id, effect_id, formula, effect_base_value, effect_max_value in effects:
        # Effect ID of 254 means empty
        # Effect ID 10 (CHA) with 0 increase/decrease is an anomaly (see Yaulp: ID 205)
        if effect_id == 254 or (effect_id == 10 and effect_base_value == 0):
            continue
        base = calc_spell_effect_value(formula, effect_base_value, effect_max_value, min_level)
        max_value = calc_spell_effect_value(formula, effect_base_value, effect_max_value, server_max_level)

        base = math.floor(base)
        max_value = math.floor(max_value)

        max_level = determine_spell_effect_max_level(formula, effect_base_value, max_value, min_level)

        description = ""
        match effect_id:
            case SE.Hitpoints.value:
                description = f"{'Decrease' if effect_base_value < 0 else 'Increase'} {spell_effects[effect_id]}"

                if base != max_value:
                    base_string = f"{abs(base)} (L{min_level})"
                    base_string += f" per tick" if spell_duration > 1 else ""

                    max_string = f"{abs(max_value)} (L{max_level})"
                    max_string += f" per tick" if spell_duration > 1 else ""

                    description += f" by {base_string} to {max_string}"
                else:
                    description += f" by {-max_value if max_value < 0 else max_value}"

            case SE.AC.value:
                description = describe_se_ac(spell_effects[effect_id], base, max_value, min_level, max_level)
            case 2:  # Attack Power
                description = (f"{'Decrease' if effect_base_value < 0 else 'Increase'} {spell_effects[effect_id]} by "
                               f"{abs(effect_base_value)}")
            case SE.Movement_Speed.value:  # Movement Rate
                description = f"{'Decrease' if max_value < 0 else 'Increase'} {spell_effects[effect_id]}"
                if base != max_value:
                    description += f" by {abs(base)}% (L{min_level}) to {abs(max_value)}% (L{abs(max_level)})"
                else:
                    if max_value < 0:
                        description += f" by 100%"
                    else:
                        description += f" by {max_value}%"
            case SE.Attack_Speed.value:  # Decrease or Increase Attack Speed
                if max_value < 100:  # Decrease
                    description = f"Decrease Attack Speed"
                    if base != max_value:
                        description += f" by {100 - base}% (L{min_level}) to {100 - max_value}% (L{max_level})"
                    else:
                        description += f" by {100 - max_value}%"
                else:
                    description = f"Increase Attack Speed"
                    if base != max_value:
                        description += f" by {base - 100}% (L{min_level}) to {max_value - 100}% (L{max_level})"
                    else:
                        description += f" by {max_value - 100}%"
            case 15 | 100:
                description = f"{spell_effects[effect_id]}"
                duration = calc_buff_duration(server_max_level,
                                              getattr(spell_data, 'buff_duration_formula'),
                                              getattr(spell_data, 'buff_duration')
                                              )
                if base != max_value:
                    description += f" by {abs(base)} (L{min_level}) to {abs(max_value)} (L{max_level})"
                    if duration > 0:
                        description += f" per tick (total {abs(base * duration)} to {abs(max_value * duration)})"
                else:
                    description += f" by {max_value}"
                    if duration > 0:
                        description += f" per tick (total {abs(max_value * duration)})"
            case 21:  # stun
                description = f"{spell_effects[effect_id]}"
                if base != max_value:
                    description += f" {base / 1000} sec (L{min_level}) to {max_value / 1000} sec (L{max_level}))"
                else:
                    description += f" ({max_value / 1000} sec)"
            case 22 | 31:
                description += f"{spell_effects[effect_id]} up to level {max_value}"
            case 23:  # Fear
                description += f"{spell_effects[effect_id]} up to level {FEAR_MAX_LEVEL}"
            case 30 | 86:
                description = f"{spell_effects[effect_id]}"
                description += f" ({effect_base_value}/{effect_max_value})"
            case 32:  # Summon Item
                description = f"{spell_effects[effect_id]}"
                item = Items.objects.filter(id=effect_base_value).first()
                if item:
                    description += f" : <a class='link' href=/items/view/{effect_base_value}>{item.Name}</a>"
            case 33 | 68 | 71 | 108 | 113 | 152:
                description = f"{spell_effects[effect_id]}"
                description += (f" <a class='link' href='/pets/view/{getattr(spell_data, 'teleport_zone')}'>"
                                f"{getattr(spell_data, 'teleport_zone')}</a>")
            case 36:
                description = f"{'Decrease' if effect_base_value < 0 else 'Increase'} {spell_effects[effect_id]}"
                description += f" by {abs(effect_base_value)}"
            case 13 | 18 | 20 | 25 | 26 | 28 | 29 | 40 | 41 | 42 | 44 | 52 | 53 | 54 | 56 | 57 | 61 | 64 | 65 | 66 | 67 | 68 | 73 | 74 | 75 | 76 | 77 | 82 | 90 | 93 | 94 | 95 | 96 | 99 | 101 | 103 | 104 | 105 | 115 | 117 | 135 | 137 | 138 | 141 | 150 | 151 | 154 | 156 | 178 | 179 | 182 | 194 | 195 | 205 | 206 | 311 | 314 | 299:
                description = f"{spell_effects[effect_id]} ({effect_base_value})"  # TODO: Fix output here
            case 58:
                description = f"{spell_effects[effect_id]}:"
                description += f"  {RACES[effect_base_value]}"
            case 59:  # Damage Shields
                description = f"{spell_effects[effect_id]}"
                if base != max_value:
                    description += f" by {base} (L{min_level}) to {max_value} (L{max_level})"
                else:
                    description += f" by {-max_value if max_value < 0 else max_value}"
            case 63 | 120 | 330:
                description = f"{spell_effects[effect_id]}"
                description += f" ({max_value}%)"
            case 81:
                description = f"{spell_effects[effect_id]}"
                description += f" and restore {base}% experience"
            case 83 | 88 | 145:
                description = (f"{spell_effects[effect_id]} to ({getattr(spell_data, 'effect_base_value1')}, "
                               f"{getattr(spell_data, 'effect_base_value2')}, "
                               f"{getattr(spell_data, 'effect_base_value3')}) in")
                if getattr(spell_data, 'teleport_zone') != "same":
                    zone_short_name = getattr(spell_data, 'teleport_zone')
                    zone_long_name = ZONE_SHORT_TO_LONG.get(zone_short_name, zone_short_name)
                    description += f" <a class='link' href=/zones/view/{zone_short_name}>{zone_long_name}</a>"
                else:
                    description += " : same zone"
            case 85 | 289 | 323:
                description = f"{spell_effects[effect_id]}"
                spell = SpellsNew.objects.filter(id=effect_base_value).first()
                description += f"  <a class='link' href=/spells/view/{effect_base_value}>{spell.name}</a>"
            case 89:
                description = f"{'Decrease' if max_value < 0 else 'Increase'} {spell_effects[effect_id]}"
                base -= 100
                max_value -= 100
                if base != max_value:
                    description += f" by {base}% (L{min_level}) to {max_value}% (L{max_level})"
                else:
                    description += f" by {max_value}%"
            case 87 | 98 | 114 | 119 | 123 | 124 | 125 | 127 | 128 | 129 | 130 | 131 | 132 | 158 | 169 | 173 | 174 | 175 | 176 | 177 | 180 | 181 | 183 | 186 | 188 | 200 | 201 | 216 | 227 | 266 | 273 | 294:
                description = f"{spell_effects[effect_id]}"
                if base != max_value:
                    description += f" by {base}% (L{min_level}) to {max_value}% (L{max_level})"
                else:
                    description += f" by {max_value}%"
            case 121:  # Reverse Damage Shield
                description = f"{spell_effects[effect_id]}"
                description += f" (-{max_value})"
            case 91:
                description = f"{spell_effects[effect_id]}"
                description += f" (max level {max_value})"
            case 136:
                description = f"{spell_effects[effect_id]}"
                v = ""
                if max_value < 0:
                    max_value = -max_value
                    v = " excluded"
                else:
                    v = ""
                description += f" ({SPELL_TARGETS[max_value]}) {v}"
            case 139:  # Limit: Spell
                description = f"{spell_effects[effect_id]}"
                v = " excluded" if effect_base_value < 0 else ""
                spell = SpellsNew.objects.filter(id=abs(effect_base_value)).first()
                description += f" (<a class='link' href=/spells/view/{abs(effect_base_value)}>{spell.name}</a>{v})"
            case 140:
                description = f"{spell_effects[effect_id]}"
                base *= 6
                max_value *= 6
                if base != max_value:
                    description += f" ({base} sec (L{min_level}) to {max_value} sec (L{max_level})"
                else:
                    description += f" ({max_value} sec)"
            case 143:  # limit min casting time
                description = f"{spell_effects[effect_id]}"
                base *= 6
                max_value *= 6
                if base != max_value:
                    description += f" ({base / 6000} sec (L{min_level}) to {max_value / 6000} sec (L{max_level}))"
                else:
                    description += f" ({max_value / 6000} sec)"
            case 148 | 149:  # stacking: overwrite existing spell
                description = f"{spell_effects[effect_id]}"
                description += (f" if slot {effect_id - 200} is effect '{spell_effects[effect_base_value]}' and < "
                                f"{getattr(spell_data, 'effect_limit_value' + str(slot_id))}")
            case 168 | 172 | 184 | 185:  # all skills modifier %
                description = f"{'Decrease' if max_value < 0 else 'Increase'} {spell_effects[effect_id]}"
                if base != max_value:
                    description += f" by {base}% (L{min_level}) to {max_value}% (L{max_level})"
                else:
                    description += f" by {-max_value if max_value < 0 else max_value}%"
            case 147:  # Increase hit points (%)
                description = f"{'Decrease' if max_value < 0 else 'Increase'} {spell_effects[effect_id]}"
                description += f" by {getattr(spell_data, 'max'+str(slot_id))} ({max_value}% max)"
            case 153:  # balance party health
                description = f"{spell_effects[effect_id]}"
                description += f" ({max_value}% penalty)"
            case 301:
                name = f"{spell_effects[effect_id]}"
                if max_value < 0:
                    name = name.replace("Increase", "Decrease")
                description = name
                if base != max_value:
                    description += f" by {base}% (L{min_level}) to {max_value}% (L{max_level})"
                else:
                    description += f" by {-max_value if max_value < 0 else max_value}%"
            case _:
                description = f"{'Decrease' if effect_base_value < 0 else 'Increase'} {spell_effects[effect_id]}"
                if base != max_value:
                    description += f" by {base} (L{min_level}) to {max_value} (L{max_level})"
                else:
                    if max_value < 0:
                        max_value = -max_value
                    description += f" by {-max_value if max_value < 0 else max_value}"
        # Replacing - (negative) signs because we use terms like "Decrease" and so absolute values are needed
        spell_descriptions.append((slot_id, description.replace("-","")))
    return spell_descriptions


def calc_buff_duration(level, formula, duration):
    """
    Returns how many ticks the buff will last
    A tick is 6 seconds

    :param level: the max level for the server
    :param formula: buff duration formula from spells_new entry
    :param duration: buff duration from spells_new_entry
    :return:
    """

    if formula >= 200:
        return formula

    # Mirrors CalcBuffDuration_formula from Server/zone/spells.cpp
    match formula:
        case 0:  # not a buff
            return 0
        case 1:
            i = level // 2
            return min(i, 1) if i < duration else duration
        case 2:
            i = 6 if level <= 1 else level // 2 + 5
            return min(i, 1) if i < duration else duration
        case 3:
            i = level * 30
            return min(i, 1) if i < duration else duration
        case 4:
            i = 50
            return min(i, duration) if duration else i
        case 5:
            i = 2
            return min(i, duration) if duration else i
        case 6:
            i = level // 2 + 2
            return min(i, duration) if duration else i
        case 7:
            i = level
            return min(i, duration) if duration else i
        case 8:
            i = level + 10
            return min(i, 1) if i < duration else duration
        case 9:
            i = level * 2 + 10
            return min(i, 1) if i < duration else duration
        case 10:
            i = level * 3 + 10
            return min(i, 1) if i < duration else duration
        case 11:
            i = level * 30 + 90
            return min(i, 1) if i < duration else duration
        case 12:  # not used by any spells
            i = level // 4
            i = max(i, 1)
            return i if duration == 0 else min(i, duration)
        case 50:  # permanent buff
            return 65534
        case _:  # Unknown formula
            return 0
