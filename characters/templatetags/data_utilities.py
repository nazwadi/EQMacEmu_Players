import datetime
from django import template

register = template.Library()


@register.filter(name='clean_name')
def clean_name(value):
    """Remove underscores and prepended # from NPC names"""
    if value:
        value = value.replace('_', ' ')
        return value.replace('#', '')
    return value


@register.filter(name="can_bind_filter")
def can_bind(value):
    match value:
        case 0:
            return "No"
        case 1:
            return "Self"
        case 2:
            return "Others"
        case 3:
            return "Area"
        case _:
            return "Unknown"


@register.filter(name="zone_type_filter")
def zone_type_filter(value):
    match value:
        case 0:
            return "Unknown"
        case 1:
            return "Regular"
        case 2:
            return "Instanced"
        case 3:
            return "Hybrid"
        case 4:
            return "Instanced"
        case 5:
            return "Hybrid"
        case 6:
            return "Raid"
        case 7:
            return "City"
        case _:
            return "Unknown"


@register.filter(name='yes_no')
def yes_no(value):
    return "yes" if value == 1 else "no"


@register.filter(name='django_range')
def django_range(value=5):
    return range(1,value)


@register.filter(name='gender')
def gender_filter(value):
    match value:
        case 0:
            return "Male"
        case 1:
            return "Female"
        case 2:
            return "Neuter"
        case _:
            return "Unknown"


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
        258: "General 1, Slot 9 (Left)",
        259: "General 1, Slot 10 (Right)",
        260: "General 2, Slot 1 (Left)",
        261: "General 2, Slot 2 (Right)",
        262: "General 2, Slot 3 (Left)",
        263: "General 2, Slot 4 (Right)",
        264: "General 2, Slot 5 (Left)",
        265: "General 2, Slot 6 (Right)",
        266: "General 2, Slot 7 (Left)",
        267: "General 2, Slot 8 (Right)",
        268: "General 2, Slot 9 (Left)",
        269: "General 2, Slot 10 (Right)",
        270: "General 3, Slot 1 (Left)",
        271: "General 3, Slot 2 (Right)",
        272: "General 3, Slot 3 (Left)",
        273: "General 3, Slot 4 (Right)",
        274: "General 3, Slot 5 (Left)",
        275: "General 3, Slot 6 (Right)",
        276: "General 3, Slot 7 (Left)",
        277: "General 3, Slot 8 (Right)",
        278: "General 3, Slot 9 (Left)",
        279: "General 3, Slot 10 (Right)",
        280: "General 4, Slot 1 (Left)",
        281: "General 4, Slot 2 (Right)",
        282: "General 4, Slot 3 (Left)",
        283: "General 4, Slot 4 (Right)",
        284: "General 4, Slot 5 (Left)",
        285: "General 4, Slot 6 (Right)",
        286: "General 4, Slot 7 (Left)",
        287: "General 4, Slot 8 (Right)",
        288: "General 4, Slot 9 (Left)",
        289: "General 4, Slot 10 (Right)",
        290: "General 5, Slot 1 (Left)",
        291: "General 5, Slot 2 (Right)",
        292: "General 5, Slot 3 (Left)",
        293: "General 5, Slot 4 (Right)",
        294: "General 5, Slot 5 (Left)",
        295: "General 5, Slot 6 (Right)",
        296: "General 5, Slot 7 (Left)",
        297: "General 5, Slot 8 (Right)",
        298: "General 5, Slot 9 (Left)",
        299: "General 5, Slot 10 (Right)",
        300: "General 6, Slot 1 (Left)",
        301: "General 6, Slot 2 (Right)",
        302: "General 6, Slot 3 (Left)",
        303: "General 6, Slot 4 (Right)",
        304: "General 6, Slot 5 (Left)",
        305: "General 6, Slot 6 (Right)",
        306: "General 6, Slot 7 (Left)",
        307: "General 6, Slot 8 (Right)",
        308: "General 6, Slot 9 (Right)",
        309: "General 6, Slot 10 (Right)",
        310: "General 7, Slot 1 (Left)",
        311: "General 7, Slot 2 (Right)",
        312: "General 7, Slot 3 (Left)",
        313: "General 7, Slot 4 (Right)",
        314: "General 7, Slot 5 (Left)",
        315: "General 7, Slot 6 (Right)",
        316: "General 7, Slot 7 (Left)",
        317: "General 7, Slot 8 (Right)",
        318: "General 7, Slot 9 (Left)",
        319: "General 7, Slot 10 (Right)",
        320: "General 8, Slot 1 (Left)",
        321: "General 8, Slot 2 (Right)",
        322: "General 8, Slot 3 (Left)",
        323: "General 8, Slot 4 (Right)",
        324: "General 8, Slot 5 (Left)",
        325: "General 8, Slot 6 (Right)",
        326: "General 8, Slot 7 (Left)",
        327: "General 8, Slot 8 (Right)",
        328: "General 8, Slot 9 (Left)",
        329: "General 8, Slot 10 (Right)",
        2000: "Bank 1 (Left)",
        2001: "Bank 2 (Left)",
        2002: "Bank 3 (Left)",
        2003: "Bank 4 (Left)",
        2004: "Bank 5 (Right)",
        2005: "Bank 6 (Right)",
        2006: "Bank 7 (Right)",
        2007: "Bank 8 (Right)",
        2030: "Bank Bag 1, Slot 1 (Left)",
        2031: "Bank Bag 1, Slot 2 (Right)",
        2032: "Bank Bag 1, Slot 3 (Left)",
        2033: "Bank Bag 1, Slot 4 (Right)",
        2034: "Bank Bag 1, Slot 5 (Left)",
        2035: "Bank Bag 1, Slot 6 (Right)",
        2036: "Bank Bag 1, Slot 7 (Left)",
        2037: "Bank Bag 1, Slot 8 (Right)",
        2038: "Bank Bag 1, Slot 9 (Left)",
        2039: "Bank Bag 1, Slot 10 (Right)",
        2040: "Bank Bag 2, Slot 1 (Left)",
        2041: "Bank Bag 2, Slot 2 (Right)",
        2042: "Bank Bag 2, Slot 3 (Left)",
        2043: "Bank Bag 2, Slot 4 (Right)",
        2044: "Bank Bag 2, Slot 5 (Left)",
        2045: "Bank Bag 2, Slot 6 (Right)",
        2046: "Bank Bag 2, Slot 7 (Left)",
        2047: "Bank Bag 2, Slot 8 (Right)",
        2048: "Bank Bag 2, Slot 9 (Left)",
        2049: "Bank Bag 2, Slot 10 (Right)",
        2050: "Bank Bag 3, Slot 1 (Left)",
        2051: "Bank Bag 3, Slot 2 (Right)",
        2052: "Bank Bag 3, Slot 3 (Left)",
        2053: "Bank Bag 3, Slot 4 (Right)",
        2054: "Bank Bag 3, Slot 5 (Left)",
        2055: "Bank Bag 3, Slot 6 (Right)",
        2056: "Bank Bag 3, Slot 7 (Left)",
        2057: "Bank Bag 3, Slot 8 (Right)",
        2058: "Bank Bag 3, Slot 9 (Left)",
        2059: "Bank Bag 3, Slot 10 (Right)",
        2060: "Bank Bag 4, Slot 1 (Left)",
        2061: "Bank Bag 4, Slot 2 (Right)",
        2062: "Bank Bag 4, Slot 3 (Left)",
        2063: "Bank Bag 4, Slot 4 (Right)",
        2064: "Bank Bag 4, Slot 5 (Left)",
        2065: "Bank Bag 4, Slot 6 (Right)",
        2066: "Bank Bag 4, Slot 7 (Left)",
        2067: "Bank Bag 4, Slot 8 (Right)",
        2068: "Bank Bag 4, Slot 9 (Left)",
        2069: "Bank Bag 4, Slot 10 (Right)",
        2070: "Bank Bag 5, Slot 1 (Left)",
        2071: "Bank Bag 5, Slot 2 (Right)",
        2072: "Bank Bag 5, Slot 3 (Left)",
        2073: "Bank Bag 5, Slot 4 (Right)",
        2074: "Bank Bag 5, Slot 5 (Left)",
        2075: "Bank Bag 5, Slot 6 (Right)",
        2076: "Bank Bag 5, Slot 7 (Left)",
        2077: "Bank Bag 5, Slot 8 (Right)",
        2078: "Bank Bag 5, Slot 9 (Left)",
        2079: "Bank Bag 5, Slot 10 (Right)",
        2080: "Bank Bag 6, Slot 1 (Left)",
        2081: "Bank Bag 6, Slot 2 (Right)",
        2082: "Bank Bag 6, Slot 3 (Left)",
        2083: "Bank Bag 6, Slot 4 (Right)",
        2084: "Bank Bag 6, Slot 5 (Left)",
        2085: "Bank Bag 6, Slot 6 (Right)",
        2086: "Bank Bag 6, Slot 7 (Left)",
        2087: "Bank Bag 6, Slot 8 (Right)",
        2088: "Bank Bag 6, Slot 9 (Left)",
        2089: "Bank Bag 6, Slot 10 (Right)",
        2090: "Bank Bag 7, Slot 1 (Left)",
        2091: "Bank Bag 7, Slot 2 (Right)",
        2092: "Bank Bag 7, Slot 3 (Left)",
        2093: "Bank Bag 7, Slot 4 (Right)",
        2094: "Bank Bag 7, Slot 5 (Left)",
        2095: "Bank Bag 7, Slot 6 (Right)",
        2096: "Bank Bag 7, Slot 7 (Left)",
        2097: "Bank Bag 7, Slot 8 (Right)",
        2098: "Bank Bag 7, Slot 9 (Left)",
        2099: "Bank Bag 7, Slot 10 (Right)",
        2100: "Bank Bag 8, Slot 1 (Left)",
        2101: "Bank Bag 8, Slot 2 (Right)",
        2102: "Bank Bag 8, Slot 3 (Left)",
        2103: "Bank Bag 8, Slot 4 (Right)",
        2104: "Bank Bag 8, Slot 5 (Left)",
        2105: "Bank Bag 8, Slot 6 (Right)",
        2106: "Bank Bag 8, Slot 7 (Left)",
        2107: "Bank Bag 8, Slot 8 (Right)",
        2108: "Bank Bag 8, Slot 9 (Left)",
        2109: "Bank Bag 8, Slot 10 (Right)",
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


@register.filter(name='npc_class')
def npc_class(value):
    classes = {
        0: 'Soldier',
        1: 'Warrior',
        2: 'Cleric',
        3: 'Paladin',
        4: 'Ranger',
        5: 'Shadowknight',
        6: 'Druid',
        7: 'Monk',
        8: 'Bard',
        9: 'Rogue',
        10: 'Shaman',
        11: 'Necromancer',
        12: 'Wizard',
        13: 'Magician',
        14: 'Enchanter',
        15: 'Beastlord',
        16: 'Berserker',
        17: 'Banker',
        18: 'Unknown18',
        19: 'Unknown19',
        20: 'Warrior GM',
        21: 'Cleric GM',
        22: 'Paladin GM',
        23: 'Ranger GM',
        24: 'Shadowknight GM',
        25: 'Druid GM',
        26: 'Monk GM',
        27: 'Bard GM',
        28: 'Rogue GM',
        29: 'Shaman GM',
        30: 'Necromancer GM',
        31: 'Wizard GM',
        32: 'Magician GM',
        33: 'Enchanter GM',
        34: 'Beastlord GM',
        35: 'Berserker GM',
        36: 'Unknown36',
        37: 'Unknown37',
        38: 'Unknown38',
        39: 'Unknown39',
        40: 'Banker',
        41: 'Shopkeeper'
    }
    return classes[value] if value in classes else "Unknown"


@register.filter(name="npc_race")
def npc_race(value):
    races = {
        0: 'Doug',
        1: 'Human',
        2: 'Barbarian',
        3: 'Erudite',
        4: 'Wood Elf',
        5: 'High Elf',
        6: 'Dark Elf',
        7: 'Half Elf',
        8: 'Dwarf',
        9: 'Troll',
        10: 'Ogre',
        11: 'Halfling',
        12: 'Gnome',
        13: 'Aviak',
        14: 'Werewolf',
        15: 'Brownie',
        16: 'Centaur',
        17: 'Golem',
        18: 'Giant/Cyclops',
        19: 'Trakanon',
        20: 'Doppleganger',
        21: 'Evil Eye',
        22: 'Beetle',
        23: 'Kerran',
        24: 'Fish',
        25: 'Fairy',
        26: 'Froglok',
        27: 'Froglok Ghoul',
        28: 'Fungusman',
        29: 'Gargoyle',
        30: 'Gasbag',
        31: 'Gelatinous Cube',
        32: 'Ghost',
        33: 'Ghoul',
        34: 'Giant Bat',
        35: 'Giant Eel',
        36: 'Giant Rat',
        37: 'Giant Snake',
        38: 'Giant Spider',
        39: 'Gnoll',
        40: 'Goblin',
        41: 'Gorilla',
        42: 'Wolf',
        43: 'Bear',
        44: 'Freeport Guard',
        45: 'Demi Lich',
        46: 'Imp',
        47: 'Griffin',
        48: 'Kobold',
        49: 'Lava Dragon',
        50: 'Lion',
        51: 'Lizard Man',
        52: 'Mimic',
        53: 'Minotaur',
        54: 'Orc',
        55: 'Human Beggar',
        56: 'Pixie',
        57: 'Dracnid',
        58: 'Solusek Ro',
        59: 'Bloodgill',
        60: 'Skeleton',
        61: 'Shark',
        62: 'Tunare',
        63: 'Tiger',
        64: 'Treant',
        65: 'Vampire',
        66: 'Statue of Rallos Zek',
        67: 'Highpass Citizen',
        68: 'Tentacle',
        69: 'Wisp',
        70: 'Zombie',
        71: 'Qeynos Citizen',
        72: 'Ship',
        73: 'Launch',
        74: 'Piranha',
        75: 'Elemental',
        76: 'Puma',
        77: 'Neriak Citizen',
        78: 'Erudite Citizen',
        79: 'Bixie',
        80: 'Reanimated Hand',
        81: 'Rivervale Citizen',
        82: 'Scarecrow',
        83: 'Skunk',
        84: 'Snake Elemental',
        85: 'Spectre',
        86: 'Sphinx',
        87: 'Armadillo',
        88: 'Clockwork Gnome',
        89: 'Drake',
        90: 'Halas Citizen',
        91: 'Alligator',
        92: 'Grobb Citizen',
        93: 'Oggok Citizen',
        94: 'Kaladim Citizen',
        95: 'Cazic Thule',
        96: 'Cockatrice',
        97: 'Daisy Man',
        98: 'Elf Vampire',
        99: 'Denizen',
        100: 'Dervish',
        101: 'Efreeti',
        102: 'Froglok Tadpole',
        103: 'Phinigel Autropos',
        104: 'Leech',
        105: 'Swordfish',
        106: 'Felguard',
        107: 'Mammoth',
        108: 'Eye of Zomm',
        109: 'Wasp',
        110: 'Mermaid',
        111: 'Harpie',
        112: 'Fayguard',
        113: 'Drixie',
        114: 'Ghost Ship',
        115: 'Clam',
        116: 'Sea Horse',
        117: 'Dwarf Ghost',
        118: 'Erudite Ghost',
        119: 'Sabertooth',
        120: 'Wolf Elemental',
        121: 'Gorgon',
        122: 'Dragon Skeleton',
        123: 'Innoruuk',
        124: 'Unicorn',
        125: 'Pegasus',
        126: 'Djinn',
        127: 'Invisible Man',
        128: 'Iksar',
        129: 'Scorpion',
        130: 'Vah Shir',
        131: 'Sarnak',
        132: 'Draglock',
        133: 'Lycanthrope',
        134: 'Mosquito',
        135: 'Rhino',
        136: 'Xalgoz',
        137: 'Kunark Goblin',
        138: 'Yeti',
        139: 'Iksar Citizen',
        140: 'Forest Giant',
        141: 'Boat',
        142: 'Minor Illusion',
        143: 'Tree Illusion',
        144: 'Burynai',
        145: 'Goo',
        146: 'Spectral Sarnak',
        147: 'Spectral Iksar',
        148: 'Kunark Fish',
        149: 'Iksar Scorpion',
        150: 'Erollisi',
        151: 'Tribunal',
        152: 'Bertoxxulous',
        153: 'Bristlebane',
        154: 'Fay Drake',
        155: 'Sarnak Skeleton',
        156: 'Ratman',
        157: 'Wyvern',
        158: 'Wurm',
        159: 'Devourer',
        160: 'Iksar Golem',
        161: 'Iksar Skeleton',
        162: 'Man Eating Plant',
        163: 'Raptor',
        164: 'Sarnak Golem',
        165: 'Water Dragon',
        166: 'Iksar Hand',
        167: 'Succulent',
        168: 'Holgresh',
        169: 'Brontotherium',
        170: 'Snow Dervish',
        171: 'Dire Wolf',
        172: 'Manticore',
        173: 'Totem',
        174: 'Cold Spectre',
        175: 'Enchanted Armor',
        176: 'Snow Bunny',
        177: 'Walrus',
        178: 'Rock-gem Man',
        179: 'Unknown179',
        180: 'Unknown180',
        181: 'Yak Man',
        182: 'Faun',
        183: 'Coldain',
        184: 'Velious Dragon',
        185: 'Hag',
        186: 'Hippogriff',
        187: 'Siren',
        188: 'Frost Giant',
        189: 'Storm Giant',
        190: 'Otterman',
        191: 'Walrus Man',
        192: 'Clockwork Dragon',
        193: 'Abhorrent',
        194: 'Sea Turtle',
        195: 'Black and White Dragon',
        196: 'Ghost Dragon',
        197: 'Ronnie Test',
        198: 'Prismatic Dragon',
        199: 'Shiknar',
        200: 'Rockhopper',
        201: 'Underbulk',
        202: 'Grimling',
        203: 'Vacuum Worm',
        204: 'Evan Test',
        205: 'Kahli Shah',
        206: 'Owlbear',
        207: 'Rhino Beetle',
        208: 'Vampyre',
        209: 'Earth Elemental',
        210: 'Air Elemental',
        211: 'Water Elemental',
        212: 'Fire Elemental',
        213: 'Wetfang Minnow',
        214: 'Thought Horror',
        215: 'Tegi',
        216: 'Horse',
        217: 'Shissar',
        218: 'Fungal Fiend',
        219: 'Vampire Volatalis',
        220: 'StoneGrabber',
        221: 'Scarlet Cheetah',
        222: 'Zelniak',
        223: 'Lightcrawler',
        224: 'Shade',
        225: 'Sunflower',
        226: 'Khati Sha',
        227: 'Shrieker',
        228: 'Galorian',
        229: 'Netherbian',
        230: 'Akhevan',
        231: 'Spire Spirit',
        232: 'Sonic Wolf',
        233: 'Ground Shaker',
        234: 'Vah Shir Skeleton',
        235: 'Mutant Humanoid',
        236: 'Lord Inquisitor Seru',
        237: 'Recuso',
        238: 'Vah Shir King',
        239: 'Vah Shir Guard',
        240: 'Teleport Man',
        241: 'Lujein',
        242: 'Naiad',
        243: 'Nymph',
        244: 'Ent',
        245: 'Wrinnfly',
        246: 'Coirnav',
        247: 'Solusek Ro',
        248: 'Clockwork Golem',
        249: 'Clockwork Brain',
        250: 'Spectral Banshee',
        251: 'Guard of Justice',
        252: 'PoM Castle',
        253: 'Disease Boss',
        254: 'Solusek Ro Guard',
        255: 'Bertoxxulous (New)',
        256: 'Tribunal (New)',
        257: 'Terris Thule',
        258: 'Vegerog',
        259: 'Crocodile',
        260: 'Bat',
        261: 'Slarghilug',
        262: 'Tranquilion',
        263: 'Tin Soldier',
        264: 'Nightmare Wraith',
        265: 'Malarian',
        266: 'Knight of Pestilence',
        267: 'Lepertoloth',
        268: 'Bubonian Boss',
        269: 'Bubonian Underling',
        270: 'Pusling',
        271: 'Water Mephit',
        272: 'Stormrider',
        273: 'Junk Beast',
        274: 'Broken Clockwork',
        275: 'Giant Clockwork',
        276: 'Clockwork Beetle',
        277: 'Nightmare Goblin',
        278: 'Karana',
        279: 'Blood Raven',
        280: 'Nightmare Gargoyle',
        281: 'Mouth of Insanity',
        282: 'Skeletal Horse',
        283: 'Saryrn',
        284: 'Fennin Ro',
        285: 'Tormentor',
        286: 'Necromancer Priest',
        287: 'Nightmare',
        288: 'New Rallos Zek',
        289: 'Vallon Zek',
        290: 'Tallon Zek',
        291: 'Air Mephit',
        292: 'Earth Mephit',
        293: 'Fire Mephit',
        294: 'Nightmare Mephit',
        295: 'Zebuxoruk',
        296: 'Mithaniel Marr',
        297: 'Knightmare Rider',
        298: 'Rathe Councilman',
        299: 'Xegony',
        300: 'Demon/Fiend',
        301: 'Test Object',
        302: 'Lobster Monster',
        303: 'Phoenix',
        304: 'Quarm',
        305: 'New Bear',
        306: 'Earth Golem',
        307: 'Iron Golem',
        308: 'Storm Golem',
        309: 'Air Golem',
        310: 'Wood Golem',
        311: 'Fire Golem',
        312: 'Water Golem',
        313: 'Veiled Gargoyle',
        314: 'Lynx',
        315: 'Squid',
        316: 'Frog',
        317: 'Flying Serpent',
        318: 'Tactics Soldier',
        319: 'Armored Boar',
        320: 'Djinni',
        321: 'Boar',
        322: 'Knight of Marr',
        323: 'Armor of Marr',
        324: 'Nightmare Knight',
        325: 'Rallos Ogre',
        326: 'Arachnid',
        327: 'Crystal Arachnid',
        328: 'Tower Model',
        329: 'Portal'
    }
    return races[value] if value in races else value


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


@register.filter(name='zone_short_to_long')
def zone_short_to_long(value):
    zones = {
        "qeynos": "South Qeynos",
        "qeynos2": "North Qeynos",
        "qrg": "The Surefall Glade",
        "qeytoqrg": "The Qeynos Hills",
        "highpass": "Highpass Hold",
        "highkeep": "High Keep",
        "Unused": "Unused",
        "freportn": "North Freeport",
        "freportw": "West Freeport",
        "freporte": "East Freeport",
        "runnyeye": "The Liberated Citadel of Runnyeye",
        "qey2hh1": "The Western Plains of Karana",
        "northkarana": "The Northern Plains of Karana",
        "southkarana": "The Southern Plains of Karana",
        "eastkarana": "Eastern Plains of Karana",
        "beholder": "Gorge of King Xorbb",
        "blackburrow": "Blackburrow",
        "paw": "The Lair of the Splitpaw",
        "rivervale": "Rivervale",
        "kithicor": "Kithicor Forest",
        "commons": "West Commonlands",
        "ecommons": "East Commonlands",
        "erudnint": "The Erudin Palace",
        "erudnext": "Erudin",
        "nektulos": "The Nektulos Forest",
        "cshome": "Sunset Home",
        "lavastorm": "The Lavastorm Mountains",
        "nektropos": "Nektropos",
        "halas": "Halas",
        "everfrost": "Everfrost Peaks",
        "soldunga": "Solusek's Eye",
        "soldungb": "Nagafen's Lair",
        "misty": "Misty Thicket",
        "nro": "Northern Desert of Ro",
        "sro": "Southern Desert of Ro",
        "befallen": "Befallen",
        "oasis": "Oasis of Marr",
        "tox": "Toxxulia Forest",
        "hole": "The Hole",
        "neriaka": "Neriak - Foreign Quarter",
        "neriakb": "Neriak - Commons",
        "neriakc": "Neriak - 3rd Gate",
        "neriakd": "Neriak Palace",
        "najena": "Najena",
        "qcat": "The Qeynos Aqueduct System",
        "innothule": "Innothule Swamp",
        "feerrott": "The Feerott",
        "cazicthule": "Accursed Temple of CazicThule",
        "oggok": "Oggok",
        "rathemtn": "The Rathe Mountains",
        "lakerathe": "Lake Rathetear",
        "grobb": "Grobb",
        "aviak": "Aviak Village",
        "gfaydark": "The Greater Faydark",
        "akanon": "Ak'Anon",
        "steamfont": "Steamfont Mountains",
        "lfaydark": "The Lesser Faydark",
        "crushbone": "Crushbone",
        "mistmoore": "The Castle of Mistmoore",
        "kaladima": "South Kaladim",
        "felwithea": "Northern Felwithe",
        "felwitheb": "Southern Felwithe",
        "unrest": "The Estate of Unrest",
        "kedge": "Kedge Keep",
        "guktop": "The City of Guk",
        "gukbottom": "The Ruins of Old Guk",
        "kaladimb": "North Kaladim",
        "butcher": "Butcherblock Mountains",
        "oot": "Ocean of Tears",
        "cauldron": "Dagnor's Cauldron",
        "airplane": "The Plane of Sky",
        "fearplane": "The Plane of Fear",
        "permafrost": "The Permafrost Caverns",
        "kerraridge": "Kerra Isle",
        "paineel": "Paineel",
        "hateplane": "Plane of Hate",
        "arena": "The Arena",
        "fieldofbone": "The Field of Bone",
        "warslikswood": "The Warsliks Woods",
        "soltemple": "The Temple of Solusek Ro",
        "droga": "The Temple of Droga",
        "cabwest": "Cabilis West",
        "swampofnohope": "The Swamp of No Hope",
        "firiona": "Firiona Vie",
        "lakeofillomen": "Lake of Ill Omen",
        "dreadlands": "The Dreadlands",
        "burningwood": "The Burning Wood",
        "kaesora": "Kaesora",
        "sebilis": "The Ruins of Sebilis",
        "citymist": "The City of Mist",
        "skyfire": "The Skyfire Mountains",
        "frontiermtns": "Frontier Mountains",
        "overthere": "The Overthere",
        "emeraldjungle": "The Emerald Jungle",
        "trakanon": "Trakanon's Teeth",
        "timorous": "Timorous Deep",
        "kurn": "Kurn's Tower",
        "erudsxing": "Erud's Crossing",
        "unused": "Unused",
        "stonebrunt": "The Stonebrunt Mountains",
        "warrens": "The Warrens",
        "karnor": "Karnor's Castle",
        "chardok": "Chardok",
        "dalnir": "The Crypt of Dalnir",
        "charasis": "The Howling Stones",
        "cabeast": "Cabilis East",
        "nurga": "The Mines of Nurga",
        "veeshan": "Veeshan's Peak",
        "veksar": "Veksar",
    }
    return zones[value] if value in zones else "Unknown" + str(value)


@register.filter(name='zone_filter')
def zone_filter(value, arg):
    """
    Converts a zone_id to a zones long name or short name

    :param value: The zone_id piped to the filter
    :param arg: "long" if the zones's long name is desired, defaults to the zones short name
    :return: a zones long name or short name
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
    return datetime.timedelta(seconds=value) if value else value


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
        -1: "Any",
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


@register.filter(name="npc_special_ability")
def npc_special_ability(values):
    npc_special_abilities = {
        0: 'None',
        1: 'Summon',
        2: 'Enrage',
        3: 'Rampage',
        4: 'Area Rampage',
        5: 'Flurry',
        6: 'Triple Attack',
        7: 'Quad Attack',
        8: 'Dual Wield',
        9: 'Bane Attack',
        10: 'Magical Attack',
        11: 'Ranged Attack',
        12: 'Unslowable',
        13: 'Unmezable',
        14: 'Uncharmable',
        15: 'Unstunable',
        16: 'Unsnareable',
        17: 'Unfearable',
        18: 'Immune to Dispell',
        19: 'Immune to Melee',
        20: 'Immune to Magic',
        21: 'Immune to Fleeing',
        22: 'Immune to Non-Bane Damage',
        23: 'Immune to Non-Magical Damage',
        24: 'Will Not Aggro',
        25: 'Immune to Aggro',
        26: 'Resist Ranged Spells',
        27: 'See through Feign Death',
        28: 'Immune to Taunt',
        29: 'Tunnel Vision',
        30: 'Does NOT buff/heal friends',
        31: 'Unpacifiable',
        32: 'Leashed',
        33: 'Tethered',
        34: 'Destructible Object',
        35: 'No Harm from Players',
        36: 'Always Flee',
        37: 'Flee Percentage',
        38: 'Allow Beneficial',
        39: 'Disable Melee',
        40: 'Chase Distance',
        41: 'Allow Tank',
        42: 'Ignore Root Aggro',
        43: 'Casting Resist Diff',
        44: 'Counter Avoid Damage',
        45: 'Proximity Aggro',
        46: 'Immune Ranged Attacks',
        47: 'Immune Client Damage',
        48: 'Immune NPC Damage',
        49: 'Immune Client Aggro',
        50: 'Immune NPC Aggro'
    }

    result = list()
    abilities = values.split('^')
    for ability in abilities:
        codes = ability.split(',')
        try:
            ability_code = codes[0].strip()
            result.append(npc_special_abilities[int(ability_code)])
        except (IndexError, ValueError) as e:
            print(e, ability)
            continue
    return ', '.join(result)


@register.filter(name="multiply")
def multiply(value, arg):
    return value * arg
