from common.constants import ITEM_STATS

def get_class_bitmask(class_id):
    """

    :param class_id:
    :return:
    """
    match class_id:
        case 1:  # WAR
            return 1
        case 2:  # CLR
            return 2
        case 3:  # PAL
            return 4
        case 4:  # RNG
            return 8
        case 5:  # SHD
            return 16
        case 6:  # DRU
            return 32
        case 7:  # MNK
            return 64
        case 8:  # BRD
            return 128
        case 9:  # ROG
            return 256
        case 10:  # SHM
            return 512
        case 11:  # NEC
            return 1024
        case 12:  # WIZ
            return 2048
        case 13:  # MAG
            return 4096
        case 14:  # ENC
            return 8192
        case 15:  # BST
            return 16384
        case _:
            return 0


def check_class_can_use_item(classes_bitmask, class_id):
    """

    :param class_id:
    :param classes_bitmask:
    :return:
    """
    match class_id:
        case 1:  # WAR
            result = classes_bitmask & 1
        case 2:  # CLR
            result = classes_bitmask & 2
        case 3:  # PAL
            result = classes_bitmask & 4
        case 4:  # RNG
            result = classes_bitmask & 8
        case 5:  # SHD
            result = classes_bitmask & 16
        case 6:  # DRU
            result = classes_bitmask & 32
        case 7:  # MNK
            result = classes_bitmask & 64
        case 8:  # BRD
            result = classes_bitmask & 128
        case 9:  # ROG
            result = classes_bitmask & 256
        case 10:  # SHM
            result = classes_bitmask & 512
        case 11:  # NEC
            result = classes_bitmask & 1024
        case 12:  # WIZ
            result = classes_bitmask & 2048
        case 13:  # MAG
            result = classes_bitmask & 4096
        case 14:  # ENC
            result = classes_bitmask & 8192
        case 15:  # BST
            result = classes_bitmask & 16384
        case _:  # anything else
            result = 0
    return result


def get_race_bitmask(race_id: int):
    """

    :param race_id:
    :return: the bitmask associated with the given race_id
    """
    match race_id:
        case 1:  # Human
            return 1
        case 2:  # Barbarian
            return 2
        case 3:  # Erudite
            return 4
        case 4:  # Wood Elf
            return 8
        case 5:  # High Elf
            return 16
        case 6:  # Dark Elf
            return 32
        case 7:  # Half Elf
            return 64
        case 8:  # Dwarf
            return 128
        case 9:  # Troll
            return 256
        case 10:  # Ogre
            return 512
        case 11:  # Halfling
            return 1024
        case 12:  # Gnome
            return 2048
        case 13:  # Iksar
            return 4096
        case 14:  # Vah Shir
            return 8192
        case _:
            return 0

def build_stat_query(clause: str,
                     stat: str,
                     operator: str) -> (str, list):
    """

    :param clause: either WHERE or AND (the latter if WHERE is already part of the query)
    :param stat: an item stat (found in common.constants.ITEM_STATS)
    :param operator: a comparison operator (e.g. >, <, <=, >=, = )
    :return: the partial query and error messages if they occurred
    """
    error_messages = []


    if stat not in ITEM_STATS.keys():
        error_messages.append("Invalid item stat submitted")

    allowed_operators = {'>': '>', '>=': '>=', '=': '=', '<=': '<=', '<': '<'}
    if operator not in allowed_operators.keys():
        error_messages.append("Invalid stat operator submitted")
    else:
        operator = allowed_operators[operator]  # just an extra precaution
    partial_query = f" {clause} items.{stat} {operator} %s"

    return partial_query, error_messages
