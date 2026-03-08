from dkp.models import CircuitMembership, RaidCircuit

def dkp_context(request):
    if not request.user.is_authenticated:
        return {'dkp_membership': None, 'dkp_is_officer': False, 'dkp_circuits': [], 'dkp_pending_count': 0}

    memberships = CircuitMembership.objects.filter(
        member=request.user, status='active'
    ).select_related('circuit')

    is_officer = any(m.role == 'officer' for m in memberships)
    officer_circuit_ids = set(
        m.circuit_id for m in memberships if m.role == 'officer'
    )
    circuits = [m.circuit for m in memberships]
    active_membership = memberships.first()

    pending_count = 0
    if is_officer:
        pending_count = CircuitMembership.objects.filter(
            circuit__in=circuits, status='pending'
        ).count()

    return {
        'dkp_membership': active_membership,
        'dkp_is_officer': is_officer,
        'dkp_circuits': circuits,
        'dkp_memberships': memberships,
        'dkp_pending_count': pending_count,
        'officer_circuit_ids': officer_circuit_ids,
    }