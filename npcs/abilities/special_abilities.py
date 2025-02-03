from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class NPCSpecialAbility:
    id: int
    name: str
    description: str

_ability_name_map: Dict[str, NPCSpecialAbility] = {}
_ability_id_map: Dict[int, NPCSpecialAbility] = {}

def _initialize_ability_maps():
    abilities = [
        NPCSpecialAbility(
            0,
            'None',
            'No special abilities.'
        ),
        NPCSpecialAbility(
            1,
            'Summon',
            'Allows you to teleport the player to the NPC, or the NPC to the player.'
        ),
        NPCSpecialAbility(
            2,
            'Enrage',
            'Allows the NPC to riposte incoming melee attacks.'
        ),
        NPCSpecialAbility(
            3,
            'Rampage',
            'Allows the NPC to attack additional players.'
        ),
        NPCSpecialAbility(
            4,
            'Area Rampage',
            'Allows the NPC to attack additional players in an area effect.'
        ),
        NPCSpecialAbility(
            5,
            'Flurry',
            'Allows the NPC to have additional melee attacks against a player.'
        ),
        NPCSpecialAbility(
            6,
            'Triple Attack',
            'Allows the NPC to have three melee attacks against a player.'
        ),
        NPCSpecialAbility(
            7,
            'Quad Attack',
            'Allows the NPC to have four melee attacks against a player.'
        ),
        NPCSpecialAbility(
            8,
            'Dual Wield',
            'Allows the NPC to utilize two weapons.'
        ),
        NPCSpecialAbility(
            9,
            'Bane Attack',
            'Gives the NPC the ability to hit NPCs that require bane weapons to damage.'
        ),
        NPCSpecialAbility(
            10,
            'Magical Attack',
            'Gives the NPC the ability to hit NPCs that require magical weapons to damage.'
        ),
        NPCSpecialAbility(
            11,
            'Ranged Attack',
            'Gives the NPC the ability to perform ranged attacks if their target is out of melee range.'
        ),
        NPCSpecialAbility(
            12,
            'Unslowable',
            'Makes the NPC immune to slow effects.'
        ),
        NPCSpecialAbility(
            13,
            'Unmezable',
            'Makes the NPC immune to mesmerization effects.'
        ),
        NPCSpecialAbility(
            14,
            'Uncharmable',
            'Makes the NPC immune to charm effects.'
        ),
        NPCSpecialAbility(
            15,
            'Unstunable',
            'Makes the NPC immune to stun effects.'
        ),
        NPCSpecialAbility(
            16,
            'Unsnareable',
            'Makes the NPC immune to snare effects.'
        ),
        NPCSpecialAbility(
            17,
            'Unfearable',
            'Makes the NPC immune to fear effects.'
        ),
        NPCSpecialAbility(
            18,
            'Immune to Dispell',
            'Makes the NPC immune to dispelling spells.'
        ),
        NPCSpecialAbility(
            19,
            'Immune to Melee',
            'Makes the NPC immune to all melee damage.'
        ),
        NPCSpecialAbility(
            20,
            'Immune to Magic',
            'Makes the NPC immune to all magic spells.'
        ),
        NPCSpecialAbility(
            21,
            'Immune to Fleeing',
            'Prevents the NPC from fleeing under any circumstances.'
        ),
        NPCSpecialAbility(
            22,
            'Immune to Non-Bane Damage',
            'Prevents the NPC from being damaged by weapons that don\'t have the bane type matching its bodytype.'
        ),
        NPCSpecialAbility(
            23,
            'Immune to Non-Magical Damage',
            'Prevents the NPC from being damaged by weapons that are not magical.'
        ),
        NPCSpecialAbility(
            24,
            'Will Not Aggro',
            'Prevents a player from getting on an NPC\'s hate list.'
        ),
        NPCSpecialAbility(
            25,
            'Immune to Aggro',
            'Prevents the NPC from getting on an NPC\'s hate list.'
        ),
        NPCSpecialAbility(
            26,
            'Resist Ranged Spells',
            'Prevents the NPC from being damaged from spells cast outside of melee range ("belly caster" mob).'
        ),
        NPCSpecialAbility(
            27,
            'See through Feign Death',
            'Allows the NPC to see through feign death attempts.'
        ),
        NPCSpecialAbility(
            28,
            'Immune to Taunt',
            'Prevents the NPC from being taunted by players.'
        ),
        NPCSpecialAbility(
            29,
            'Tunnel Vision',
            'Makes anyone not on the top of the hate list generate a different amount of hate.'
        ),
        NPCSpecialAbility(
            30,
            'Does NOT buff/heal friends',
            'Makes the NPC NOT buff or heal members of the same faction.'
        ),
        NPCSpecialAbility(
            31,
            'Unpacifiable',
            'Makes the NPC immune to lull effects.'
        ),
        NPCSpecialAbility(
            32,
            'Leashed',
            'Makes the NPC return to their aggro point, fully heal, and wipes their hate list if the NPC is pulled out of a particular range.'
        ),
        NPCSpecialAbility(
            33,
            'Tethered',
            'Is used to leash the mob to their aggro range.'
        ),
        NPCSpecialAbility(
            34,
            'Destructible Object',
            'Is used on destructing NPCs.'
        ),
        NPCSpecialAbility(
            35,
            'No Harm from Players',
            'Prevents players from being able to harm the NPC in any way.'
        ),
        NPCSpecialAbility(
            36,
            'Always Flee',
            'Makes the NPC flee at low health even if faction allies are near.'
        ),
        NPCSpecialAbility(
            37,
            'Flee Percentage',
            'Makes the NPC flee at low health even if faction allies are near, at a given percent.'
        ),
        NPCSpecialAbility(
            38,
            'Allow Beneficial',
            'Allows players to cast beneficial spells on the NPC.'
        ),
        NPCSpecialAbility(
            39,
            'Disable Melee',
            'Makes the NPC unable to melee, but does allow the NPC to aggro.'
        ),
        NPCSpecialAbility(
            40,
            'Chase Distance',
            'Establishes the minimum and maximum distances between the NPC and an aggro player.'
        ),
        NPCSpecialAbility(
            41,
            'Allow Tank',
            'Sets the NPC to allow other NPCs to take aggro from players.'
        ),
        NPCSpecialAbility(
            42,
            'Ignore Root Aggro',
            'Sets the NPC to ignore the rules of root aggro--the NPC will not attack the closest player, but rather the player on top of the hate list.'
        ),
        NPCSpecialAbility(
            43,
            'Casting Resist Diff',
            'Makes the NPC\'s spells cast at a different resist level.'
        ),
        NPCSpecialAbility(
            44,
            'Counter Avoid Damage',
            'Makes the NPC more likely to hit a player, decreasing their chance for avoiding melee through dodge/parry/riposte/etc.'
        ),
        NPCSpecialAbility(
            45,
            'Proximity Aggro',
            'Allows the NPC to engage new clients while in combat if the client is within their proximity.'
        ),
        NPCSpecialAbility(
            46,
            'Immune Ranged Attacks',
            'Makes the NPC immune to ranged attacks.'
        ),
        NPCSpecialAbility(
            47,
            'Immune Client Damage',
            'Makes the NPC immune to damage by clients.'
        ),
        NPCSpecialAbility(
            48,
            'Immune NPC Damage',
            'Makes the NPC immune to damage by NPCs.'
        ),
        NPCSpecialAbility(
            49,
            'Immune Client Aggro',
            'Makes the NPC immune to aggro by clients.'
        ),
        NPCSpecialAbility(
            50,
            'Immune NPC Aggro',
            'Makes the NPC immune to aggro by NPCs.'
        ),
        NPCSpecialAbility(
            51,
            'Modify Avoid Damage',
            'Allows you to modify specific avoidances for an NPC.'
        ),
        NPCSpecialAbility(
            52,
            'Immune Fading Memories',
            'Makes the NPC immune to memory fades.'
        ),
        NPCSpecialAbility(
            53,
            'Immune to Open',
            'Makes the NPC immune to /open.'
        ),
        NPCSpecialAbility(
            54,
            'Immune to Assassinate',
            'Makes the NPC immune to being Assassinated.'
        ),
        NPCSpecialAbility(
            55,
            'Immune to Headshot',
            'Makes the NPC immune to being Headshotted.'
        ),
        NPCSpecialAbility(
            56,
            'Immune to Bot Aggro',
            'Makes the NPC immune to Bot Aggro.'
        ),
        NPCSpecialAbility(
            57,
            'Immune to Bot Damage',
            'Makes the NPC immune to Bot Damage.'
        )
    ]

    for ability in abilities:
        _ability_name_map[ability.name.lower()] = ability
        _ability_id_map[ability.id] = ability

# Initialize when module loads
_initialize_ability_maps()

def get_ability_by_name(name: str) -> Optional[NPCSpecialAbility]:
    return _ability_name_map.get(name.lower())

def get_ability_by_id(id: int) -> Optional[NPCSpecialAbility]:
    return _ability_id_map.get(id)
