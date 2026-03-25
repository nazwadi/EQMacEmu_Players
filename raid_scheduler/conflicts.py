"""Conflict-check logic, separated so views and AJAX can share it."""
from datetime import datetime

from dkp.models import CircuitMembership

from .models import RaidEvent

_ACTIVE = ('scheduled', 'active')


def check_conflicts(targets, event_date, start_time, is_visible, circuit, exclude_pk=None):
    """
    Returns (hard_conflicts, soft_warnings).

    `targets` — iterable of RaidTarget instances to check.

    Rules
    -----
    Any new event:
        Hard block if another VISIBLE event already holds ANY of the same targets on the same day.

    Any new event additionally:
        Soft warn if any visible event on the same day overlaps in time (<2 h apart)
        and the two circuits share active roster members.

    Write-in circuits (circuit=None) produce no soft warnings (no roster to compare).
    """
    hard_conflicts = []
    soft_warnings = []

    targets = list(targets)
    if not targets:
        return hard_conflicts, soft_warnings

    # ── Hard block ────────────────────────────────────────────────────────────
    blocking_qs = RaidEvent.objects.filter(
        targets__in=targets,
        date=event_date,
        is_visible=True,
        status__in=_ACTIVE,
    ).distinct().select_related('circuit')
    if exclude_pk:
        blocking_qs = blocking_qs.exclude(pk=exclude_pk)

    for ev in blocking_qs:
        # Find which of our targets overlap
        ev_target_ids = set(ev.targets.values_list('id', flat=True))
        clashing = [t for t in targets if t.pk in ev_target_ids]
        names = ', '.join(t.name for t in clashing)
        hard_conflicts.append(
            f"{ev.circuit_display} has already publicly reserved "
            f"{names} on {event_date.strftime('%A, %b %-d')}. "
            f"Contact a GM to resolve this conflict."
        )

    if hard_conflicts:
        return hard_conflicts, soft_warnings

    # ── Soft warning (roster overlap + time overlap vs public raids) ───────────
    if not circuit:
        return hard_conflicts, soft_warnings

    same_day_public = RaidEvent.objects.filter(
        date=event_date,
        is_visible=True,
        status__in=_ACTIVE,
    ).select_related('circuit')
    if exclude_pk:
        same_day_public = same_day_public.exclude(pk=exclude_pk)

    if not same_day_public.exists():
        return hard_conflicts, soft_warnings

    our_members = set(
        CircuitMembership.objects.filter(circuit=circuit, status='active')
        .values_list('member_id', flat=True)
    )
    if not our_members:
        return hard_conflicts, soft_warnings

    t_new = datetime.combine(event_date, start_time)

    for ev in same_day_public:
        if not ev.circuit:
            continue
        t_existing = datetime.combine(ev.date, ev.start_time)
        if abs((t_new - t_existing).total_seconds()) / 3600 >= 2:
            continue
        their_members = set(
            CircuitMembership.objects.filter(circuit=ev.circuit, status='active')
            .values_list('member_id', flat=True)
        )
        overlap = our_members & their_members
        if overlap:
            soft_warnings.append(
                f"{len(overlap)} shared member(s) with "
                f"{ev.circuit_display}'s raid at {ev.start_time.strftime('%-I:%M %p')}."
            )

    return hard_conflicts, soft_warnings
