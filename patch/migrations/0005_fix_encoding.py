from django.db import migrations

AFFECTED_SLUGS = [
    'june-16-2006',
    'february-11-2009',
    'april-7-2009',
    'may-14-2009',
    'june-10-2009',
    'july-15-2009',
    'august-19-2009',
    'september-15-2009',
    'october-8-2009',
    'november-19-2009',
    'december-15-2009',
    'april-14-2010',
    'may-12-2010',
    'october-21-2010',
    'november-10-2010',
    'december-8-2010',
]


def fix_mojibake(text):
    """Fix mojibake by re-encoding latin-1 as utf-8."""
    if not text:
        return text
    # Check if any characters in U+0080-U+00FF are present
    if any('\u0080' <= ch <= '\u00ff' for ch in text):
        try:
            fixed = text.encode('latin-1').decode('utf-8', errors='replace')
            return fixed
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
    return text


def fix_encoding(apps, schema_editor):
    PatchMessage = apps.get_model('patch', 'PatchMessage')
    fixed_count = 0
    for slug in AFFECTED_SLUGS:
        try:
            pm = PatchMessage.objects.get(slug=slug)
        except PatchMessage.DoesNotExist:
            continue
        new_plaintext = fix_mojibake(pm.body_plaintext)
        new_markdown = fix_mojibake(pm.body_markdown)
        changed = False
        if new_plaintext != pm.body_plaintext:
            pm.body_plaintext = new_plaintext
            changed = True
        if new_markdown != pm.body_markdown:
            pm.body_markdown = new_markdown
            changed = True
        if changed:
            pm.save(update_fields=['body_plaintext', 'body_markdown'])
            fixed_count += 1
    print(f'Fixed encoding in {fixed_count} records.')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('patch', '0004_patch_type_expansion_markdown_edited_comment_subject'),
    ]

    operations = [
        migrations.RunPython(fix_encoding, noop),
    ]
