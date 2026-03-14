from django.db import models
from django.utils import timezone


TIEBREAKER_CHOICES = [
    ('earned_dkp', 'Earned DKP'),
    ('attendance', 'Attendance'),
]
CIRCUIT_MEMBERSHIP_STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending Approval')]
ROLE_CHOICES = [('officer', 'Officer'), ('member', 'Member')]
ATTENDANCE_CHOICES = [
    ('present', 'Present'),
    ('late', 'Late'),
    ('early_departure', 'Early Departure'),
    ('partial', 'Partial'),
    ('absent', 'Absent'),
]
TRANSACTION_TYPE_CHOICES = [
    ('award', 'Award'),
    ('spend', 'Spend'),
    ('adjustment', 'Adjustment')
]
AUCTION_STATUS_CHOICES = [('pending', 'Pending'), ('open', 'Open'), ('closed', 'Closed'), ('awarded', 'Awarded'),
                          ('disputed', 'Disputed'), ('retracted', 'Retracted')]
BID_STATUS_CHOICES = [('active', 'Active'), ('retracted', 'Retracted'), ('outbid', 'Outbid'), ('lost', 'Lost'), ('won', 'Won'), ('disputed', 'Disputed')]


# Create your models here.
class RaidCircuit(models.Model):
    """The guild, fellowship, or group of players that participate in this circuit of raid events.

    A RaidCircuit is the core definition for the players that participate in raid events for which we are tracking DKP.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CircuitConfig(models.Model):
    """RaidCircuit-specific configuration options."""
    circuit = models.OneToOneField(RaidCircuit, on_delete=models.CASCADE)
    public_bids = models.BooleanField(default=False)  # Default to private bidding (False)
    dkp_cap = models.DecimalField(default=50, max_digits=6, decimal_places=1)
    dkp_overcap = models.DecimalField(default=5, max_digits=6, decimal_places=1)
    minimum_bid = models.DecimalField(default=2, max_digits=6, decimal_places=1)
    new_player_bonus = models.DecimalField(default=15, max_digits=6, decimal_places=1)
    hourly_rate = models.DecimalField(default=2, max_digits=6, decimal_places=1)
    tie_breaker_rule = models.CharField(
        max_length=20, choices=TIEBREAKER_CHOICES, default='earned_dkp'
    )
    attendance_window_days = models.IntegerField(default=90)

    def __str__(self):
        return f'Config for {self.circuit.name}'


class CircuitMembership(models.Model):
    """Membership of a RaidCircuit by a User."""
    circuit = models.ForeignKey(RaidCircuit, on_delete=models.CASCADE)
    member = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, default='pending', choices=CIRCUIT_MEMBERSHIP_STATUS_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    display_name = models.CharField(max_length=200, blank=True)
    current_dkp = models.DecimalField(default=0, max_digits=6, decimal_places=1)
    lifetime_earned_dkp = models.DecimalField(default=0, max_digits=6, decimal_places=1)
    lifetime_spent_dkp = models.DecimalField(default=0, max_digits=6, decimal_places=1)
    hourly_redistribution = models.DecimalField(default=0, max_digits=6, decimal_places=1)
    hide_dashboard = models.BooleanField(default=False)

    class Meta:
        unique_together = ('circuit', 'member')

    def __str__(self):
        return f'{self.member.username} ({self.role})'

class Mob(models.Model):
    """Represents a mob within a RaidCircuit with associated DKP and activity status."""
    name = models.CharField(max_length=200)
    dkp = models.DecimalField(max_digits=6, decimal_places=1)
    circuit = models.ForeignKey(RaidCircuit, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    payout_change_history = models.JSONField(default=list)
    npc_id = models.IntegerField(null=True, blank=True)
    npc_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            old = Mob.objects.filter(pk=self.pk).values_list('dkp', flat=True).first()
            if old is not None and old != self.dkp:
                history = self.payout_change_history or []
                history.append({
                    'date': timezone.now().strftime('%Y-%m-%d'),
                    'old_dkp': str(old),
                    'new_dkp': str(self.dkp),
                })
                self.payout_change_history = history
        super().save(*args, **kwargs)

class Raid(models.Model):
    """Represents a raid event within a RaidCircuit."""
    date = models.DateField()
    labels = models.CharField(max_length=200, blank=True)
    circuit = models.ForeignKey(RaidCircuit, on_delete=models.CASCADE)
    members = models.ManyToManyField('CircuitMembership', through='RaidAttendance')
    mobs = models.ManyToManyField('Mob')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    mob_dkp_snapshot = models.JSONField(default=dict, blank=True)
    mobs_awarded = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f'{self.date}'

class RaidAttendance(models.Model):
    """Represents the attendance of a member in a raid event."""
    member = models.ForeignKey('CircuitMembership', on_delete=models.CASCADE)
    raid = models.ForeignKey(Raid, on_delete=models.CASCADE)
    arrived_at = models.DateTimeField(null=True, blank=True)
    departed_at = models.DateTimeField(null=True, blank=True)
    partial_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='present')
    attendance_notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.member.display_name} in {self.raid.date}'

    class Meta:
        unique_together = ('member', 'raid')

class DKPTransaction(models.Model):
    """Represents a DKP transaction for an item at a Raid"""
    raid = models.ForeignKey(Raid, null=True, blank=True, on_delete=models.SET_NULL)
    member = models.ForeignKey(CircuitMembership, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200, null=True, blank=True)
    item_id = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=1)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_notes = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        raid_date = self.raid.date if self.raid else 'Manual Adjustment'
        item = self.item_name or ''
        return f'{self.member.display_name} - {self.transaction_type} - {self.amount} DKP {item} ({raid_date})'

class Auction(models.Model):
    """Represents an auction for an item at a Raid"""
    raid = models.ForeignKey(Raid, null=True, blank=True, on_delete=models.SET_NULL)
    circuit = models.ForeignKey(RaidCircuit, on_delete=models.CASCADE, null=True, blank=True, related_name='auctions')
    item_name = models.CharField(max_length=200, null=True, blank=True)
    item_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=AUCTION_STATUS_CHOICES, default='pending')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    resolution_order = models.JSONField(default=list)
    admin_override = models.ForeignKey(CircuitMembership, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctioned_overrides')
    override_reason = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    winner = models.ForeignKey(
        'Bid',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_auctions'
    )

    def __str__(self):
        raid_date = self.raid.date if self.raid else 'No Raid'
        return f'{self.item_name} ({raid_date})'

class Bid(models.Model):
    """Represents a bid in an auction"""
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    member = models.ForeignKey(CircuitMembership, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=6, decimal_places=1)
    bidder_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=BID_STATUS_CHOICES, default='active')
    submitted_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.member.display_name} - {self.auction.item_name} - {self.bid_amount} DKP'


class RaidMobAttendance(models.Model):
    """Records which members were present for each mob kill at a raid."""
    raid = models.ForeignKey(Raid, on_delete=models.CASCADE)
    mob = models.ForeignKey(Mob, on_delete=models.CASCADE)
    member = models.ForeignKey(CircuitMembership, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('raid', 'mob', 'member')

    def __str__(self):
        return f'{self.member.display_name} — {self.mob.name} ({self.raid.date})'
