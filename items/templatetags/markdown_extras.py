import json
import markdown2 as md

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def render_markdown(value):
    return mark_safe(md.markdown(value, extras=['task_list', 'footnotes', 'tables']))


@register.filter
def dict_get(d, key):
    """Return d[key], or an empty dict if key is absent."""
    return d.get(key, {})


@register.filter
def bis_entries_json(entries):
    """Serialize a list of BISEntry objects to a JSON string safe for an HTML attribute."""
    data = [
        {"item_name": e.item_name, "item_id": e.item_id, "rank": e.rank, "note": e.note}
        for e in entries
    ]
    return escape(json.dumps(data))
