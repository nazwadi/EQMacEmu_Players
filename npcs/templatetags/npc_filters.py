import math
from django import template
from common.constants import BODY_TYPES

register = template.Library()


@register.filter(name='body_type')
def body_type(value: int) -> str:
    return BODY_TYPES.get(value, 'Unknown')


@register.filter(name='copper_to_coins')
def copper_to_coins(value: int) -> str:
    """Convert a raw copper value to a formatted PP/GP/SP/CP string."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return '0 cp'
    pp = math.floor(value / 1000)
    gp = math.floor((value % 1000) / 100)
    sp = math.floor((value % 100) / 10)
    cp = value % 10
    parts = []
    if pp:
        parts.append(f'{pp} pp')
    if gp:
        parts.append(f'{gp} gp')
    if sp:
        parts.append(f'{sp} sp')
    if cp or not parts:
        parts.append(f'{cp} cp')
    return ' '.join(parts)
