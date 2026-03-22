from django.contrib.auth.models import User
from django.db import models


class PetitionCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class StaffTag(models.Model):
    COLOR_CHOICES = [
        ('primary', 'Blue'),
        ('secondary', 'Grey'),
        ('success', 'Green'),
        ('danger', 'Red'),
        ('warning', 'Yellow'),
        ('info', 'Cyan'),
    ]
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='secondary')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CannedResponse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    body = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Petition(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLAIMED = 'claimed'
    STATUS_PENDING_PLAYER = 'pending_player'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLAIMED, 'Claimed'),
        (STATUS_PENDING_PLAYER, 'Pending Player'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    ACTIVE_STATUSES = [STATUS_OPEN, STATUS_CLAIMED, STATUS_PENDING_PLAYER]

    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_CRITICAL = 'critical'

    PRIORITY_CHOICES = [
        (PRIORITY_CRITICAL, 'Critical'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_LOW, 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petitions')
    category = models.ForeignKey(PetitionCategory, on_delete=models.PROTECT)
    subject = models.CharField(max_length=200)
    character_name = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    is_locked = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)
    claimed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_petitions'
    )
    staff_tags = models.ManyToManyField(StaffTag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"#{self.pk} — {self.subject}"

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES

    @property
    def status_badge_color(self):
        return {
            self.STATUS_OPEN: 'primary',
            self.STATUS_CLAIMED: 'info',
            self.STATUS_PENDING_PLAYER: 'warning',
            self.STATUS_RESOLVED: 'success',
            self.STATUS_CLOSED: 'secondary',
        }.get(self.status, 'secondary')

    def get_player_status_display(self):
        """Player-friendly status label — avoids internal jargon like 'Pending Player'."""
        if self.status == self.STATUS_PENDING_PLAYER:
            return 'Awaiting Your Response'
        return self.get_status_display()

    @property
    def age_display(self):
        from django.utils import timezone
        delta = timezone.now() - self.updated_at
        days = delta.days
        if days == 0:
            hours = delta.seconds // 3600
            return f'{hours}h' if hours > 0 else 'just now'
        if days < 7:
            return f'{days}d'
        return f'{days // 7}w'

    @property
    def is_stale(self):
        """Active petition with no activity for 2+ days."""
        from django.utils import timezone
        from datetime import timedelta
        return self.is_active and (timezone.now() - self.updated_at).days >= 2

    @property
    def priority_badge_color(self):
        return {
            self.PRIORITY_CRITICAL: 'danger',
            self.PRIORITY_HIGH: 'warning',
            self.PRIORITY_NORMAL: 'primary',
            self.PRIORITY_LOW: 'secondary',
        }.get(self.priority, 'secondary')


class PetitionReply(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    is_staff = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=False)   # staff-only note, hidden from petitioner
    is_system = models.BooleanField(default=False)     # audit log entry (status changes, claims)
    attachment = models.FileField(upload_to='petitions/attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to #{self.petition_id} by {self.user.username}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petition_notifications')
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class StaffEmailPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_email_pref')
    email_notifications = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} email prefs"


class PlayerEmailPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_email_pref')
    email_notifications = models.BooleanField(default=True)  # opt-out, so default is on

    def __str__(self):
        return f"{self.user.username} player email prefs"
