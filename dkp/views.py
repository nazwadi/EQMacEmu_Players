import json
from decimal import Decimal, InvalidOperation

from django.db.models import Count, Max, Sum, Q
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.shortcuts import render, redirect
from dkp.models import CircuitConfig, CircuitMembership, DKPTransaction, Auction, Bid, RaidCircuit, Raid, \
    RaidAttendance, Mob, RaidMobAttendance
from dkp.utils import get_standings
from dkp.services import attendance_calculation

from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from dkp.services import place_bid, retract_bid

from dkp.services import join_circuit


def get_circuit_from_kwargs(kwargs):
    if 'circuit_id' in kwargs:
        return RaidCircuit.objects.filter(id=kwargs['circuit_id']).first()
    if 'raid_id' in kwargs:
        raid = Raid.objects.filter(id=kwargs['raid_id']).select_related('circuit').first()
        return raid.circuit if raid else None
    if 'auction_id' in kwargs:
        auction = Auction.objects.filter(id=kwargs['auction_id']).select_related('circuit').first()
        return auction.circuit if auction else None
    return None


def get_officer_membership(user, circuit):
    """Returns membership if user is an officer in circuit, else None."""
    m = CircuitMembership.objects.filter(circuit=circuit, member=user).first()
    if m and (m.role == 'officer' or user.is_superuser):
        return m
    return None


def officer_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        circuit = get_circuit_from_kwargs(kwargs)
        if not circuit:
            raise Http404
        if not get_officer_membership(request.user, circuit):
            raise Http404
        return view_func(request, *args, **kwargs)

    return wrapper

def attendance_history(request, membership_id):
    membership = CircuitMembership.objects.filter(id=membership_id).select_related('circuit', 'member').first()
    if not membership:
        raise Http404

    is_officer = bool(get_officer_membership(request.user, membership.circuit))
    is_own = request.user.is_authenticated and membership.member == request.user

    if not is_own and not is_officer:
        raise Http404

    config = getattr(membership.circuit, 'circuitconfig', None)
    window = config.attendance_window_days if config else 90
    cutoff = timezone.now() - timedelta(days=window)
    raids = Raid.objects.filter(
        circuit=membership.circuit,
        date__gte=cutoff
    ).order_by('-date')

    if request.method == 'POST' and is_officer:
        checked_ids = set(int(x) for x in request.POST.getlist('raid_ids'))
        existing = {a.raid_id: a for a in RaidAttendance.objects.filter(member=membership, raid__in=raids)}
        for raid in raids:
            att = existing.get(raid.id)
            if raid.id in checked_ids:
                if att is None:
                    RaidAttendance.objects.create(
                        raid=raid, member=membership, attendance_status='present'
                    )
                elif att.attendance_status == 'absent':
                    att.attendance_status = 'present'
                    att.save(update_fields=['attendance_status'])
                # non-absent record already exists — leave status untouched
            else:
                if att and att.attendance_status != 'absent':
                    att.delete()
        messages.success(request, f'Attendance updated for {membership.display_name}.')
        return redirect('dkp:attendance_history', membership_id=membership.id)

    attendance_map = {
        a.raid_id: a for a in RaidAttendance.objects.filter(
            member=membership, raid__in=raids
        )
    }

    raid_rows = []
    for raid in raids:
        att = attendance_map.get(raid.id)
        raid_rows.append({
            'raid': raid,
            'attendance': att,
            'status': att.attendance_status if att else 'not_attended',
            'notes': att.attendance_notes if att else '',
            'checked': bool(att and att.attendance_status != 'absent'),
        })

    attended_count = sum(1 for row in raid_rows if row['status'] not in ('absent', 'not_attended'))
    total_count = len(raid_rows)
    attendance_pct = round((attended_count / total_count) * 100, 1) if total_count > 0 else 0

    return render(request, 'dkp/attendance_history.html', {
        'membership': membership,
        'circuit': membership.circuit,
        'raid_rows': raid_rows,
        'is_own': is_own,
        'is_officer': is_officer,
        'config': config,
        'attended_count': attended_count,
        'total_count': total_count,
        'attendance_pct': attendance_pct,
    })

@login_required
@require_POST
def circuit_join(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id, is_active=True, is_public=True).first()
    if not circuit:
        raise Http404

    display_name = request.POST.get('display_name', '').strip() or request.user.username

    membership, created, error = join_circuit(circuit, request.user, display_name)
    if error:
        messages.error(request, error)
    else:
        messages.success(request, f'Your request to join {circuit.name} has been submitted and is pending approval.')

    return redirect('dkp:standings', circuit_id=circuit_id)

@officer_required
def circuit_config(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    config, created = CircuitConfig.objects.get_or_create(circuit=circuit)
    if created:
        config.save()

    if request.method == 'POST':
        try:
            config.dkp_cap = Decimal(request.POST.get('dkp_cap', config.dkp_cap))
            config.dkp_overcap = Decimal(request.POST.get('dkp_overcap', config.dkp_overcap))
            config.minimum_bid = Decimal(request.POST.get('minimum_bid', config.minimum_bid))
            config.new_player_bonus = Decimal(request.POST.get('new_player_bonus', config.new_player_bonus))
            config.hourly_rate = Decimal(request.POST.get('hourly_rate', config.hourly_rate))
            config.attendance_window_days = int(
                request.POST.get('attendance_window_days', config.attendance_window_days))
            config.tie_breaker_rule = request.POST.get('tie_breaker_rule', config.tie_breaker_rule)
            config.public_bids = request.POST.get('public_bids') == 'on'
            config.save()
            messages.success(request, 'Circuit settings saved.')
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Invalid value — settings not saved.')

        return redirect('dkp:circuit_config', circuit_id=circuit_id)

    return render(request, 'dkp/circuit_config.html', {
        'circuit': circuit,
        'config': config,
    })

def circuit_list(request):
    circuits = RaidCircuit.objects.filter(is_active=True, is_public=True)
    if circuits.count() == 1:
        return redirect('dkp:standings', circuit_id=circuits.first().id)
    return render(request, 'dkp/circuit_list.html', {'circuits': circuits})

def auction_state(request, auction_id):
    """
    Lightweight polling endpoint — returns current auction state as JSON.
    Structured so this could be replaced by a WebSocket consumer later
    with no changes to the frontend JS.
    """
    auction = Auction.objects.filter(id=auction_id).select_related(
        'winner__member', 'circuit'
    ).first()
    if not auction:
        return JsonResponse({'error': 'Not found'}, status=404)

    circuit = auction.circuit
    config = getattr(circuit, 'circuitconfig', None) if circuit else None
    public_bids = config.public_bids if config else False

    viewer_membership = None
    is_officer = False
    if request.user.is_authenticated and circuit:
        viewer_membership = CircuitMembership.objects.filter(
            circuit=circuit, member=request.user
        ).first()
        is_officer = bool(viewer_membership and viewer_membership.role == 'officer')

    bids_qs = Bid.objects.filter(auction=auction).select_related('member').order_by('-bid_amount')

    bid_count = bids_qs.count()
    high_bid = bids_qs.first().bid_amount if bid_count > 0 else None

    # Build bid list based on visibility rules
    if is_officer or public_bids:
        bids_data = [
            {
                'bidder': b.member.display_name,
                'amount': str(b.bid_amount),
                'status': b.status,
                'is_mine': viewer_membership and b.member_id == viewer_membership.id,
            }
            for b in bids_qs
        ]
    elif viewer_membership:
        my_bid = bids_qs.filter(member=viewer_membership).first()
        bids_data = [
            {
                'bidder': 'You',
                'amount': str(my_bid.bid_amount),
                'status': my_bid.status,
                'is_mine': True,
            }
        ] if my_bid else []
    else:
        bids_data = []

    my_active_bid = None
    if viewer_membership:
        b = bids_qs.filter(member=viewer_membership, status='active').first()
        if b:
            my_active_bid = str(b.bid_amount)

    return JsonResponse({
        'auction_id': auction_id,
        'status': auction.status,
        'bid_count': bid_count,
        'high_bid': str(high_bid) if high_bid else None,
        'bids': bids_data,
        'my_active_bid': my_active_bid,
        'public_bids': public_bids,
        'is_officer': is_officer,
    })

@login_required
@require_POST
def bid_submit(request, auction_id):
    auction = Auction.objects.filter(id=auction_id).select_related('circuit').first()
    if not auction:
        return JsonResponse({'error': 'Auction not found.'}, status=404)

    circuit = auction.circuit
    if not circuit:
        return JsonResponse({'error': 'No circuit found.'}, status=400)

    member = CircuitMembership.objects.filter(
        circuit=circuit, member=request.user, status='active'
    ).first()
    if not member:
        return JsonResponse({'error': 'You are not an active member of this circuit.'}, status=403)

    try:
        amount = Decimal(request.POST.get('amount', '0'))
    except Exception:
        return JsonResponse({'error': 'Invalid bid amount.'}, status=400)

    bid, created, error = place_bid(auction, member, amount)
    if error:
        return JsonResponse({'error': error}, status=400)

    return JsonResponse({
        'success': True,
        'created': created,
        'bid_amount': str(bid.bid_amount),
    })


@login_required
@require_POST
def bid_retract(request, auction_id):
    auction = Auction.objects.filter(id=auction_id).select_related('circuit').first()
    if not auction:
        return JsonResponse({'error': 'Auction not found.'}, status=404)

    circuit = auction.circuit
    member = CircuitMembership.objects.filter(
        circuit=circuit, member=request.user, status='active'
    ).first()
    if not member:
        return JsonResponse({'error': 'Not a member.'}, status=403)

    success, error = retract_bid(auction, member)
    if not success:
        return JsonResponse({'error': error}, status=400)

    return JsonResponse({'success': True})


def auction_list(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    is_member = request.user.is_authenticated and CircuitMembership.objects.filter(
        circuit=circuit, member=request.user, status='active'
    ).exists()
    viewer_membership = None
    is_officer = False
    if request.user.is_authenticated:
        viewer_membership = CircuitMembership.objects.filter(
            circuit=circuit, member=request.user
        ).first()
        is_officer = viewer_membership and viewer_membership.role == 'officer'

    active_auctions = Auction.objects.filter(
        status__in=['pending', 'open'],
        circuit=circuit
    ).annotate(
        bid_count=Count('bid'),
        high_bid=Max('bid__bid_amount')
    ).order_by('-opened_at')

    closed_auctions = Auction.objects.filter(
        status__in=['closed', 'awarded', 'disputed', 'retracted'],
        circuit=circuit
    ).annotate(
        bid_count=Count('bid'),
        high_bid=Max('bid__bid_amount')
    ).select_related('winner__member').order_by('-opened_at')

    config = getattr(circuit, 'circuitconfig', None)
    public_bids = config.public_bids if config else False

    return render(request, 'dkp/auction_list.html', {
        'circuit': circuit,
        'active_auctions': active_auctions,
        'closed_auctions': closed_auctions,
        'is_member': is_member,
        'is_officer': is_officer,
        'config': config,
        'public_bids': public_bids
    })

def auction_detail(request, auction_id):
    auction = Auction.objects.filter(id=auction_id).select_related(
        'circuit', 'winner__member', 'admin_override'
    ).first()
    if not auction:
        raise Http404

    circuit = auction.circuit

    is_member = False
    is_officer = False
    viewer_membership = None
    if request.user.is_authenticated and circuit:
        viewer_membership = CircuitMembership.objects.filter(
            circuit=circuit, member=request.user
        ).first()
        is_member = viewer_membership and viewer_membership.status == 'active'
        is_officer = viewer_membership and viewer_membership.role == 'officer'

    config = getattr(circuit, 'circuitconfig', None) if circuit else None
    public_bids = config.public_bids if config else False

    # Bids visibility
    if is_officer or public_bids:
        bids = Bid.objects.filter(auction=auction).select_related(
            'member'
        ).order_by('-bid_amount')
    elif viewer_membership:
        bids = Bid.objects.filter(
            auction=auction, member=viewer_membership
        ).select_related('member')
    else:
        bids = Bid.objects.none()

    return render(request, 'dkp/auction_detail.html', {
        'auction': auction,
        'circuit': circuit,
        'bids': bids,
        'is_member': is_member,
        'is_officer': is_officer,
        'public_bids': public_bids,
        'viewer_membership': viewer_membership,
    })

@officer_required
def auction_manage(request, auction_id):
    auction = Auction.objects.filter(id=auction_id).select_related(
        'circuit', 'winner__member', 'admin_override'
    ).first()
    if not auction:
        raise Http404

    circuit = auction.circuit
    if not circuit or not get_officer_membership(request.user, circuit):
        raise Http404

    members = CircuitMembership.objects.filter(
        circuit=circuit, status='active'
    ).order_by('display_name')

    bids = Bid.objects.filter(auction=auction).select_related('member').order_by('-bid_amount')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'override_winner':
            member_id = request.POST.get('member_id')
            reason = request.POST.get('override_reason', '')
            member = CircuitMembership.objects.filter(id=member_id, circuit=circuit).first()
            if not member:
                messages.error(request, 'Member not found.')
                return redirect('dkp:auction_manage', auction_id=auction.id)

            # Refund previous winner if already awarded
            if auction.winner and auction.status == 'awarded':
                prev = auction.winner.member
                prev.current_dkp += auction.winner.bid_amount
                prev.lifetime_spent_dkp -= auction.winner.bid_amount
                prev.save(update_fields=['current_dkp', 'lifetime_spent_dkp'])
                DKPTransaction.objects.create(
                    raid=auction.raid,
                    member=prev,
                    item_name=auction.item_name,
                    amount=auction.winner.bid_amount,
                    transaction_type='adjustment',
                    transaction_notes='Refund: winner overridden by officer',
                    created_by=request.user,
                )

            # Find or create a bid for the override member at 0 cost
            override_amount = request.POST.get('override_amount', '0')
            try:
                override_amount = max(Decimal('0'), Decimal(override_amount))
            except Exception:
                override_amount = Decimal('0')

            # Reset all existing bids to lost before setting new winner
            Bid.objects.filter(auction=auction).update(status='lost')
            override_bid, _ = Bid.objects.get_or_create(
                auction=auction,
                member=member,
                defaults={
                    'bid_amount': override_amount,
                    'status': 'won',
                    'created_by': request.user,
                }
            )
            override_bid.bid_amount = override_amount
            override_bid.status = 'won'
            override_bid.save(update_fields=['bid_amount', 'status'])

            # Deduct DKP (0 by default unless bid existed)
            member.current_dkp -= override_bid.bid_amount
            member.lifetime_spent_dkp += override_bid.bid_amount
            member.save(update_fields=['current_dkp', 'lifetime_spent_dkp'])

            DKPTransaction.objects.create(
                raid=auction.raid,
                member=member,
                item_name=auction.item_name,
                amount=override_bid.bid_amount,
                transaction_type='spend',
                transaction_notes=f'Officer override: {reason}' if reason else 'Officer override',
                created_by=request.user,
            )

            auction.admin_override = member
            auction.override_reason = reason
            auction.winner = override_bid
            auction.status = 'awarded'
            auction.save(update_fields=['admin_override', 'override_reason', 'winner', 'status'])

            messages.success(request, f'Auction awarded to {member.display_name} via override.')
            return redirect('dkp:auction_manage', auction_id=auction.id)

        elif action == 'retract':
            auction.status = 'retracted'
            auction.save(update_fields=['status'])
            if auction.winner:
                # Refund DKP
                winner_membership = auction.winner.member
                winner_membership.current_dkp += auction.winner.bid_amount
                winner_membership.lifetime_spent_dkp -= auction.winner.bid_amount
                winner_membership.save(update_fields=['current_dkp', 'lifetime_spent_dkp'])
                DKPTransaction.objects.create(
                    raid=auction.raid,
                    member=winner_membership,
                    item_name=auction.item_name,
                    amount=auction.winner.bid_amount,
                    transaction_type='adjustment',
                    transaction_notes=f'Refund: auction retracted',
                    created_by=request.user,
                )
            messages.success(request, 'Auction retracted and DKP refunded.')
            return redirect('dkp:auction_manage', auction_id=auction.id)

        elif action == 'delete':
            raid_id = auction.raid_id
            auction.delete()
            messages.success(request, 'Auction deleted.')
            if raid_id:
                return redirect('dkp:raid_manage_detail', raid_id=raid_id)
            return redirect('dkp:raid_manage_list', circuit_id=circuit.id)

        elif action == 'dispute':
            auction.status = 'disputed'
            auction.save(update_fields=['status'])
            messages.success(request, 'Auction marked as disputed.')
            return redirect('dkp:auction_manage', auction_id=auction.id)

        elif action == 'resolve_dispute':
            auction.status = 'closed'
            auction.save(update_fields=['status'])
            messages.success(request,
                             'Dispute resolved — auction returned to closed status. You can now award or override.')
            return redirect('dkp:auction_manage', auction_id=auction.id)

    return render(request, 'dkp/auction_manage.html', {
        'auction': auction,
        'circuit': circuit,
        'members': members,
        'bids': bids,
    })


@officer_required
def raid_manage_list(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    from django.db.models import OuterRef, Subquery
    dkp_subq = DKPTransaction.objects.filter(
        raid=OuterRef('pk'), transaction_type='award'
    ).values('raid').annotate(total=Sum('amount')).values('total')
    raids = Raid.objects.filter(circuit=circuit).order_by('-date').annotate(
        attendee_count=Count('raidattendance', distinct=True),
        mob_count=Count('mobs', distinct=True),
        dkp_awarded=Subquery(dkp_subq),
        items_awarded=Count('auction',
                            filter=Q(auction__status='awarded'), distinct=True),
    )
    return render(request, 'dkp/raid_manage_list.html', {
        'circuit': circuit,
        'raids': raids,
    })


@officer_required
def raid_create(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    if request.method == 'POST':
        date = request.POST.get('date')
        labels = request.POST.get('labels', '')
        notes = request.POST.get('notes', '')
        is_private = request.POST.get('is_private') == 'on'
        if date:
            raid = Raid.objects.create(
                circuit=circuit,
                date=date,
                labels=labels,
                notes=notes,
                is_private=is_private,
                created_by=request.user,
            )
            messages.success(request, f'Raid created.')
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)
        else:
            messages.error(request, 'Date is required.')

    return render(request, 'dkp/raid_create.html', {'circuit': circuit})


@officer_required
def raid_manage_detail(request, raid_id):
    raid = Raid.objects.filter(id=raid_id).prefetch_related(
        'raidattendance_set__member', 'mobs'
    ).first()
    if not raid:
        raise Http404
    if not get_officer_membership(request.user, raid.circuit):
        raise Http404

    all_members = CircuitMembership.objects.filter(
        circuit=raid.circuit, status='active'
    ).order_by('display_name')

    # Bulk-compute RA% for all members (2 queries)
    _config = getattr(raid.circuit, 'circuitconfig', None)
    _window = _config.attendance_window_days if _config else 90
    _cutoff = timezone.now() - timedelta(days=_window)
    _total_raids = Raid.objects.filter(circuit=raid.circuit, date__gte=_cutoff).count()
    _attended = dict(
        RaidAttendance.objects.filter(
            member__in=all_members,
            raid__date__gte=_cutoff,
            raid__circuit=raid.circuit,
        ).exclude(attendance_status='absent').values('member_id').annotate(
            n=Count('id')
        ).values_list('member_id', 'n')
    )
    member_ra = {
        m.id: round(_attended.get(m.id, 0) / _total_raids * 100, 1) if _total_raids else 0.0
        for m in all_members
    }

    attendance_map = {
        str(a.member_id): a for a in raid.raidattendance_set.all()
    }

    circuit_mobs = Mob.objects.filter(circuit=raid.circuit, is_active=True).order_by('name')
    raid_mobs = raid.mobs.all()
    auctions = Auction.objects.filter(raid=raid).annotate(
        bid_count=Count('bid')
    ).order_by('-opened_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_attendance':
            checked_ids = set(int(x) for x in request.POST.getlist('attendees'))
            status_map = {}
            notes_map = {}
            for key, val in request.POST.items():
                if key.startswith('status_'):
                    mid = int(key.split('_')[1])
                    status_map[mid] = val
                if key.startswith('notes_'):
                    mid = int(key.split('_')[1])
                    notes_map[mid] = val
            RaidAttendance.objects.filter(
                raid=raid
            ).exclude(member_id__in=checked_ids).delete()
            for mid in checked_ids:
                status = status_map.get(mid, 'present')
                notes = notes_map.get(mid, '')
                RaidAttendance.objects.update_or_create(
                    raid=raid, member_id=mid,
                    defaults={'attendance_status': status, 'attendance_notes': notes}
                )
            messages.success(request, 'Attendance saved.')
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)

        elif action == 'save_mobs':
            mob_ids = set(int(x) for x in request.POST.getlist('mobs'))
            raid.mobs.set(mob_ids)
            snapshot = {str(m.id): str(m.dkp) for m in Mob.objects.filter(id__in=mob_ids)}
            raid.mob_dkp_snapshot = snapshot
            raid.save(update_fields=['mob_dkp_snapshot'])
            messages.success(request, 'Mobs updated.')
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)

        elif action == 'toggle_private':
            raid.is_private = not raid.is_private
            raid.save(update_fields=['is_private'])
            messages.success(request, f'Raid is now {"private" if raid.is_private else "public"}.')
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)

        elif action == 'create_auction':
            item_name = request.POST.get('item_name', '').strip()
            if item_name:
                Auction.objects.create(
                    raid=raid,
                    circuit=raid.circuit,
                    item_name=item_name,
                    status='pending',
                    created_by=request.user,
                )
                messages.success(request, f'Auction created for {item_name}.')
            else:
                messages.error(request, 'Item name is required.')
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)

        elif action == 'open_auction':
            auction_id = request.POST.get('auction_id')
            Auction.objects.filter(id=auction_id, raid=raid).update(status='open')
            messages.success(request, 'Auction opened.')
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)

        elif action == 'close_auction':
            auction_id = request.POST.get('auction_id')
            auction = Auction.objects.filter(id=auction_id, raid=raid).first()
            if auction:
                from dkp.services import resolve_auction
                resolve_auction(auction)
                messages.success(request, 'Auction closed and winner resolved.')
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)

        elif action == 'award_auction':
            auction_id = request.POST.get('auction_id')
            auction = Auction.objects.filter(id=auction_id, raid=raid).first()
            if auction:
                from dkp.services import award_auction
                try:
                    award_auction(auction, created_by=request.user)
                    messages.success(request, 'Auction awarded.')
                except Exception as e:
                    messages.error(request, str(e))
            return redirect('dkp:raid_manage_detail', raid_id=raid.id)

        elif action == 'confirm_mob_award':
            mob_id = request.POST.get('mob_id')
            mob = Mob.objects.filter(id=mob_id, circuit=raid.circuit).first()
            if mob:
                awarded = list(raid.mobs_awarded or [])
                if mob.id in awarded:
                    messages.error(request, f'DKP already awarded for {mob.name}.')
                else:
                    # Handle late arrivals — create their base RaidAttendance first
                    late_arrival_ids = [int(x) for x in request.POST.getlist('late_arrival')]
                    newly_added_ids = []
                    for mid in late_arrival_ids:
                        status = request.POST.get(f'mob_status_{mid}', 'late')
                        notes = request.POST.get(f'mob_notes_{mid}', '')
                        _, created = RaidAttendance.objects.get_or_create(
                            raid=raid, member_id=mid,
                            defaults={'attendance_status': status, 'attendance_notes': notes},
                        )
                        if created:
                            newly_added_ids.append(mid)

                    member_ids = [int(x) for x in request.POST.getlist('kill_attendees')]
                    for mid in member_ids:
                        RaidMobAttendance.objects.get_or_create(raid=raid, mob=mob, member_id=mid)

                    from dkp.services import award_dkp
                    txn_ids = award_dkp(raid, mob, member_ids=member_ids)

                    awarded.append(mob.id)
                    raid.mobs_awarded = awarded
                    raid.save(update_fields=['mobs_awarded'])

                    # Save status/notes for members unchecked from this kill
                    kill_attendee_ids = set(member_ids)
                    for attendance in raid.raidattendance_set.exclude(attendance_status='absent').all():
                        if attendance.member_id not in kill_attendee_ids and attendance.member_id not in late_arrival_ids:
                            new_status = request.POST.get(f'mob_status_{attendance.member_id}')
                            new_notes = request.POST.get(f'mob_notes_{attendance.member_id}', attendance.attendance_notes)
                            if new_status:
                                attendance.attendance_status = new_status
                                attendance.attendance_notes = new_notes
                                attendance.save(update_fields=['attendance_status', 'attendance_notes'])

                    # Store undo data in session for this page load
                    request.session[f'undo_mob_{raid.id}_{mob.id}'] = {
                        'txn_ids': txn_ids,
                        'new_attendance_ids': newly_added_ids,
                        'mob_name': mob.name,
                    }
                    messages.success(request, f'DKP awarded to {len(member_ids)} members for {mob.name}.')
            from django.urls import reverse
            undo_param = f'&undo={mob.id}' if mob else ''
            return redirect(reverse('dkp:raid_manage_detail', kwargs={'raid_id': raid.id}) + f'?tab=mobs{undo_param}')

        elif action == 'undo_mob_award':
            mob_id = request.POST.get('mob_id')
            mob = Mob.objects.filter(id=mob_id, circuit=raid.circuit).first()
            if mob:
                session_key = f'undo_mob_{raid.id}_{mob.id}'
                undo_data = request.session.pop(session_key, None)
                if undo_data:
                    from django.db import transaction as db_transaction
                    with db_transaction.atomic():
                        for txn in DKPTransaction.objects.filter(id__in=undo_data['txn_ids']).select_related('member'):
                            txn.member.current_dkp -= txn.amount
                            txn.member.lifetime_earned_dkp -= txn.amount
                            txn.member.save(update_fields=['current_dkp', 'lifetime_earned_dkp'])
                        DKPTransaction.objects.filter(id__in=undo_data['txn_ids']).delete()
                        RaidMobAttendance.objects.filter(raid=raid, mob=mob).delete()
                        if undo_data.get('new_attendance_ids'):
                            RaidAttendance.objects.filter(
                                raid=raid, member_id__in=undo_data['new_attendance_ids']
                            ).delete()
                        awarded = list(raid.mobs_awarded or [])
                        if mob.id in awarded:
                            awarded.remove(mob.id)
                        raid.mobs_awarded = awarded
                        raid.save(update_fields=['mobs_awarded'])
                        cache.delete(f'dkp:standings:{raid.circuit_id}')
                    messages.success(request, f'DKP award for {mob.name} has been undone.')
                else:
                    messages.error(request, 'Undo is no longer available for this award.')
            from django.urls import reverse
            return redirect(reverse('dkp:raid_manage_detail', kwargs={'raid_id': raid.id}) + '?tab=mobs')

        elif action == 'add_mob_credits':
            mob_id = request.POST.get('mob_id')
            mob = Mob.objects.filter(id=mob_id, circuit=raid.circuit).first()
            if mob:
                credit_ids = [int(x) for x in request.POST.getlist('credit_members')]
                added = 0
                for mid in credit_ids:
                    _, created = RaidMobAttendance.objects.get_or_create(raid=raid, mob=mob, member_id=mid)
                    if created:
                        added += 1
                messages.success(request, f'Added kill credit for {added} member(s) on {mob.name}.')
            from django.urls import reverse
            return redirect(reverse('dkp:raid_manage_detail', kwargs={'raid_id': raid.id}) + '?tab=mobs')

    mobs_awarded = list(raid.mobs_awarded or [])
    total_awarded = len(mobs_awarded)
    mob_kill_counts = {}
    mob_credited = {}
    mob_uncredited = {}
    if total_awarded:
        from django.db.models import Count as _Count
        kill_qs = RaidMobAttendance.objects.filter(raid=raid).values('member_id').annotate(kills=_Count('mob'))
        mob_kill_counts = {str(row['member_id']): row['kills'] for row in kill_qs}
        for rma in RaidMobAttendance.objects.filter(raid=raid, mob_id__in=mobs_awarded):
            mob_credited.setdefault(str(rma.mob_id), set()).add(rma.member_id)
        attending_ids = set(
            raid.raidattendance_set.exclude(attendance_status='absent').values_list('member_id', flat=True)
        )
        for mid in mobs_awarded:
            credited_ids = mob_credited.get(str(mid), set())
            uncredited_ids = attending_ids - credited_ids
            if uncredited_ids:
                mob_uncredited[str(mid)] = list(
                    CircuitMembership.objects.filter(id__in=uncredited_ids).order_by('display_name')
                )

    # Check if undo is available for the most recently awarded mob
    undo_mob_id = None
    undo_mob_name = None
    undo_param = request.GET.get('undo')
    if undo_param:
        try:
            undo_mid = int(undo_param)
            session_key = f'undo_mob_{raid.id}_{undo_mid}'
            if session_key in request.session:
                undo_mob_id = undo_mid
                undo_mob_name = request.session[session_key].get('mob_name', '')
        except (ValueError, TypeError):
            pass

    return render(request, 'dkp/raid_manage_detail.html', {
        'raid': raid,
        'circuit': raid.circuit,
        'all_members': all_members,
        'attendance_map': attendance_map,
        'circuit_mobs': circuit_mobs,
        'raid_mobs': raid_mobs,
        'auctions': auctions,
        'mobs_awarded': mobs_awarded,
        'total_awarded': total_awarded,
        'mob_kill_counts': mob_kill_counts,
        'mob_credited': mob_credited,
        'mob_uncredited': mob_uncredited,
        'undo_mob_id': undo_mob_id,
        'undo_mob_name': undo_mob_name,
        'member_ra': member_ra,
    })


@officer_required
def raid_delete(request, raid_id):
    raid = Raid.objects.filter(id=raid_id).first()
    if not raid:
        raise Http404
    circuit_id = raid.circuit_id
    if request.method == 'POST':
        raid.delete()
        messages.success(request, 'Raid deleted.')
        return redirect('dkp:raid_manage_list', circuit_id=circuit_id)
    return render(request, 'dkp/raid_delete_confirm.html', {
        'raid': raid,
        'circuit': raid.circuit,
    })

@login_required
def dashboard(request, membership_id=None):
    if membership_id:
        membership = CircuitMembership.objects.filter(id=membership_id).select_related('circuit', 'member').first()
        if not membership:
            raise Http404
    else:
        membership = CircuitMembership.objects.filter(
            member=request.user, status='active'
        ).select_related('circuit').first()
        if not membership:
            return render(request, 'dkp/dashboard.html', {'no_membership': True})

    # Resolve viewer context early so everything below can use it
    viewer_membership = CircuitMembership.objects.filter(
        circuit=membership.circuit, member=request.user
    ).first()
    is_officer = viewer_membership and viewer_membership.role == 'officer'
    is_own = membership.member == request.user

    if not is_own and not is_officer and membership.hide_dashboard:
        raise Http404

    # All memberships for circuit selector
    all_memberships = CircuitMembership.objects.filter(
        member=membership.member, status='active'
    ).select_related('circuit')

    # Handle privacy toggle
    if is_own:
        if 'hide_dashboard' in request.GET:
            membership.hide_dashboard = True
            membership.save(update_fields=['hide_dashboard'])
            return redirect('dkp:dashboard')
        elif 'show_dashboard' in request.GET:
            membership.hide_dashboard = False
            membership.save(update_fields=['hide_dashboard'])
            return redirect('dkp:dashboard')

    # Handle circuit selector
    circuit_id = request.GET.get('circuit')
    if circuit_id and not membership_id:
        target = CircuitMembership.objects.filter(
            id=circuit_id, member=request.user
        ).first()
        if target:
            return redirect('dkp:dashboard_member', membership_id=target.id)

    transactions = DKPTransaction.objects.filter(
        member=membership
    ).order_by('-transaction_date')[:20]

    active_auctions = Auction.objects.filter(
        status__in=['open', 'pending'],
        circuit=membership.circuit
    ).order_by('-opened_at')[:10]

    active_bids = Bid.objects.filter(
        member=membership, status='active'
    ).select_related('auction').order_by('-submitted_at')

    attendance = attendance_calculation(membership)

    # --- DKP balance chart (reconstruct history backwards from current_dkp) ---
    _all_txns = list(DKPTransaction.objects.filter(
        member=membership
    ).order_by('transaction_date', 'id'))
    _bal = float(membership.current_dkp)
    _points = []
    for tx in reversed(_all_txns):
        _points.append((tx.transaction_date, round(_bal, 1)))
        if tx.transaction_type == 'spend':
            _bal += float(tx.amount)
        else:
            _bal -= float(tx.amount)
    _points.reverse()  # chronological; _bal is now the pre-all-time balance

    _chart_cutoff = _att_cutoff
    _pre_window_bal = round(_bal, 1)
    for _d, _b in _points:
        if _d < _chart_cutoff:
            _pre_window_bal = _b

    _in_window = [{'x': _d.strftime('%Y-%m-%d'), 'y': _b} for _d, _b in _points if _d >= _chart_cutoff]
    dkp_chart_json = json.dumps(
        [{'x': _chart_cutoff.strftime('%Y-%m-%d'), 'y': _pre_window_bal}]
        + _in_window
        + [{'x': timezone.now().strftime('%Y-%m-%d'), 'y': float(membership.current_dkp)}]
    )

    _circuit_config = getattr(membership.circuit, 'circuitconfig', None)
    dkp_cap = float(_circuit_config.dkp_cap) if _circuit_config else None

    # --- Attendance dots (one per raid in window, green=attended, grey=missed) ---
    _att_window = _circuit_config.attendance_window_days if _circuit_config else 90
    _att_cutoff = timezone.now() - timedelta(days=_att_window)
    _window_raids = list(Raid.objects.filter(
        circuit=membership.circuit, date__gte=_att_cutoff
    ).order_by('date'))
    _attended_ids = set(RaidAttendance.objects.filter(
        member=membership, raid__in=_window_raids
    ).exclude(attendance_status='absent').values_list('raid_id', flat=True))
    attendance_dots = [
        {'date': r.date.strftime('%b %d'), 'attended': r.id in _attended_ids}
        for r in _window_raids
    ]

    context = {
        'membership': membership,
        'all_memberships': all_memberships,
        'transactions': transactions,
        'active_auctions': active_auctions,
        'active_bids': active_bids,
        'attendance': attendance,
        'attendance_dots': attendance_dots,
        'dkp_chart_json': dkp_chart_json,
        'dkp_cap': dkp_cap,
        'is_officer': is_officer,
        'is_own': is_own,
    }
    return render(request, 'dkp/dashboard.html', context)


def standings(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    join_status = 'none'
    if request.user.is_authenticated:
        membership = CircuitMembership.objects.filter(
            circuit=circuit, member=request.user
        ).first()
        if membership:
            join_status = membership.status  # 'active', 'pending', 'inactive'

    # Don't show join banner for active members
    if join_status == 'active':
        join_status = 'member'

    is_officer = False
    if request.user.is_authenticated:
        viewer = CircuitMembership.objects.filter(
            circuit=circuit, member=request.user
        ).first()
        is_officer = bool(viewer and viewer.role == 'officer')

    standings_data = get_standings(circuit_id)
    return render(request, 'dkp/standings.html', {
        'circuit': circuit,
        'standings': standings_data,
        'join_status': join_status,
        'is_officer': is_officer,
    })

def raid_list(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    is_member = request.user.is_authenticated and CircuitMembership.objects.filter(
        circuit=circuit, member=request.user, status='active'
    ).exists()

    from django.db.models import OuterRef, Subquery
    dkp_subq = DKPTransaction.objects.filter(
        raid=OuterRef('pk'), transaction_type='award'
    ).values('raid').annotate(total=Sum('amount')).values('total')
    raids = Raid.objects.filter(circuit=circuit).order_by('-date').annotate(
        attendee_count=Count('raidattendance', distinct=True),
        mob_count=Count('mobs', distinct=True),
        dkp_awarded=Subquery(dkp_subq),
        items_awarded=Count('auction',
                           filter=Q(auction__status='awarded'), distinct=True),
    )
    if not is_member:
        raids = raids.filter(is_private=False)

    return render(request, 'dkp/raid_list.html', {
        'circuit': circuit,
        'raids': raids,
        'is_member': is_member,
    })

def raid_detail(request, raid_id):
    raid = Raid.objects.filter(id=raid_id).prefetch_related(
        'raidattendance_set__member',
        'mobs',
        'auction_set__winner__member',
    ).first()
    if not raid:
        raise Http404

    is_member = request.user.is_authenticated and CircuitMembership.objects.filter(
        circuit=raid.circuit, member=request.user, status='active'
    ).exists()

    if raid.is_private and not is_member:
        raise Http404

    viewer_membership = None
    is_officer = False
    if request.user.is_authenticated:
        viewer_membership = CircuitMembership.objects.filter(
            circuit=raid.circuit, member=request.user
        ).first()
        is_officer = viewer_membership and viewer_membership.role == 'officer'

    attendees = raid.raidattendance_set.select_related('member').order_by('member__display_name')
    mobs = raid.mobs.all()
    auctions = Auction.objects.filter(raid=raid).select_related('winner__member').order_by('-opened_at')
    transactions = DKPTransaction.objects.filter(raid=raid).select_related('member').order_by('-transaction_date')

    return render(request, 'dkp/raid_detail.html', {
        'raid': raid,
        'circuit': raid.circuit,
        'attendees': attendees,
        'mobs': mobs,
        'auctions': auctions,
        'transactions': transactions,
        'is_member': is_member,
        'is_officer': is_officer,
    })


def transaction_history(request, membership_id):
    membership = CircuitMembership.objects.filter(id=membership_id).select_related('circuit', 'member').first()
    if not membership:
        raise Http404

    viewer_membership = None
    is_officer = False
    if request.user.is_authenticated:
        viewer_membership = CircuitMembership.objects.filter(
            circuit=membership.circuit, member=request.user
        ).first()
        is_officer = bool(viewer_membership and viewer_membership.role == 'officer')

    is_own = request.user.is_authenticated and membership.member == request.user

    if not is_own and not is_officer:
        raise Http404

    transactions = DKPTransaction.objects.filter(
        member=membership
    ).select_related('raid').order_by('-transaction_date')

    return render(request, 'dkp/transaction_history.html', {
        'membership': membership,
        'circuit': membership.circuit,
        'transactions': transactions,
        'is_own': is_own,
        'is_officer': is_officer,
    })


@officer_required
def member_list(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    if request.method == 'POST':
        action = request.POST.get('action')
        member_id = request.POST.get('member_id')
        membership = CircuitMembership.objects.filter(id=member_id, circuit=circuit).first()

        if not membership:
            messages.error(request, 'Member not found.')
            return redirect('dkp:member_list', circuit_id=circuit_id)

        if action == 'approve':
            membership.status = 'active'
            membership.save(update_fields=['status'])
            cache.delete(f'dkp:standings:{circuit_id}')
            messages.success(request, f'{membership.display_name} approved.')

        elif action == 'deactivate':
            membership.status = 'inactive'
            membership.save(update_fields=['status'])
            messages.success(request, f'{membership.display_name} deactivated.')

        elif action == 'reactivate':
            membership.status = 'active'
            membership.save(update_fields=['status'])
            messages.success(request, f'{membership.display_name} reactivated.')

        elif action == 'set_role':
            role = request.POST.get('role')
            if role in ('officer', 'member'):
                membership.role = role
                membership.save(update_fields=['role'])
                messages.success(request, f'{membership.display_name} role updated.')

        elif action == 'set_display_name':
            display_name = request.POST.get('display_name', '').strip()
            if display_name:
                membership.display_name = display_name
                membership.save(update_fields=['display_name'])
                messages.success(request, f'Display name updated.')
            else:
                messages.error(request, 'Display name cannot be empty.')

        elif action == 'remove':
            name = membership.display_name
            membership.delete()
            messages.success(request, f'{name} removed from circuit.')

        return redirect('dkp:member_list', circuit_id=circuit_id)

    active_members = CircuitMembership.objects.filter(
        circuit=circuit, status='active'
    ).order_by('display_name')

    inactive_members = CircuitMembership.objects.filter(
        circuit=circuit, status='inactive'
    ).order_by('display_name')

    pending_members = CircuitMembership.objects.filter(
        circuit=circuit, status='pending'
    ).order_by('joined_at')

    # Attach attendance to active members
    from dkp.services import attendance_calculation
    active_with_attendance = [
        (m, attendance_calculation(m)) for m in active_members
    ]

    return render(request, 'dkp/member_list.html', {
        'circuit': circuit,
        'active_with_attendance': active_with_attendance,
        'inactive_members': inactive_members,
        'pending_members': pending_members,
        'pending_count': pending_members.count(),
    })

@officer_required
def mob_manage(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    if request.method == 'POST':
        action = request.POST.get('action')
        mob_id = request.POST.get('mob_id')

        if action == 'add':
            name = request.POST.get('name', '').strip()
            dkp = request.POST.get('dkp', '0')
            try:
                dkp = Decimal(dkp)
            except InvalidOperation:
                messages.error(request, 'Invalid DKP value.')
                return redirect('dkp:mob_manage', circuit_id=circuit_id)
            if name:
                count = min(max(int(request.POST.get('count', 1) or 1), 1), 5)
                for i in range(count):
                    mob_name = name if i == 0 else f'{name} #{i + 1}'
                    Mob.objects.create(circuit=circuit, name=mob_name, dkp=dkp)
                messages.success(request, f'Added {count} mob(s): {name}.')
            else:
                messages.error(request, 'Mob name is required.')

        elif action == 'edit':
            mob = Mob.objects.filter(id=mob_id, circuit=circuit).first()
            if mob:
                try:
                    mob.dkp = Decimal(request.POST.get('dkp', mob.dkp))
                    mob.name = request.POST.get('name', mob.name).strip()
                    mob.save()
                    messages.success(request, f'{mob.name} updated.')
                except InvalidOperation:
                    messages.error(request, 'Invalid DKP value.')

        elif action == 'deactivate':
            mob = Mob.objects.filter(id=mob_id, circuit=circuit).first()
            if mob:
                mob.is_active = False
                mob.save(update_fields=['is_active'])
                messages.success(request, f'{mob.name} deactivated.')

        elif action == 'reactivate':
            mob = Mob.objects.filter(id=mob_id, circuit=circuit).first()
            if mob:
                mob.is_active = True
                mob.save(update_fields=['is_active'])
                messages.success(request, f'{mob.name} reactivated.')

        elif action == 'link_npc':
            mob = Mob.objects.filter(id=mob_id, circuit=circuit).first()
            if mob:
                npc_id = request.POST.get('npc_id', '').strip()
                npc_name = request.POST.get('npc_name', '').strip()
                mob.npc_id = int(npc_id) if npc_id else None
                mob.npc_name = npc_name if npc_id else ''
                mob.save(update_fields=['npc_id', 'npc_name'])
                if npc_id:
                    messages.success(request, f'{mob.name} linked to {npc_name}.')
                else:
                    messages.success(request, f'{mob.name} NPC link removed.')
            return JsonResponse({'ok': True})

        return redirect('dkp:mob_manage', circuit_id=circuit_id)

    active_mobs = Mob.objects.filter(circuit=circuit, is_active=True).order_by('name')
    inactive_mobs = Mob.objects.filter(circuit=circuit, is_active=False).order_by('name')

    return render(request, 'dkp/mob_manage.html', {
        'circuit': circuit,
        'active_mobs': active_mobs,
        'inactive_mobs': inactive_mobs,
    })


@officer_required
def npc_search(request, circuit_id):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    from common.models.npcs import NPCTypes
    npcs = NPCTypes.objects.using('game_database').filter(
        name__icontains=q, loottable_id__gt=0
    ).values('id', 'name')[:20]
    return JsonResponse({'results': list(npcs)})


@officer_required
def mob_loot_items(request, circuit_id, mob_id):
    mob = Mob.objects.filter(id=mob_id, circuit_id=circuit_id).first()
    if not mob or not mob.npc_id:
        return JsonResponse({'items': []})
    from django.db import connections
    with connections['game_database'].cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT i.id, i.Name
            FROM npc_types npc
            JOIN loottable_entries lte ON lte.loottable_id = npc.loottable_id
            JOIN lootdrop_entries lde ON lde.lootdrop_id = lte.lootdrop_id
            JOIN items i ON i.id = lde.item_id
            WHERE npc.id = %s
            ORDER BY i.Name
        """, [mob.npc_id])
        rows = cursor.fetchall()
    return JsonResponse({'items': [{'id': r[0], 'name': r[1]} for r in rows]})


@officer_required
@require_POST
def direct_award_view(request, raid_id):
    from dkp.services import direct_award as _direct_award
    raid = Raid.objects.filter(id=raid_id).select_related('circuit').first()
    if not raid:
        raise Http404
    item_name = request.POST.get('item_name', '').strip()
    item_id_str = request.POST.get('item_id', '').strip()
    member_id = request.POST.get('member_id', '').strip()
    amount_str = request.POST.get('amount', '0').strip()

    loot_redirect = f'/dkp/manage/raid/{raid_id}/?tab=loot'

    if not item_name:
        messages.error(request, 'Item name is required.')
        return redirect(loot_redirect)

    try:
        amount = Decimal(amount_str)
    except InvalidOperation:
        messages.error(request, 'Invalid DKP amount.')
        return redirect(loot_redirect)

    member = CircuitMembership.objects.filter(
        id=member_id, circuit=raid.circuit, status='active'
    ).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect(loot_redirect)

    if amount > member.current_dkp:
        messages.error(request, f'{member.display_name} only has {member.current_dkp} DKP.')
        return redirect(loot_redirect)

    item_id = int(item_id_str) if item_id_str.isdigit() else None
    _direct_award(
        raid=raid,
        circuit=raid.circuit,
        item_name=item_name,
        item_id=item_id,
        member=member,
        amount=amount,
        created_by=request.user,
    )
    messages.success(request, f'{item_name} awarded to {member.display_name} for {amount} DKP.')
    return redirect(loot_redirect)


@officer_required
def circuit_adjustments(request, circuit_id):
    circuit = RaidCircuit.objects.filter(id=circuit_id).first()
    if not circuit:
        raise Http404

    if request.method == 'POST':
        action = request.POST.get('action')
        amount_str = request.POST.get('amount', '0').strip()
        note = request.POST.get('note', '').strip()

        if not note:
            messages.error(request, 'A reason is required for all adjustments.')
            return redirect('dkp:circuit_adjustments', circuit_id=circuit_id)

        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            messages.error(request, 'Invalid amount.')
            return redirect('dkp:circuit_adjustments', circuit_id=circuit_id)

        if action == 'individual':
            member = CircuitMembership.objects.filter(
                id=request.POST.get('member_id'), circuit=circuit, status='active'
            ).first()
            if not member:
                messages.error(request, 'Member not found.')
                return redirect('dkp:circuit_adjustments', circuit_id=circuit_id)
            new_dkp = member.current_dkp + amount
            config = getattr(circuit, 'circuitconfig', None)
            max_dkp = (config.dkp_cap + config.dkp_overcap) if config else None
            member.current_dkp = new_dkp
            member.save(update_fields=['current_dkp'])
            DKPTransaction.objects.create(
                member=member,
                amount=amount,
                transaction_type='adjustment',
                transaction_notes=note,
                created_by=request.user,
            )
            cache.delete(f'dkp:standings:{circuit_id}')
            if max_dkp is not None and new_dkp > max_dkp:
                messages.warning(request, f'Adjusted {member.display_name} by {amount:+g} DKP — new total {new_dkp} exceeds the cap ({config.dkp_cap} + {config.dkp_overcap} overcap = {max_dkp}).')
            else:
                messages.success(request, f'Adjusted {member.display_name} by {amount:+g} DKP.')

        elif action == 'raid':
            raid = Raid.objects.filter(id=request.POST.get('raid_id'), circuit=circuit).first()
            if not raid:
                messages.error(request, 'Raid not found.')
                return redirect('dkp:circuit_adjustments', circuit_id=circuit_id)
            attendances = RaidAttendance.objects.filter(
                raid=raid
            ).exclude(attendance_status='absent').select_related('member')
            count = 0
            for attendance in attendances:
                member = attendance.member
                member.current_dkp += amount
                member.save(update_fields=['current_dkp'])
                DKPTransaction.objects.create(
                    raid=raid,
                    member=member,
                    amount=amount,
                    transaction_type='adjustment',
                    transaction_notes=note,
                    created_by=request.user,
                )
                count += 1
            cache.delete(f'dkp:standings:{circuit_id}')
            messages.success(request, f'Adjusted {count} attendees by {amount:+g} DKP.')

        return redirect('dkp:circuit_adjustments', circuit_id=circuit_id)

    members = CircuitMembership.objects.filter(
        circuit=circuit, status='active'
    ).order_by('display_name')
    raids = Raid.objects.filter(circuit=circuit).order_by('-date')[:50]

    config = getattr(circuit, 'circuitconfig', None)
    return render(request, 'dkp/circuit_adjustments.html', {
        'circuit': circuit,
        'members': members,
        'raids': raids,
        'config': config,
    })
