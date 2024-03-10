import datetime
from django import template

register = template.Library()


@register.filter(name='yes_no')
def yes_no(value):
    return "yes" if value == 1 else "no"


@register.filter(name='gender')
def gender_filter(value):
    return "Male" if value == 0 else "Female"


@register.filter(name='from_timestamp')
def from_timestamp(value):
    return datetime.datetime.fromtimestamp(value)


@register.filter(name='time_played')
def time_played(value):
    return datetime.timedelta(seconds=value)


@register.filter(name='inventory_slot')
def inventory_slot(value):
    slot = {
        0: "slotCursor",
        1: "Left Ear",
        2: "Head",
        3: "Face",
        4: "Right Ear",
        5: "Neck",
        6: "Shoulders",
        7: "Arms",
        8: "Back",
        9: "Left Wrist",
        10: "Right Wrist",
        11: "Range",
        12: "Hands",
        13: "Primary",
        14: "Secondary",
        15: "Left Finger",
        16: "Right Finger",
        17: "Chest",
        18: "Legs",
        19: "Feet",
        20: "Waist",
        21: "Ammo",
        22: "General 1 (Left, 1st)",
        23: "General 2 (Left, 2nd)",
        24: "General 3 (Left, 3rd)",
        25: "General 4 (Left, 4th)",
        26: "General 5 (Right, 1st)",
        27: "General 6 (Right, 2nd)",
        28: "General 7 (Right, 3rd)",
        29: "General 8 (Right, 4th)",
        250: "General 1, Slot 1 (Left)",
        251: "General 1, Slot 2 (Right)",
        252: "General 1, Slot 3 (Left)",
        253: "General 1, Slot 4 (Right)",
        254: "General 1, Slot 5 (Left)",
        255: "General 1, Slot 6 (Right)",
        256: "General 1, Slot 7 (Left)",
        257: "General 1, Slot 8 (Right)",
        260: "General 2, Slot 1 (Left)",
        261: "General 2, Slot 2 (Right)",
        262: "General 2, Slot 3 (Left)",
        263: "General 2, Slot 4 (Right)",
        264: "General 2, Slot 5 (Left)",
        265: "General 2, Slot 6 (Right)",
        266: "General 2, Slot 7 (Left)",
        267: "General 2, Slot 8 (Right)",
        270: "General 3, Slot 1 (Left)",
        271: "General 3, Slot 2 (Right)",
        272: "General 3, Slot 3 (Left)",
        273: "General 3, Slot 4 (Right)",
        274: "General 3, Slot 5 (Left)",
        275: "General 3, Slot 6 (Right)",
        276: "General 3, Slot 7 (Left)",
        277: "General 3, Slot 8 (Right)",
        280: "General 4, Slot 1 (Left)",
        281: "General 4, Slot 2 (Right)",
        282: "General 4, Slot 3 (Left)",
        283: "General 4, Slot 4 (Right)",
        284: "General 4, Slot 5 (Left)",
        285: "General 4, Slot 6 (Right)",
        286: "General 4, Slot 7 (Left)",
        287: "General 4, Slot 8 (Right)",
        290: "General 5, Slot 1 (Left)",
        291: "General 5, Slot 2 (Right)",
        292: "General 5, Slot 3 (Left)",
        293: "General 5, Slot 4 (Right)",
        294: "General 5, Slot 5 (Left)",
        295: "General 5, Slot 6 (Right)",
        296: "General 5, Slot 7 (Left)",
        297: "General 5, Slot 8 (Right)",
        300: "General 6, Slot 1 (Left)",
        301: "General 6, Slot 2 (Right)",
        302: "General 6, Slot 3 (Left)",
        303: "General 6, Slot 4 (Right)",
        304: "General 6, Slot 5 (Left)",
        305: "General 6, Slot 6 (Right)",
        306: "General 6, Slot 7 (Left)",
        307: "General 6, Slot 8 (Right)",
        310: "General 7, Slot 1 (Left)",
        311: "General 7, Slot 2 (Right)",
        312: "General 7, Slot 3 (Left)",
        313: "General 7, Slot 4 (Right)",
        314: "General 7, Slot 5 (Left)",
        315: "General 7, Slot 6 (Right)",
        316: "General 7, Slot 7 (Left)",
        317: "General 7, Slot 8 (Right)",
        320: "General 8, Slot 1 (Left)",
        321: "General 8, Slot 2 (Right)",
        322: "General 8, Slot 3 (Left)",
        323: "General 8, Slot 4 (Right)",
        324: "General 8, Slot 5 (Left)",
        325: "General 8, Slot 6 (Right)",
        326: "General 8, Slot 7 (Left)",
        327: "General 8, Slot 8 (Right)",
    }
    return slot[value] if value in slot else value


@register.filter(name='player_class')
def player_class(value):
    classes = {
        0: "Unknown",
        1: "Warrior",
        2: "Cleric",
        3: "Paladin",
        4: "Ranger",
        5: "Shadowknight",
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
    }
    return classes[value] if value in classes else "Unknown"


@register.filter(name='spell_target_type')
def spell_target_type(value):
    target_type = {
        0: "Rag'Zhezum Special",
        1: "Line of Sight",
        3: "Group V1",
        4: "PBAE",
        5: "Single",
        6: "Self",
        8: "Targeted Area of Effect",
        9: "Animal",
        10: "Undead",
        11: "Summoned",
        13: "Lifetap",
        14: "Pet",
        15: "Corpse",
        16: "Plant",
        17: "Uber Giants",
        18: "Uber Dragons",
        20: "Targeted Area of Effect Life Tap",
        24: "Area of Effect Undead",
        25: "Area of Effect Summoned",
        32: "Area of Effect Caster",
        33: "NPC Hate List",
        34: "Dungeon Object",
        35: "Muramite",
        36: "Area - PC Only",
        37: "Area - NPC Only",
        38: "Summoned Pet",
        39: "Group No Pets",
        40: "Area of EffectPC V2",
        41: "Group v2",
        42: "Self (Directional)",
        43: "Group With Pets",
        44: "Beam",
    }
    return target_type[value] if value in target_type else "Unknown"


@register.simple_tag
def define(value=None):
    return value


@register.filter(name='player_race')
def player_race(value):
    races = {
        0: "Unknown",
        1: "Human",
        2: "Barbarian",
        3: "Erudite",
        4: "Wood Elf",
        5: "High Elf",
        6: "Dark Elf",
        7: "Half Elf",
        8: "Dwarf",
        9: "Troll",
        10: "Ogre",
        11: "Halfling",
        12: "Gnome",
        13: "Iksar",
        14: "Vah Shir",
        128: "Iksar",
    }
    return races[value] if value in races else value


@register.filter(name='player_deity')
def player_deity(value):
    """
    Converts a deity id to a human-readable player deity name

    :param value: the deity id piped to the filter
    :return: a human-readable player deity name
    """
    deities = {
        140: "Agnostic",
        396: "Agnostic",  # Yes, the duplicate is intentional
        201: "Bertoxxulous",
        202: "Brell Serilis",
        203: "Cazic Thule",
        204: "Erollisi Marr",
        205: "Bristlebane",
        206: "Innoruuk",
        207: "Karana",
        208: "Mithaniel Marr",
        209: "Prexus",
        210: "Quellious",
        211: "Rallos Zek",
        212: "Rodcet Nife",
        213: "Solusek Ro",
        214: "The Tribunal",
        215: "Tunare",
        216: "Veeshan",
    }
    return deities[value] if value in deities else "Unknown"


@register.filter(name='player_skill')
def player_skill(value):
    """
    Converts a player skill id to a human-readable skill name
    :param value: player skill id
    :return: a human-readable player skill name
    """
    player_skills = {
        0: "1H Blunt",
        1: "1H Slashing",
        2: "2H Blunt",
        3: "2H Slashing",
        4: "Abjuration",
        5: "Alteration",
        6: "Apply Poison",
        7: "Archery",
        8: "Backstab",
        9: "Bind Wound",
        10: "Bash",
        11: "Block",
        12: "Brass Instruments",
        13: "Channeling",
        14: "Conjuration",
        15: "Defense",
        16: "Disarm",
        17: "Disarm Traps",
        18: "Divination",
        19: "Dodge",
        20: "Double Attack",
        21: "Dragon Punch / Tail Rake",
        22: "Dual Wield",
        23: "Eagle Strike",
        24: "Evocation",
        25: "Feign Death",
        26: "Flying Kick",
        27: "Forage",
        28: "Hand to Hand",
        29: "Hide",
        30: "Kick",
        31: "Meditate",
        32: "Mend",
        33: "Offense",
        34: "Parry",
        35: "Pick Lock",
        36: "1H Piercing",
        37: "Riposte",
        38: "Round Kick",
        39: "Safe Fall",
        40: "Sense Heading",
        41: "Singing",
        42: "Sneak",
        43: "Specialize Abjure",
        44: "Specialize Alteration",
        45: "Specialize Conjuration",
        46: "Specialize Divination",
        47: "Specialize Evocation",
        48: "Pick Pockets",
        49: "Stringed Instruments",
        50: "Swimming",
        51: "Throwing",
        52: "Tiger Claw",
        53: "Tracking",
        54: "Wind Instruments",
        55: "Fishing",
        56: "Make Poison",
        57: "Tinkering",
        58: "Research",
        59: "Alchemy",
        60: "Baking",
        61: "Tailoring",
        62: "Sense Traps",
        63: "Blacksmithing",
        64: "Fletching",
        65: "Brewing",
        66: "Alcohol Tolerance",
        67: "Begging",
        68: "Jewelrymaking",
        69: "Pottery",
        70: "Percussion Instruments",
        71: "Intimidation",
        72: "Berserking",
        73: "Taunt",
        74: "Count",
    }
    return player_skills[value] if value in player_skills else "Unknown " + str(value)


@register.filter(name='player_language')
def player_language(value):
    player_languages = {
        0: "Common Tongue",
        1: "Barbarian",
        2: "Erudian",
        3: "Elvish",
        4: "Dark Elvish",
        5: "Dwarvish",
        6: "Troll",
        7: "Ogre",
        8: "Gnomish",
        9: "Halfling",
        10: "Thieves Cant",
        11: "Old Erudian",
        12: "Elder Elvish",
        13: "Froglok",
        14: "Goblin",
        15: "Gnoll",
        16: "Combine Tongue",
        17: "Elder Teir`dal",
        18: "Lizardman",
        19: "Orcish",
        20: "Faerie",
        21: "Dragon",
        22: "Elder Dragon",
        23: "Dark Speech",
        24: "Vah Shir",
        25: "Unknown1",
        26: "Unknown2",
    }
    return player_languages[value] if value in player_languages else "Unknown" + str(value)


@register.filter(name='zone_filter')
def zone_filter(value, arg):
    """
    Converts a zone_id to a zone long name or short name

    :param value: The zone_id piped to the filter
    :param arg: "long" if the zone's long name is desired, defaults to the zone short name
    :return: a zone long name or short name
    """
    zones = {
        1: ("South Qeynos", "qeynos"),
        2: ("North Qeynos", "qeynos2"),
        3: ("The Surefall Glade", "qrg"),
        4: ("The Qeynos Hills", "qeytoqrg"),
        5: ("Highpass Hold", "highpass"),
        6: ("High Keep", "highkeep"),
        7: ("Unused", "Unused"),
        8: ("North Freeport", "freportn"),
        9: ("West Freeport", "freportw"),
        10: ("East Freeport", "freporte"),
        11: ("The Liberated Citadel of Runnyeye", "runneye"),
        12: ("The Western Plains of Karana", "qey2hh1"),
        13: ("The Northern Plains of Karana", "northkarana"),
        14: ("The Southern Plains of Karana", "southkarana"),
        15: ("Eastern Plains of Karana", "eastkarana"),
        16: ("Gorge of King Xorbb", "beholder"),
        17: ("Blackburrow", "blackburrow"),
        18: ("The Lair of the Splitpaw", "paw"),
        19: ("Rivervale", "rivervale"),
        20: ("Kithicor Forest", "kithicor"),
        21: ("West Commonlands", "commons"),
        22: ("East Commonlands", "ecommons"),
        23: ("The Erudin Palace", "erudint"),
        24: ("Erudin", "erudnext"),
        25: ("The Nektulos Forest", "nektulos"),
        26: ("Sunset Home", "cshome"),
        27: ("The Lavastorm Mountains", "lavastorm"),
        28: ("Nektropos", "nektropos"),
        29: ("Halas", "halas"),
        30: ("Everfrost Peaks", "everfrost"),
        31: ("Solusek's Eye", "soldunga"),
        32: ("Nagafen's Lair", "soldungb"),
        33: ("Misty Thicket", "misty"),
        34: ("Northern Desert of Ro", "nro"),
        35: ("Southern Desert of Ro", "sro"),
        36: ("Befallen", "befallen"),
        37: ("Oasis of Marr", "oasis"),
        38: ("Toxxulia Forest", "tox"),
        39: ("The Hole", "hole"),
        40: ("Neriak - Foreign Quarter", "neriaka"),
        41: ("Neriak - Commons", "neriakb"),
        42: ("Neriak - 3rd Gate", "neriakc"),
        43: ("Neriak Palace", "neriakd"),
        44: ("Najena", "najena"),
        45: ("The Qeynos Aqueduct System", "qcat"),
        46: ("Innothule Swamp", "innothule"),
        47: ("The Feerott", "feerott"),
        48: ("Accursed Temple of CazicThule", "cazicthule"),
        49: ("Oggok", "oggok"),
        50: ("The Rathe Mountains", "rathemtn"),
        51: ("Lake Rathetear", "lakerathe"),
        52: ("Grobb", "grobb"),
        53: ("Aviak Village", "aviak"),
        54: ("The Greater Faydark", "gfaydark"),
        55: ("Ak'Anon", "akanon"),
        56: ("Steamfont Mountains", "steamfont"),
        57: ("The Lesser Faydark", "lfaydark"),
        58: ("Crushbone", "crushbone"),
        59: ("The Castle of Mistmoore", "mistmoore"),
        60: ("South Kaladim", "kaladima"),
        61: ("Northern Felwithe", "felwithea"),
        62: ("Southern Felwithe", "felwitheb"),
        63: ("The Estate of Unrest", "unrest"),
        64: ("Kedge Keep", "kedge"),
        65: ("The City of Guk", "guktop"),
        66: ("The Ruins of Old Guk", "gukbuttom"),
        67: ("North Kaladim", "kaladimb"),
        68: ("Butcherblock Mountains", "butcher"),
        69: ("Ocean of Tears", "oot"),
        70: ("Dagnor's Cauldron", "cauldron"),
        71: ("The Plane of Sky", "airplane"),
        72: ("The Plane of Fear", "fearplane"),
        73: ("The Permafrost Caverns", "permafrost"),
        74: ("Kerra Isle", "kerraridge"),
        75: ("Paineel", "paineel"),
        76: ("Plane of Hate", "hateplane"),
        77: ("The Arena", "arena"),
        78: ("The Field of Bone", "fieldofbone"),
        79: ("The Warsliks Woods", "warslikswood"),
        80: ("The Temple of Solusek Ro", "soltemple"),
        81: ("The Temple of Droga", "droga"),
        82: ("Cabilis West", "cabwest"),
        83: ("The Swamp of No Hope", "swampofnohope"),
        84: ("Firiona Vie", "firiona"),
        85: ("Lake of Ill Omen", "lakeofillomen"),
        86: ("The Dreadlands", "dreadlands"),
        87: ("The Burning Wood", "burningwood"),
        88: ("Kaesora", "kaesora"),
        89: ("The Ruins of Sebilis", "sebilis"),
        90: ("The City of Mist", "citymist"),
        91: ("The Skyfire Mountains", "skyfire"),
        92: ("Frontier Mountains", "frontiermtns"),
        93: ("The Overthere", "overthere"),
        94: ("The Emerald Jungle", "emeraldjungle"),
        95: ("Trakanon's Teeth", "trakanon"),
        96: ("Timorous Deep", "timorous"),
        97: ("Kurn's Tower", "kurn"),
        98: ("Erud's Crossing", "erudsxing"),
        99: ("Unused", "unused"),
        100: ("The Stonebrunt Mountains", "stonebrunt"),
        101: ("The Warrens", "warrens"),
        102: ("Karnor's Castle", "karnor"),
        103: ("Chardok", "chardok"),
        104: ("The Crypt of Dalnir", "dalnir"),
        105: ("The Howling Stones", "charasis"),
        106: ("Cabilis East", "cabeast"),
        107: ("The Mines of Nurga", "nurga"),
        108: ("Veeshan's Peak", "veeshan"),
        109: ("Veksar", "veksar"),
    }
    if arg == "long":
        return zones[value][0] if value in zones else "Unknown"

    return zones[value][1] if value in zones else "Unknown"


@register.filter(name="datetime_delta")
def datetime_delta(value):
    return datetime.timedelta(seconds=value)


@register.filter(name="datetime_from_timestamp")
def datetime_delta(value):
    return datetime.datetime.fromtimestamp(value)


@register.filter(name='guild_rank')
def guild_rank_filter(value):
    guild_ranks = {
        0: "Member",
        1: "Officer",
        2: "Leader",
    }
    return guild_ranks[value] if value in guild_ranks else "Unknown"


@register.filter(name="expansion_icon")
def expansion_icon(value):
    expansion_icons = {
        0: "Original.gif",
        1: "Kunarkicon.gif",
        2: "Veliousicon.gif",
        3: "Luclinicon.gif",
        4: "Powericon.gif",
        5: "Ykeshaicon.gif",
        6: "Ldonicon.gif"
    }
    return expansion_icons[value] if value in expansion_icons else None


@register.filter(name="faction_level")
def faction_level(value):
    try:
        value = int(value)
    except ValueError:
        return None
    if value >= 2000:
        return "Max Ally"
    elif value >= 1100:
        return "Ally"
    elif 750 <= value <= 1099:
        return "Warmly"
    elif 500 <= value <= 749:
        return "Kindly"
    elif 100 <= value <= 499:
        return "Amiably"
    elif 0 <= value <= 99:
        return "Indifferently"
    elif -100 <= value <= -1:
        return "Apprehensively"
    elif -500 <= value <= -101:
        return "Dubiously"
    elif -750 <= value <= -501:
        return "Threateningly"
    elif -1999 <= value <= -500:
        return "Scowls"
    else:
        return "Max Scowls"
