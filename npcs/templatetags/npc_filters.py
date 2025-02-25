from django import template
from common.constants import BODY_TYPES

register = template.Library()

@register.filter(name='body_type')
def body_type(value: int) -> str:
    return BODY_TYPES.get(value, 'Unknown')
