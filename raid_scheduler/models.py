from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from dkp.models import CircuitMembership, RaidCircuit

User = get_user_model()

RAID_TZ_CHOICES = [
    ('North America', [
        ('America/New_York',    'Eastern Time (ET)'),
        ('America/Chicago',     'Central Time (CT)'),
        ('America/Denver',      'Mountain Time (MT)'),
        ('America/Los_Angeles', 'Pacific Time (PT)'),
        ('America/Anchorage',   'Alaska Time (AKT)'),
        ('Pacific/Honolulu',    'Hawaii Time (HT)'),
    ]),
    ('Europe', [
        ('Europe/London',   'London (GMT/BST)'),
        ('Europe/Paris',    'Paris / Berlin / Rome (CET/CEST)'),
        ('Europe/Helsinki', 'Helsinki / Athens (EET/EEST)'),
        ('Europe/Moscow',   'Moscow (MSK)'),
    ]),
]


class RaidTarget(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class RaidEvent(models.Model):
    STATUS_SCHEDULED = 'scheduled'
    STATUS_ACTIVE = 'active'
    STATUS_CLOSED = 'closed'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_CLOSED, 'Closed'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    title = models.CharField(max_length=150, help_text='Descriptive name for this raid, e.g. "Tuesday NToV Progression"')
    targets = models.ManyToManyField(RaidTarget, related_name='raid_events', blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    # Either a linked circuit or a free-text write-in name
    circuit = models.ForeignKey(
        RaidCircuit, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='raid_events',
    )
    circuit_name = models.CharField(
        max_length=100, blank=True,
        help_text='Free-text circuit name when not linked to an existing circuit',
    )
    is_visible = models.BooleanField(
        default=True,
        help_text='Visible on the public board. Eligible for GM reservation protection.',
    )
    is_open = models.BooleanField(
        default=True,
        help_text='Open to all players. When False, attendance is restricted to circuit members.',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    timezone = models.CharField(
        max_length=50,
        default='America/New_York',
        choices=RAID_TZ_CHOICES,
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='created_raid_events',
    )
    posted_by_name = models.CharField(
        max_length=100, blank=True,
        help_text='Display name override for the poster. Leave blank to use their account username.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def posted_by_display(self):
        if self.posted_by_name:
            return self.posted_by_name
        if self.created_by:
            return self.created_by.username
        return '—'

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} — {self.date}"

    @property
    def circuit_display(self):
        if self.circuit:
            return self.circuit.name
        return self.circuit_name or '—'

    @property
    def visibility_display(self):
        if not self.is_visible:
            return 'Hidden'
        if self.is_open:
            return 'Open'
        return 'Closed'

    @property
    def tz_abbr(self):
        """Short timezone label for display, e.g. 'EST', 'PDT'."""
        tz_name = self.timezone or 'America/New_York'
        dt = datetime.combine(self.date, self.start_time).replace(tzinfo=ZoneInfo(tz_name))
        return dt.strftime('%Z')

    @property
    def expiry_dt(self):
        tz_name = self.timezone or 'America/New_York'
        naive = datetime.combine(self.date, self.start_time)
        aware = naive.replace(tzinfo=ZoneInfo(tz_name))
        return aware + timedelta(hours=2)

    def expire_if_stale(self):
        """Mark expired if 2 h have passed since start. Returns True if expired."""
        if self.status not in (self.STATUS_SCHEDULED, self.STATUS_ACTIVE):
            return False
        if timezone.now() >= self.expiry_dt:
            self.status = self.STATUS_EXPIRED
            self.save(update_fields=['status'])
            return True
        return False


class RaidSignup(models.Model):
    STATUS_CONFIRMED = 'confirmed'
    STATUS_TENTATIVE = 'tentative'
    STATUS_DECLINED = 'declined'

    STATUS_CHOICES = [
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_TENTATIVE, 'Tentative'),
        (STATUS_DECLINED, 'Declined'),
    ]

    event = models.ForeignKey(RaidEvent, on_delete=models.CASCADE, related_name='signups')
    # Null when this is a free-text write-in invite
    member = models.ForeignKey(
        CircuitMembership, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='raid_signups',
    )
    display_name = models.CharField(
        max_length=100, blank=True,
        help_text='Name for invites not linked to a roster member',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = [('event', 'member')]

    def __str__(self):
        name = self.member.display_name if self.member else self.display_name
        return f"{name} → {self.event}"


class GMOverrideLog(models.Model):
    """Audit trail for superuser-forced scheduling past a hard conflict."""
    event = models.ForeignKey(RaidEvent, on_delete=models.CASCADE, related_name='gm_overrides')
    overridden_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GM Override — {self.event} by {self.overridden_by} at {self.created_at:%Y-%m-%d %H:%M}"
