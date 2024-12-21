import markdown2 as md

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def render_markdown(value):
    return mark_safe(md.markdown(value, extras=['task_list', 'footnotes', 'tables']))
