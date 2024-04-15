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
            return "Medicine Bag"
        case 15:
            return "Oven"
        case 16:
            return "Loom"
        case 17:
            return "Forge"
        case 18:
            return "Fletching Kit"
        case 19:
            return "Brew Barrel"
        case 20:
            return "Jeweler's Kit"
        case 21:
            return "Pottery Wheel"
        case 22:
            return "Kiln"
        case 23:
            return "Key Maker"
        case 24:
            return "Wizard Lexicon"
        case 25:
            return "Mage Lexicon"
        case 26:
            return "Necro Lexicon"
        case 27:
            return "Enchanter Lexicon"
        case 32:
            return "Tier`Dal Forge"
        case 33:
            return "Oggok Forge"
        case 34:
            return "Storm Guard Forge"
        case 38:
            return "Cabilis Forge"
        case 46:
            return "Tacklebox"
        case 48:
            return "Fier'Dal Forge"
        case 53:
            return "Augment Pool"


@register.filter(name='trade_icon_filter')
def trade_icon_filter(container_code):
    match container_code:
        case 9:  # Medicine Bag
            return "item_727.png"
        case 15:  # Oven
            return "item_1114.png"
        case 16:  # Sewing Kit
            return "item_892.png"
        case 17:  # Forge
            return "item_1115.png"
        case 18:  # Fletching Kit
            return "item_883.png"
        case 19:  # Brew Barrel
            return "item_1116.png"
        case 20:  # Jeweler's Kit
            return "item_539.png"
        case 21:  # Pottery Wheel
            return "item_1112.png"
        case 22: # Kiln
            return "item_1113.png"  # KILN
        case 23: # Key Maker
            return "item_716.png"
        case 24: # Wizard Lexicon
            return "item_777.png"
        case 25: # Mage Lexicon
            return "item_777.png"
        case 26: # Necro Lexicon
            return "item_777.png"
        case 27: # Enchanter Lexicon
            return "item_777.png"
        case 32: # Tier`Dal Forge
            return "item_1115.png"
        case 33: # Oggok Forge
            return "item_1115.png"
        case 34: # Storm Guard Forge
            return "item_1115.png"
        case 38: # Cabilis Forge
            return "item_1115.png"
        case 46: # Tacklebox
            return "item_730.png"
        case 48: # Fier`Dal Forge
            return "item_1115.png"
        case 53: # Augment Pool
            return "item_1142.png"
