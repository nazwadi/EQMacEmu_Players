from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from dkp.models import (
    Auction,
    Bid,
    CircuitMembership,
    DKPTransaction,
    Mob,
    Raid,
    RaidAttendance,
)

@transaction.atomic
def place_bid(auction, member, amount):
    """Place or update a bid. Returns (bid, created, error_message)."""
    from dkp.models import Bid
    from django.utils import timezone

    if auction.status != 'open':
        return None, False, 'Auction is not open for bidding.'

    config = getattr(auction.raid.circuit, 'circuitconfig', None) if auction.raid else None
    minimum_bid = config.minimum_bid if config else 0

    if amount < minimum_bid:
        return None, False, f'Minimum bid is {minimum_bid} DKP.'

    if amount > member.current_dkp:
        return None, False, f'Insufficient DKP. You have {member.current_dkp}.'

    # Update existing active bid or create new one
    existing = Bid.objects.filter(auction=auction, member=member, status='active').first()
    if existing:
        existing.bid_amount = amount
        existing.modified_at = timezone.now()
        existing.save(update_fields=['bid_amount', 'modified_at'])
        return existing, False, None
    else:
        bid = Bid.objects.create(
            auction=auction,
            member=member,
            bid_amount=amount,
            status='active',
            created_by=member.member,
        )
        return bid, True, None


@transaction.atomic
def retract_bid(auction, member):
    """Retract an active bid. Returns (success, error_message)."""
    from dkp.models import Bid

    if auction.status != 'open':
        return False, 'Bids can only be retracted while the auction is open.'

    updated = Bid.objects.filter(
        auction=auction, member=member, status='active'
    ).update(status='retracted')

    if updated:
        return True, None
    return False, 'No active bid found to retract.'


def attendance_calculation(member: CircuitMembership):
    """
    Calculate attendance for raids based on attendance records.
    """
    circuit = member.circuit
    days = circuit.circuitconfig.attendance_window_days
    if days is None:
        raise ValueError("Attendance window days not configured for the circuit")
    cutoff = timezone.now() - timedelta(days=days)
    matching_raids = Raid.objects.filter(date__gte=cutoff, circuit=circuit).count()
    attended_raids = RaidAttendance.objects.filter(
        member=member,
        raid__date__gte=cutoff,
        raid__circuit=circuit
    ).exclude(attendance_status='absent').count()
    return round((attended_raids / matching_raids) * 100, 1) if matching_raids > 0 else 0


@transaction.atomic
def award_dkp(raid: Raid, mob: Mob):
    """
    Award DKP to members for attendance at a raid.

    :param raid: Raid instance
    :param mob: Mob instance
    :return: None
    """
    dkp_payout = mob.dkp
    attendances = RaidAttendance.objects.filter(
        raid=raid
    ).exclude(attendance_status='absent').select_related('member')
    config = raid.circuit.circuitconfig
    max_dkp = config.dkp_cap + config.dkp_overcap
    for attendance in attendances:
        member = attendance.member
        if member.current_dkp + dkp_payout <= max_dkp:
            member.current_dkp += dkp_payout
        else:
            member.current_dkp = max_dkp
        member.lifetime_earned_dkp += dkp_payout
        member.save()
        dkp_transaction = DKPTransaction(raid=raid, member=member, amount=dkp_payout,
                                     transaction_type='award',created_by=None)
        dkp_transaction.save()
    cache.delete(f'dkp:standings:{raid.circuit_id}')

@transaction.atomic
def resolve_auction(auction: Auction):
    """
    Resolve an auction by awarding an item to the winning bidder.

    :param auction: Auction instance
    :return: None
    """
    bids = Bid.objects.filter(auction=auction).filter(status='active').order_by('-bid_amount', '-member__lifetime_earned_dkp')

    for bid in bids:
        if bid.bid_amount <= bid.member.current_dkp:
            auction.winner = bid
            bid.status = 'won'
            bid.save()
            break
    if auction.winner:
        bids.exclude(id=auction.winner.id).update(status='lost')
    else:
        bids.update(status='lost')
    auction.resolution_order = [bid.id for bid in bids]
    auction.status = 'closed'
    auction.closed_at = timezone.now()
    auction.save()
    if auction.raid:
        cache.delete(f'dkp:standings:{auction.raid.circuit_id}')

@transaction.atomic
def award_auction(auction: Auction, created_by: 'auth.User'):
    """
    Award the winning bid of an auction to the winner and update transaction status.

    :param auction: Auction instance
    :param created_by: User instance who initiated the auction award
    :return: None
    """
    if not auction.winner:
        raise ValueError("Auction has no winner")
    winning_bid = auction.winner
    winning_bid.member.current_dkp -= winning_bid.bid_amount
    winning_bid.member.lifetime_spent_dkp += winning_bid.bid_amount
    dkp_transaction = DKPTransaction(raid=auction.raid, member=winning_bid.member, amount=winning_bid.bid_amount,
                                     item_name=auction.item_name, item_id=auction.item_id,
                                     transaction_type='spend', created_by=created_by)
    dkp_transaction.save()
    winning_bid.member.save()
    auction.status = 'awarded'
    auction.save()

@transaction.atomic
def direct_award(raid, circuit, item_name, item_id, member, amount, created_by):
    """Award an item directly to a member without the bidding flow."""
    auction = Auction.objects.create(
        raid=raid,
        circuit=circuit,
        item_name=item_name,
        item_id=item_id,
        status='awarded',
        closed_at=timezone.now(),
        created_by=created_by,
    )
    bid = Bid.objects.create(
        auction=auction,
        member=member,
        bid_amount=amount,
        status='won',
        created_by=created_by,
    )
    auction.winner = bid
    auction.save(update_fields=['winner'])

    member.current_dkp -= amount
    member.lifetime_spent_dkp += amount
    member.save(update_fields=['current_dkp', 'lifetime_spent_dkp'])

    DKPTransaction.objects.create(
        raid=raid,
        member=member,
        item_name=item_name,
        item_id=item_id,
        amount=amount,
        transaction_type='spend',
        created_by=created_by,
    )
    cache.delete(f'dkp:standings:{circuit.id}')


def join_circuit(circuit, user, display_name=None):
    """Request to join a circuit. Returns (membership, created, error)."""
    from dkp.models import CircuitMembership

    existing = CircuitMembership.objects.filter(circuit=circuit, member=user).first()
    if existing:
        if existing.status == 'pending':
            return existing, False, 'You already have a pending request for this circuit.'
        elif existing.status == 'active':
            return existing, False, 'You are already a member of this circuit.'
        elif existing.status == 'inactive':
            return existing, False, 'Your membership is inactive. Contact an officer.'

    display_name = display_name.strip() if display_name else user.username

    membership = CircuitMembership.objects.create(
        circuit=circuit,
        member=user,
        display_name=display_name,
        role='member',
        status='pending',
    )
    return membership, True, None