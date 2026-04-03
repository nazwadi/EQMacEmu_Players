import json
import re
import markdown2 as md

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

_WIKITEXT_BOLD = re.compile(r"'''(.+?)'''", re.DOTALL)
_WIKITEXT_ITALIC = re.compile(r"''(.+?)''", re.DOTALL)
_CATEGORY_TAG = re.compile(r'\n?Category:[^\n]+', re.MULTILINE)
# Add blank line before a list item (-/*/digit.) that immediately follows a non-blank, non-list line
_LIST_NEEDS_BLANK = re.compile(r'([^\n])\n([-*]|\d+\.) ')


def _preprocess(text):
    text = _WIKITEXT_BOLD.sub(r'**\1**', text)
    text = _WIKITEXT_ITALIC.sub(r'*\1*', text)
    text = _CATEGORY_TAG.sub('', text)
    text = _LIST_NEEDS_BLANK.sub(r'\1\n\n\2 ', text)
    return text.strip()


@register.filter
@stringfilter
def render_markdown(value):
    return mark_safe(md.markdown(_preprocess(value), extras=[
        'task_list',
        'footnotes',
        'tables',
        'fenced-code-blocks',
        'strike',
        'header-ids',
    ]))


@register.filter
def dict_get(d, key):
    """Return d[key], or an empty dict if key is absent."""
    return d.get(key, {})


@register.filter
def bis_entries_json(entries):
    """Serialize a list of BISEntry objects to a JSON string safe for an HTML attribute."""
    if not isinstance(entries, (list, tuple)):
        return escape(json.dumps([]))
    data = [
        {"item_name": e.item_name, "item_id": e.item_id, "rank": e.rank, "note": e.note}
        for e in entries
    ]
    return escape(json.dumps(data))
