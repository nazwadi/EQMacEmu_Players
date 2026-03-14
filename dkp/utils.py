from django.core.cache import cache
from dkp.models import CircuitMembership
from dkp.services import attendance_calculation

STANDINGS_CACHE_TIMEOUT = 300  # 5 minutes - adjust as needed


def get_standings(circuit_id):
    cache_key = f'dkp:standings:{circuit_id}'

    # Check cache first
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Cache miss - build standings
    memberships = CircuitMembership.objects.filter(
        circuit_id=circuit_id,
        status='active'
    ).select_related('member').order_by('-current_dkp')

    standings = []
    for membership in memberships:
        standings.append({
            'id': membership.id,
            'display_name': membership.display_name if membership.display_name else membership.member.username,  # use display_name if set, else username
            'current_dkp': membership.current_dkp,
            'lifetime_earned_dkp': membership.lifetime_earned_dkp,
            'lifetime_spent_dkp': membership.lifetime_spent_dkp,
            'attendance': attendance_calculation(membership),  # call attendance_calculation here
            'status': membership.status,
            'hide_dashboard': membership.hide_dashboard,
        })

    # Store in cache
    cache.set(cache_key, standings, STANDINGS_CACHE_TIMEOUT)
    return standings