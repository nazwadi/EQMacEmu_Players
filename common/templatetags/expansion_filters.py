from django import template

register = template.Library()


@register.filter(name='exp_filter')
def exp_filter(expansion_code):
    match expansion_code:
        case -1:
            return "default"
        case 0:
            return "vanilla"
        case 1:
            return "kunark"
        case 2:
            return "velious"
        case 3:
            return "luclin"
        case 4:
            return "pop"
