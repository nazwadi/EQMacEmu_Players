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
            return "N/A (Quest Combine)"
