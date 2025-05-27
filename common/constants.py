from enum import Enum


class SE(Enum):
    Hitpoints = 0
    AC = 1
    ATK = 2
    Movement_Speed = 3
    STR = 4
    DEX = 5
    AGI = 6
    STA = 7
    INT = 8
    WIS = 9
    CHA = 10  # usd as a spacer
    Attack_Speed = 11
    Invisibility = 12
    See_Invisibility = 13
    Water_Breathing = 14
    Current_Mana = 15
    NPC_Frenzy = 16  # Not used
    NPC_Awareness = 17
    Lull = 18  # Reaction Radius
    Add_Faction = 19  # Alliance line
    Blind = 20
    Stun = 21
    Charm = 22
    Fear = 23
    Stamina = 24  # Invigor and such
    Bind_Affinity = 25
    Gate = 26
    Cancel_Magic = 27
    Invisibility_Vs_Undead = 28
    Invisibility_Vs_Animals = 29
    Change_Frenzy_Radius = 30  # Pacify
    Mesmerize = 31
    Summon_Item = 32
    Summon_Pet = 33
    Confuse = 34  # Not used
    Disease_Counter = 35
    Poison_Counter = 36
    Detect_Hostile = 37  # Not used
    Detect_Magic = 38  # Not used
    Detect_Poison = 39  # Not used
    Divine_Aura = 40
    Destroy_Target = 41  # Disintegrate
    Shadow_Step = 42
    Berserk = 43  # not used in any known live spell
    Lycanthropy = 44
    Vampirism = 45  # not used in any known live spell
    Resist_Fire = 46
    Resist_Cold = 47
    Resist_Poison = 48
    Resist_Disease = 49
    Resist_Magic = 50
    Detect_Traps = 51  # Not used
    Sense_Dead = 52
    Sense_Summoned = 53
    Sense_Animals = 54
    Rune = 55
    True_North = 56
    Levitate = 57
    Illusion = 58
    Damage_Shield = 59
    Transfer_Item = 60  # Not used
    Identify = 61
    Item_ID = 62  # Not used
    Wipe_Hate_List = 63
    Spin_Target = 64
    Infra_Vision = 65
    Ultra_Vision = 66
    Eye_of_Zomm = 67
    Reclaim_Pet = 68
    Total_HP = 69
    Corpose_Bomb = 70  # Not used
    Necro_Pet = 71
    Preserve_Corpse = 72  # Not used
    Bind_Sight = 73
    Feign_Death = 74
    Voice_Graft = 75
    Sentinel = 76
    Locate_Corpse = 77
    Absorb_Magic_Attack = 78
    Current_HP_Once = 79  # heals and nukes, non-repeating if in buff
    Enchant_Light = 80  # not used
    Revive = 81  # rez
    Summon_PC = 82
    Teleport = 83
    Toss_Up = 84  # Gravity Flux
    Weapon_Proc = 85  # i.e. Call of Fire
    Harmony = 86
    Magnify_Vision = 87
    Succor = 88
    Model_Size = 89  # shrink/grow
    Cloak = 90  # not implemented
    Summon_Corpse = 91
    Instant_Hate = 92  # add hate
    Stop_Rain = 93  # wake of karana
    Negate_If_Combat = 94
    Sacrifice = 95
    Silence = 96
    Mana_Pool = 97
    Attack_Speed_2 = 98  # Melody of Ervaj
    Root = 99
    Heal_Over_Time = 100
    Complete_Heal = 101
    Fearless = 102  # valiant companion
    Call_Pet = 103  # summon companion
    Translocate = 104
    Anti_Gate = 105  # translocational anchor
    Summon_BST_Pet = 106
    Alter_NPC_Level = 107
    Familiar = 108
    Summmon_Item_Into_Bag = 109
    Increase_Archery = 110
    Resist_All = 111
    Casting_Level = 112
    Summon_Horse = 113
    Change_Aggro = 114
    Hunger = 115
    Curse_Counter = 116
    Magic_Weapon = 117
    Amplification = 118
    Attack_Speed_3 = 119
    Heal_Rate = 120  # reduces healing by a %
    Reverse_Damage_Shield = 121
    Reduce_Skill = 122  # Not used
    Screech = 123
    Improved_Damage = 124
    Improved_Heal = 125
    Spell_Resist_Reduction = 126
    Increase_Spell_Haste = 127
    Increase_Spell_Duration = 128
    Increase_Range = 129
    Spell_Hate_Mod = 130
    Reduce_Reagent_Cost = 131
    Reduce_Mana_Cost = 132
    Stun_Time_Modifier = 133
    Limit_Max_Level = 134
    Limit_Resist = 135
    Limit_Target = 136
    Limit_Effect = 137
    Limit_Spell_Type = 138
    Limit_Spell = 139
    Limit_Minimum_Duration = 140
    Limit_Instant = 141
    Limit_Minimum_Level = 142
    Limit_Cast_Time_Minimum = 143
    Limit_Cast_Time_Maximum = 144
    Teleport_2 = 145  # Banishment of the Pantheon
    Electricity_Resist = 146  # Not implemented, Lightning Rod
    Percental_Heal = 147
    Stacking_Command_Block = 148
    Stacking_Command_Overwrite = 149
    Death_Save = 150
    Suspend_Pet = 151
    Temporary_Pets = 152
    Balance_HP = 153
    Dispel_Detrimental = 154
    Spell_Crit_Damage_Increase = 155
    Illusion_Copy = 156  # Deception
    Spell_Damage_Shield = 157  # Petrad's Protection
    Reflect = 158
    All_Stats = 159
    Make_Drunk = 160  # Not implemented
    Mitigate_Spell_Damage = 161
    Mitigate_Melee_Damage = 162
    Negate_Attacks = 163
    Pet_Power_Increase = 167
    Melee_Mitigation = 168
    Critical_Hit_Chance = 169
    Spell_Crit_Chance = 170
    Crippling_Blow_Chance = 171
    Avoid_Melee_Chance = 172
    Riposte_Chance = 173
    Dodge_Chance = 174
    Parry_Chance = 175
    Dual_Wield_Chance = 176
    Double_Attack_Chance = 177
    Melee_Lifetap = 178
    All_Instrument_Mod = 179
    Resist_Spell_Chance = 180
    Resist_Fear_Chance = 181
    Hundred_Hands = 182
    Melee_Skill_Check = 183
    Hit_Chance = 184
    Damage_Modifier = 185
    Minimum_Damage_Modifier = 186
    Balance_Mana = 187
    Increase_Block_Chance = 188
    Current_Endurance = 189
    Endurance_Pool = 190
    Amnesia = 191  # Silence vs Melee Effect
    Hate = 192
    Skill_Attack = 193
    Fading_Memories = 194
    Stun_Resist = 195
    Strike_Through = 196
    Skill_Damage_Taken = 197
    Current_Endurance_Once = 198
    Taunt = 199  # percent chance to taunt the target
    Proc_Chance = 200
    Ranged_Proc = 201
    Illusion_Other = 202  # Project illusion
    Mass_Group_Buff = 203
    Group_Fear_Immunity = 204  # not used, AA action instead
    Rampage = 205
    AE_Taunt = 206
    Dispel_Beneficial = 209
    AE_Melee = 211
    Frenzied_Devastation = 212
    Pet_Max_HP = 213
    Max_HP_Change = 214
    Pet_Avoidance = 215
    Accuracy = 216
    Head_Shot = 217
    Pet_Critical_Hit = 218
    Slay_Undead = 219
    Skill_Damage_Amount = 220  # out of era
    Packrat = 221  # not used by our client
    Block_Behind = 222  # out of era, GoD AA
    Double_Riposte = 223
    Give_Double_Riposte = 224  # AA
    Give_Double_Attack = 225  # AA
    Two_Hand_Bash = 226
    Reduce_Skill_Timer = 227
    Persistent_Casting = 229
    Stun_Bash_Chance = 231
    Divine_Save = 232
    Metabolism = 233  # Food/Drink consumption rates
    Channel_Chance_Spells = 235
    Give_Pet_Group_Target = 237
    Illusion_Persistence = 238
    Improved_Reclaim_Energy = 241
    Increase_Chance_Memwipe = 242
    Charm_Break_Chance = 243
    Root_Break_Chance = 244
    Set_Breath_Level = 246
    Raise_Skill_Cap = 247
    Secondary_Damage_Increase = 249  # Off-hand weapon damage bonus
    Spell_Proc_Chance = 250
    Consume_Projectile = 251  # Chance not consume arrow
    Frontal_Backstab_Chance = 252
    Frontal_Backstab_Min_Damage = 253
    Blank = 254
    Triple_Backstab = 258
    Combat_Stability = 259
    Add_Singing_Modifier = 260
    Song_Modifier_Cap = 261
    Raise_Stat_Cap = 262
    Mastery_Of_Past = 265
    Extra_Attack_Chance = 266
    Pet_Discipline_2 = 267
    Max_Bind_Wound = 269
    Bard_Song_Range = 270
    Base_Movement_Speed = 271
    Casting_Level_2 = 272
    Critical_DoT_Chance = 273
    Critical_Heal_Chance = 274
    Critical_Mend_Chance = 275
    Ambidexterity = 276
    Unfailing_Divinity = 277
    Finishing_Blow = 278
    Flurry = 279
    Pet_Flurry = 280
    Improved_Bind_Wound = 282
    Double_Special_Attack = 283
    Focus_Damage_Amount = 286
    Spell_Duration_Increase_By_Tick = 287
    Special_Attack_KB_Proc = 288  # not really used
    Cast_On_Fade_Effect = 289
    Increase_Run_Speed_Cap = 290
    Purify = 291
    Strike_Through_2 = 292
    Frontal_Stun_Resist = 293
    Critical_Spell_Chance = 294
    Focus_Spell_Vulnerability = 296
    Focus_Damage_Amount_Incoming = 297
    Change_Height = 298
    Wake_The_Dead = 299
    Doppelganger = 300
    Archery_Damage_Modifier = 301
    Focus_Damage_Percent_Crit = 302
    Focus_Damage_Amount_Crit = 303
    Offhand_Riposte_Fail = 304
    Mitigate_Damage_Shield = 305
    Suspend_Minion = 308
    Gate_Casters_Bind_Point = 309
    Reduce_Reuse_Timer = 310
    Limit_Combat_Skills = 311
    Shield_Block = 320
    Head_Shot_Level = 346
    Limit_Spell_Group = 385
    Finishing_Blow_Level = 440


PLAYER_CLASSES = {
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

PLAYER_RACES = {
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

# id: [race, mod]
PLAYER_RACIAL_EXP_MODIFIERS = {
    1: ["Human", 100],
    2: ["Barbarian", 105],
    4: ["Erudite", 100],
    8: ["Wood Elf", 100],
    16: ["High Elf", 100],
    32: ["Dark Elf", 100],
    64: ["Half Elf", 100],
    128: ["Dwarf", 100],
    256: ["Troll", 120],
    512: ["Ogre", 115],
    1024: ["Halfling", 95],
    2048: ["Gnome", 100],
    4096: ["Iksar", 120],
    8192: ["Vah Shir", 100]
}

PLAYER_DEITIES = {
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

PLAYER_LANGUAGES = {
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

RACES = {
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

PET_CLASSES = {
    2: "Cleric",
    5: "Shadow Knight",
    6: "Druid",
    10: "Shaman",
    11: "Necromancer",
    12: "Wizard",
    13: "Magician",
    14: "Enchanter",
    15: "Beastlord"
}

EQUIPMENT_SLOTS = {
    #    1: "Cursor",
    # 2: "Ear01",
    4: "Head",
    8: "Face",
    # 16: "Ear02",
    18: "Ears",
    32: "Neck",
    64: "Shoulders",
    128: "Arms",
    256: "Back",
    # 512: "Bracer01",
    # 1024: "Bracer02",
    1536: "Wrists",
    2048: "Range",
    4096: "Hands",
    8192: "Primary",
    16384: "Secondary",
    # 32768: "Ring01",
    # 65536: "Ring02",
    98304: "Fingers",
    131072: "Chest",
    262144: "Legs",
    524288: "Feet",
    1048576: "Waist",
    2097152: "Ammo",
}

ITEM_TYPES = {
    0: "1HS",
    1: "2HS",
    2: "Piercing",
    3: "1HB",
    4: "2HB",
    5: "Archery",
    # 6: "Unknown",
    7: "Throwing range items",
    8: "Shield",
    # 9: "Unknown",
    10: "Armor",
    11: "Gems",
    12: "Lock picks",
    # 13: "Unknown",
    14: "Food",
    15: "Drink",
    16: "Light",
    17: "Combinable",
    18: "Bandages",
    19: "Throwing",
    20: "Scroll",
    21: "Potion",
    # 22: "Unknown",
    23: "Wind Instrument",
    24: "Stringed Instrument",
    25: "Brass Instrument",
    26: "Percussion Instrument",
    27: "Arrow",
    # 28: "Unknown",
    29: "Jewelry",
    30: "Skull",
    31: "Tome",
    32: "Note",
    33: "Key",
    34: "Coin",
    35: "2H Piercing",
    36: "Fishing Pole",
    37: "Fishing Bait",
    38: "Alcohol",
    39: "Key (bis)",
    40: "Compass",
    # 41: "Unknown",
    42: "Poison",
    # 43: "Unknown",
    # 44: "Unknown",
    45: "Martial",
    # 46: "Unknown",
    # 47: "Unknown",
    # 48: "Unknown",
    # 49: "Unknown",
    # 50: "Unknown",
    # 51: "Unknown",
    52: "Charm",
    # 53: "Unknown",
    54: "Augmentation",
}

ITEM_STATS = {
    "hp": "Hit Points",
    "mana": "Mana",
    "ac": "AC",
    "attack": "Attack",
    "aagi": "Agility",
    "acha": "Charisma",
    "adex": "Dexterity",
    "aint": "Intelligence",
    "asta": "Stamina",
    "astr": "Strength",
    "awis": "Wisdom",
    "damage": "Damage",
    "delay": "Delay",
}

BODY_TYPES = {
    1: "Humanoid",
    2: "Lycanthrope",
    3: "Undead",
    4: "Giant",
    5: "Construct",
    6: "Extraplanar",
    7: "Magical",
    8: "SummonedUndead",
    9: "BaneGiant",
    10: "Dain",
    11: "NoTarget",
    12: "Vampire",
    13: "Atenha Ra",
    14: "Greater Akheva",
    15: "Khati Sha",
    16: "Seru",
    17: "Grieg Veneficus",
    18: "Draz Nurakk",
    19: "Zek",
    20: "Luggald",
    21: "Animal",
    22: "Insect",
    23: "Monster",
    24: "Summoned",
    25: "Plant",
    26: "Dragon",
    27: "Summoned2",
    28: "Summoned3",
    29: "Dragon2",
    30: "VeliousDragon",
    31: "Familiar",
    32: "Dragon3",
    33: "Boxes",
    34: "Muramite",
    60: "NoTarget2",
    63: "SwarmPet",
    64: "MonsterSummon",
}

CONTAINER_TYPES = {
    1 : "Just a Bag",
    2 : "Quiver",
    3 : "Pouch",
    4 : "Pouch",
    5 : "Backpack",
    6 : "Tupperware",
    7 : "Box",
    8 : "Bandolier",
    9 : "Alchemy",
    10 : "Tinkering",
    11 : "Research",
    12 : "Poison making",
    13 : "Special quests",
    14 : "Baking",
    15 : "Baking",
    16 : "Tailoring",
    18 : "Fletching",
    19 : "Brewing",
    20 : "Jewelry",
    24 : "Wizard Research",
    25 : "Mage Research",
    26 : "Necro Research",
    27 : "Enchanter Research",
    28 : "Plat Storage",
    29 : "Practice Research",
    30 : "Pottery",
    41 : "Tailoring",
    42 : "Tailoring",
    43 : "Tailoring",
    44 : "Fletching",
    46 : "Fishing",
    51 : "Bazaar",
}

ZONE_SHORT_TO_LONG = {
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
    "grimling": "The Grimling Forest",
    "griegsend": "Grieg's End",
    "hollowshade": "Hollowshade Moor",
    "nexus": "The Nexus",
    "twilight": "Twilight Sea",
    "dawnshroud": "Dawnshroud",
    "poknowledge": "Plane of Knowledge",
    "iceclad": "Iceclad Ocean",
    "greatdivide": "The Great Divide",
    "velketor": "Velketor's Labryninth",
    "wakening": "The Wakening Lands",
    "cobaltscar": "Cobalt Scar",
    "eastwastes": "Eastern Wastes",
    "westwastes": "Western Wastes",
    "crystal": "Crystal Caverns",
    "kael": "Kael Drakkel",
    "thurgadina": "The City of Thurgadin",
    "thurgadinb": "Icewell Keep",
    "skyshrine": "Skyshrine",
    "necropolis": "Dragon Necropolis",
    "sirens": "Siren's Grotto",
    "sleeper": "Sleeper's Tomb",
    "templeveeshan": "Temple of Veeshan",
    "mischiefplane": "Plane of Mischief",
    "growthplane": "Plane of Growth",
    "frozenshadow": "Tower of Frozen Shadow",
    "acrylia": "Acrylia Caverns",
    "erudsxing2": "Marauder's Mire",
    "shadowhaven": "Shadow Haven",
    "bazaar": "The Bazaar",
    "jaggedpine": "Jaggedpine Forest",
    "maiden": "Maiden's Eye",
    "mseru": "Marus Seru",
    "sseru": "Sanctus Seru",
    "letalis": "Mons Letalis",
    "scarlet": "Scarlet Desert",
    "shadeweaver": "Shadeweaver's Thicket",
    "tenebrous": "The Tenebrous Mountains",
    "thegrey": "The Grey",
    "umbral": "The Umbral Plains",
    "katta": "Katta Castellum",
    "sharvahl": "The City of Sharvahl",
    "akheva": "Akheva Ruins",
    "echo": "Echo Caverns",
    "fungusgrove": "The Fungus Grove",
    "netherbian": "Netherbian Lair",
    "paludal": "The Paludal Caverns",
    "ssratemple": "Ssraeshza Temple",
    "thedeep": "The Deep",
    "vexthal": "Vex Thal",
}

SPELL_TARGETS = {
    1: "",
    2: "Area of effect over the caster",
    3: "Group teleport",
    4: "Area of effect around the caster",
    5: "Single target",
    6: "Self only",
    8: "Area of effect around the target",
    9: "Animal",
    10: "Undead only",
    11: "Summoned beings",
    13: "Tap",
    14: "Caster's pet",
    15: "Target's corpse",
    16: "Plant",
    17: "Giant",
    18: "Dragon",
    24: "Area of effect on undeads",
    25: "Area of Effect Summoned",
    36: "Area - PC Only",
    40: "Friendly area of effect",
    41: "Group",
}
