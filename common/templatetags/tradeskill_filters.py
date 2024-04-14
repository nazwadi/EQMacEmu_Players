from django import template

register = template.Library()


@register.filter(name='tradeskill_filter')
def tradeskill_filter(tradeskill_id):
    """Match item slots bitmask to slots"""
    match tradeskill_id:
        case 55:
            return "Fishing"
        case 56:
            return "Make Poison"
        case 57:
            return "Tinkering"
        case 58:
            return "Research"
        case 59:
            return "Alchemy"
        case 60:
            return "Baking"
        case 61:
            return "Tailoring"
        case 62:
            return "Sense Traps"
        case 63:
            return "Blacksmithing"
        case 64:
            return "Fletching"
        case 65:
            return "Brewing"
        case 66:
            return "Alcohol Tolerance"
        case 67:
            return "Begging"
        case 68:
            return "Jewelry Making"
        case 69:
            return "Pottery"
        case 70:
            return "Percussion Instruments"
        case 71:
            return "Intimidation"
        case 72:
            return "Berserking"
        case 73:
            return "Taunt"
        case 75:
            return "Quest Combine"


@register.filter(name='trade_container_filter')
def trade_container_filter(container_code):
    match container_code:
        case 9:
            return "MEDICINEBAG"
        case 15:
            return "OVEN"
        case 16:
            return "SEWINGKIT"
        case 17:
            return "FORGE"
        case 0x12:
            return "FLETCHINGKIT"
        case 0x13:
            return "BREWBARREL"
        case 0x14:
            return "JEWELERSKIT"
        case 0x15:
            return "POTTERYWHEEL"
        case 0x16:
            return "KILN"
        case 0x17:
            return "KEYMAKER"
        case 0x18:
            return "WIZARDLEX"
        case 0x19:
            return "MAGELEX"
        case 0x1A:
            return "NECROLEX"
        case 0x1B:
            return "ENCHLEX"
        case 0x20:
            return "TEIRDALFORGE"
        case 0x21:
            return "OGGOKFORGE"
        case 0x22:
            return "STORMGUARDF"
        case 0x26:
            return "CABILISFORGE"
        case 0x2E:
            return "TACKLEBOX"
        case 0x30:
            return "FIERDALF"
        case 0x35:
            return "AUGMENT"
