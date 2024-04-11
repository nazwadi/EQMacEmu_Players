from django import template

register = template.Library()


@register.filter(name='positive_negative')
def positive_negative(value):
    if value > 0:
        return "+"+str(value)
    return value


@register.filter(name='item_type')
def item_type(item_type):
    match item_type:
        case 0:
            return "1H Slashing"
        case 1:
            return "2H Slashing"
        case 2: # 1H Piercing
            return "Piercing"
        case 3:
            return "1H Blunt"
        case 4:
            return "2H Blunt"
        case 35: # 2H Piercing
            return "Piercing"
        case 42:
            return "Hand to Hand"
        case 45:  # Sometimes shown as 'Martial', but Hand to Hand is what the client shows
            return "Hand to Hand"
        case _:
            return "None"


@register.filter(name='item_slots')
def item_slots(item_slot_bitmask):
    """Match item slots bitmask to slots"""
    slots_available = list()
    if item_slot_bitmask == 0:
        return None
    if item_slot_bitmask & 2 or item_slot_bitmask & 16:
        slots_available.append("EARS")
    if item_slot_bitmask & 4:
        slots_available.append("HEAD")
    if item_slot_bitmask & 8:
        slots_available.append("FACE")
    if item_slot_bitmask& 32:
        slots_available.append("NECK")
    if item_slot_bitmask & 64:
        slots_available.append("SHOULDER")
    if item_slot_bitmask & 128:
        slots_available.append("ARMS")
    if item_slot_bitmask & 256:
        slots_available.append("BACK")
    if item_slot_bitmask & 512 or item_slot_bitmask & 1024:
        slots_available.append("WRIST")
    if item_slot_bitmask & 2048:
        slots_available.append("RANGE")
    if item_slot_bitmask & 4096:
        slots_available.append("HANDS")
    if item_slot_bitmask & 8192:
        slots_available.append("PRIMARY")
    if item_slot_bitmask & 16384:
        slots_available.append("SECONDARY")
    if item_slot_bitmask & 32768 or item_slot_bitmask & 65536:
        slots_available.append("FINGERS")
    if item_slot_bitmask & 131072:
        slots_available.append("CHEST")
    if item_slot_bitmask & 262144:
        slots_available.append("LEGS")
    if item_slot_bitmask & 524288:
        slots_available.append("FEET")
    if item_slot_bitmask & 1048576:
        slots_available.append("WAIST")
    if item_slot_bitmask & 2097152:
        slots_available.append("POWERSOURCE")
    if item_slot_bitmask & 4194304:
        slots_available.append("AMMO")
    return ' '.join(slots_available)


@register.filter(name='item_classes')
def item_classes(classes_bitmask):
    """Match classes bitmask from an item row to human-readable value"""
    if classes_bitmask == 0:
        return "None"
    if classes_bitmask == 32767:
        return "ALL"

    classes_can_use = list()
    if classes_bitmask & 1:
        classes_can_use.append("WAR")
    if classes_bitmask & 2:
        classes_can_use.append("CLR")
    if classes_bitmask & 4:
        classes_can_use.append("PAL")
    if classes_bitmask & 8:
        classes_can_use.append("RNG")
    if classes_bitmask & 16:
        classes_can_use.append("SHD")
    if classes_bitmask & 32:
        classes_can_use.append("DRU")
    if classes_bitmask & 64:
        classes_can_use.append("MNK")
    if classes_bitmask & 128:
        classes_can_use.append("BRD")
    if classes_bitmask & 256:
        classes_can_use.append("ROG")
    if classes_bitmask & 512:
        classes_can_use.append("SHM")
    if classes_bitmask & 1024:
        classes_can_use.append("NEC")
    if classes_bitmask & 2048:
        classes_can_use.append("WIZ")
    if classes_bitmask & 4096:
        classes_can_use.append("MAG")
    if classes_bitmask & 8192:
        classes_can_use.append("ENC")
    if classes_bitmask & 16384:
        classes_can_use.append("BST")
    return " ".join(classes_can_use)


@register.filter(name='item_deities')
def item_deities(deity_bitmask):
    """Match deities bitmask from an item row to human-readable value"""
    deities_can_use = list()
    if deity_bitmask == 0:
        return 'All'
    if deity_bitmask & 1:
        deities_can_use.append("Agnostic")
    if deity_bitmask & 2:
        deities_can_use.append("Bertoxxulous")
    if deity_bitmask & 4:
        deities_can_use.append("Brell Serilis")
    if deity_bitmask & 8:
        deities_can_use.append("Cazic-Thule")
    if deity_bitmask & 16:
        deities_can_use.append("Erollisi Marr")
    if deity_bitmask & 32:
        deities_can_use.append("Bristlebane")
    if deity_bitmask & 64:
        deities_can_use.append("Innoruuk")
    if deity_bitmask & 128:
        deities_can_use.append("Karana")
    if deity_bitmask & 256:
        deities_can_use.append("Mithaniel Marr")
    if deity_bitmask & 512:
        deities_can_use.append("Prexus")
    if deity_bitmask & 1024:
        deities_can_use.append("Quellious")
    if deity_bitmask & 2048:
        deities_can_use.append("Rallos Zek")
    if deity_bitmask & 4096:
        deities_can_use.append("Rodcet Nife")
    if deity_bitmask & 8192:
        deities_can_use.append("Solusek Ro")
    if deity_bitmask & 16384:
        deities_can_use.append("The Tribunal")
    if deity_bitmask & 32768:
        deities_can_use.append("Tunare")
    if deity_bitmask & 65536:
        deities_can_use.append("Veeshan")
    return ' '.join(deities_can_use)

@register.filter(name='item_races')
def item_races(races_bitmask):
    """Match races bitmask from an item row to human-readable value"""
    races_can_use = list()
    if races_bitmask == 16383:
        return "ALL"
    if races_bitmask == 0:
        return "None"

    if races_bitmask & 1:
        races_can_use.append("HUM")
    if races_bitmask & 2:
        races_can_use.append("BAR")
    if races_bitmask & 4:
        races_can_use.append("ERU")
    if races_bitmask & 8:
        races_can_use.append("ELF")
    if races_bitmask & 16:
        races_can_use.append("HIE")
    if races_bitmask & 32:
        races_can_use.append("DEF")
    if races_bitmask & 64:
        races_can_use.append("HEF")
    if races_bitmask & 128:
        races_can_use.append("DWF")
    if races_bitmask & 256:
        races_can_use.append("TRL")
    if races_bitmask & 512:
        races_can_use.append("OGR")
    if races_bitmask & 1024:
        races_can_use.append("HLF")
    if races_bitmask & 2048:
        races_can_use.append("GNM")
    if races_bitmask & 4096:
        races_can_use.append("IKS")
    if races_bitmask & 8192:
        races_can_use.append("VAH")

    return " ".join(races_can_use)


@register.filter(name='item_weight')
def item_weight(weight):
    """Match classes bitmask from an item row to human-readable value"""
    return weight/10


@register.filter(name='item_size')
def item_size(size):
    """Convert size integer to human-readable value"""
    match size:
        case 0:
            return "TINY"
        case 1:
            return "SMALL"
        case 2:
            return "MEDIUM"
        case 3:
            return "LARGE"
        case 4:
            return "GIANT"
        case _:
            return "Unknown"


@register.filter(name='ms_to_seconds')
def ms_to_seconds(milliseconds):
    return milliseconds/1000
