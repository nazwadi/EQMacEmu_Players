"""Discord webhook notifications for raid scheduler events."""
import json
import logging
import urllib.request

logger = logging.getLogger(__name__)


def _post_to_discord(payload):
    from django.conf import settings
    webhook_url = getattr(settings, 'RAID_SCHEDULER_DISCORD_WEBHOOK_URL', '')
    if not webhook_url:
        return
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'DiscordBot (https://www.eqarchives.com, 1.0)',
            },
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        logger.error('Discord webhook failed: %s', e)


def notify_raid_scheduled(event):
    """Post to Discord when a new raid is scheduled."""
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    targets = ', '.join(t.name for t in event.targets.all())
    date_str = event.date.strftime('%A, %B %-d')
    time_str = event.start_time.strftime('%-I:%M %p')

    fields = [
        {'name': 'Circuit',  'value': event.circuit_display, 'inline': True},
        {'name': 'Date',     'value': date_str,               'inline': True},
        {'name': 'Time',     'value': time_str,               'inline': True},
        {'name': 'Targets',  'value': targets or '—',         'inline': False},
    ]

    _post_to_discord({
        'embeds': [{
            'title': f'📅 Raid Scheduled: {event.title}',
            'color': 0x8AA3FF,
            'fields': fields,
            'url': f'{site_url}/raids/event/{event.pk}/',
            'footer': {'text': f'Posted by {event.posted_by_display}'},
        }]
    })


def notify_raid_updated(event, changes):
    """
    Post to Discord when a scheduled raid is edited.

    `changes` is a list of human-readable strings describing what changed,
    e.g. ["date: Apr 12 → Apr 15", "time: 7:00 PM → 8:00 PM"].
    """
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    if not changes:
        return

    date_str = event.date.strftime('%A, %B %-d')
    time_str = event.start_time.strftime('%-I:%M %p')

    fields = [
        {'name': 'Circuit',  'value': event.circuit_display, 'inline': True},
        {'name': 'Date',     'value': date_str,               'inline': True},
        {'name': 'Time',     'value': time_str,               'inline': True},
        {'name': 'Changes',  'value': '\n'.join(f'• {c}' for c in changes), 'inline': False},
    ]

    _post_to_discord({
        'embeds': [{
            'title': f'✏️ Raid Updated: {event.title}',
            'color': 0xFCC721,
            'fields': fields,
            'url': f'{site_url}/raids/event/{event.pk}/',
            'footer': {'text': 'Check the schedule for the latest details.'},
        }]
    })
