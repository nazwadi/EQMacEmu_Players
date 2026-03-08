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