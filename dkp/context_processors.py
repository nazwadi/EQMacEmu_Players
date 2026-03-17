from dkp.models import CircuitMembership, RaidCircuit, CircuitRequest, Raid, Auction


def _int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def dkp_context(request):
    if not request.user.is_authenticated:
        return {
            'dkp_membership': None, 'dkp_is_officer': False, 'dkp_circuits': [],
            'dkp_pending_count': 0, 'can_approve_circuits': False,
            'pending_circuit_requests': 0, 'active_circuit': None,
            'active_circuit_membership': None,
        }

    memberships = CircuitMembership.objects.filter(
        member=request.user, status='active'
    ).select_related('circuit')

    membership_list = list(memberships)
    is_officer = any(m.role == 'officer' for m in membership_list)
    officer_circuit_ids = set(m.circuit_id for m in membership_list if m.role == 'officer')
    circuits = [m.circuit for m in membership_list]
    circuits_with_membership = [{'circuit': m.circuit, 'membership': m} for m in membership_list]

    # Build lookup maps from already-fetched memberships (no extra queries)
    membership_by_circuit = {m.circuit_id: m for m in membership_list}
    membership_by_id = {m.id: m for m in membership_list}

    # Resolve active circuit from URL kwargs — handles circuit_id, membership_id,
    # raid_id, and auction_id so switching circuits persists across all DKP pages
    active_circuit_membership = None
    try:
        kwargs = request.resolver_match.kwargs
    except AttributeError:
        kwargs = {}

    url_circuit_id = _int(kwargs.get('circuit_id'))
    if url_circuit_id:
        active_circuit_membership = membership_by_circuit.get(url_circuit_id)

    if not active_circuit_membership:
        url_membership_id = _int(kwargs.get('membership_id'))
        if url_membership_id:
            active_circuit_membership = membership_by_id.get(url_membership_id)

    if not active_circuit_membership:
        url_raid_id = _int(kwargs.get('raid_id'))
        if url_raid_id:
            cid = Raid.objects.filter(pk=url_raid_id).values_list('circuit_id', flat=True).first()
            if cid:
                active_circuit_membership = membership_by_circuit.get(cid)

    if not active_circuit_membership:
        url_auction_id = _int(kwargs.get('auction_id'))
        if url_auction_id:
            cid = Auction.objects.filter(pk=url_auction_id).values_list('circuit_id', flat=True).first()
            if cid:
                active_circuit_membership = membership_by_circuit.get(cid)

    if not active_circuit_membership and membership_list:
        active_circuit_membership = membership_list[0]

    active_circuit = active_circuit_membership.circuit if active_circuit_membership else None

    pending_count = 0
    if is_officer:
        pending_count = CircuitMembership.objects.filter(
            circuit__in=circuits, status='pending'
        ).count()

    can_approve = request.user.is_superuser or request.user.has_perm('dkp.approve_circuit_request')
    pending_circuit_requests = 0
    if can_approve:
        pending_circuit_requests = CircuitRequest.objects.filter(status='pending').count()

    return {
        'dkp_membership': membership_list[0] if membership_list else None,
        'dkp_is_officer': is_officer,
        'dkp_circuits': circuits,
        'dkp_circuits_with_membership': circuits_with_membership,
        'dkp_memberships': memberships,
        'dkp_pending_count': pending_count,
        'officer_circuit_ids': officer_circuit_ids,
        'can_approve_circuits': can_approve,
        'pending_circuit_requests': pending_circuit_requests,
        'active_circuit': active_circuit,
        'active_circuit_membership': active_circuit_membership,
    }
