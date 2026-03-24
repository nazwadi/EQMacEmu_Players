import calendar
import json
from datetime import date, datetime, time, timedelta
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

from django.core.paginator import Paginator

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from dkp.models import CircuitMembership, RaidCircuit

from .conflicts import check_conflicts
from .forms import RaidEventForm
from .models import GMOverrideLog, RaidEvent, RaidSignup, RaidTarget
from .utils import notify_raid_scheduled, notify_raid_updated

_CIRCUIT_COLORS = [
    '#8aa3ff', '#4dbb5f', '#ff8c69', '#c97bff',
    '#ff6b9d', '#ffc466', '#5ec4f7', '#66d9cc',
]


# ── helpers ──────────────────────────────────────────────────────────────────

def _expire_stale(qs):
    """Expire any events whose 2-h window has passed, return cleaned queryset."""
    now = timezone.now()
    stale_pks = []
    for ev in qs:
        tz_name = ev.timezone or 'America/New_York'
        naive = datetime.combine(ev.date, ev.start_time)
        aware = naive.replace(tzinfo=ZoneInfo(tz_name))
        if now >= aware + timedelta(hours=2):
            stale_pks.append(ev.pk)
    if stale_pks:
        RaidEvent.objects.filter(pk__in=stale_pks).update(status=RaidEvent.STATUS_EXPIRED)
        qs = qs.exclude(pk__in=stale_pks)
    return qs


def _visible_events(user):
    """Return queryset of currently live events visible to user."""
    qs = RaidEvent.objects.select_related('circuit').prefetch_related('targets').filter(
        status__in=(RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE),
    )
    if user is None or not user.is_authenticated:
        return _expire_stale(qs.filter(is_public=True))
    if user.is_superuser:
        return _expire_stale(qs)

    # Authenticated non-superuser: public + private events they belong to
    member_circuit_ids = CircuitMembership.objects.filter(
        member=user, status='active',
    ).values_list('circuit_id', flat=True)

    signup_event_ids = RaidEvent.objects.filter(
        signups__member__member=user,
    ).values_list('pk', flat=True)

    qs = qs.filter(
        Q(is_public=True)
        | Q(circuit_id__in=member_circuit_ids)
        | Q(pk__in=signup_event_ids)
    ).distinct()
    return _expire_stale(qs)


def _calendar_visible_events(user):
    """All events (including past) visible to user — for the calendar grid."""
    qs = RaidEvent.objects.select_related('circuit').prefetch_related('targets').filter(
        status__in=(
            RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE,
            RaidEvent.STATUS_EXPIRED, RaidEvent.STATUS_CLOSED,
        ),
    )
    if user is None or not user.is_authenticated:
        return qs.filter(is_public=True)
    if user.is_superuser:
        return qs

    member_circuit_ids = CircuitMembership.objects.filter(
        member=user, status='active',
    ).values_list('circuit_id', flat=True)
    signup_event_ids = RaidEvent.objects.filter(
        signups__member__member=user,
    ).values_list('pk', flat=True)
    return qs.filter(
        Q(is_public=True)
        | Q(circuit_id__in=member_circuit_ids)
        | Q(pk__in=signup_event_ids)
    ).distinct()


def _closeable_pks(user, events_qs):
    """Return set of event PKs that this user may close."""
    if not user.is_authenticated:
        return set()
    if user.is_superuser:
        return set(events_qs.values_list('pk', flat=True))

    owned = set(events_qs.filter(created_by=user).values_list('pk', flat=True))
    officer_circuit_ids = CircuitMembership.objects.filter(
        member=user, role='officer', status='active',
    ).values_list('circuit_id', flat=True)
    officer_events = set(
        events_qs.filter(circuit_id__in=officer_circuit_ids).values_list('pk', flat=True)
    )
    return owned | officer_events


# ── public board ─────────────────────────────────────────────────────────────

def board(request):
    today = date.today()

    view_mode = request.GET.get('view', '')
    if view_mode not in ('day', 'week', 'month'):
        view_mode = request.COOKIES.get('rs_view', 'week')
        if view_mode not in ('day', 'week', 'month'):
            view_mode = 'week'

    date_str = request.GET.get('date', '')
    try:
        anchor = date.fromisoformat(date_str) if date_str else today
    except ValueError:
        anchor = today

    all_events = _visible_events(request.user)   # live only — RSVP/close logic
    grid_events = _calendar_visible_events(request.user)  # incl. past — calendar grid
    closeable = _closeable_pks(request.user, all_events)

    user_rsvp_map_json = '{}'
    if request.user.is_authenticated:
        rsvp_pairs = RaidSignup.objects.filter(
            event__in=all_events,
            member__member=request.user,
        ).values_list('event_id', 'status')
        user_rsvp_map_json = json.dumps({str(eid): st for eid, st in rsvp_pairs})

    # Build sidebar circuit filter list from all approved (active) DKP circuits
    # so a newly approved circuit appears here even before any events exist for it.
    circuit_map = {
        c.pk: {
            'id': str(c.pk),
            'name': c.name,
            'color': _CIRCUIT_COLORS[c.pk % len(_CIRCUIT_COLORS)],
        }
        for c in RaidCircuit.objects.filter(is_active=True).order_by('name')
    }
    filter_circuits = list(circuit_map.values())
    filter_has_writein = all_events.filter(circuit__isnull=True).exists()
    circuit_color_map_json = json.dumps({str(cid): d['color'] for cid, d in circuit_map.items()})

    ctx = {
        'today': today,
        'anchor': anchor,
        'view_mode': view_mode,
        'can_schedule': request.user.is_authenticated,
        'closeable_pks': closeable,
        'filter_circuits': filter_circuits,
        'filter_has_writein': filter_has_writein,
        'circuit_color_map_json': circuit_color_map_json,
        'user_rsvp_map_json': user_rsvp_map_json,
    }

    if view_mode == 'month':
        first_of_month = anchor.replace(day=1)
        # grid starts on the Sunday of the week containing the 1st
        grid_start = first_of_month - timedelta(days=first_of_month.isoweekday() % 7)
        cal = calendar.Calendar(firstweekday=6)
        weeks_count = len(cal.monthdayscalendar(anchor.year, anchor.month))
        grid_end = grid_start + timedelta(weeks=weeks_count)

        range_events = grid_events.filter(date__gte=grid_start, date__lt=grid_end)
        events_by_date = {}
        for ev in range_events:
            events_by_date.setdefault(ev.date, []).append(ev)

        weeks = []
        d = grid_start
        for _ in range(weeks_count):
            row = []
            for __ in range(7):
                row.append({
                    'date': d,
                    'events': events_by_date.get(d, []),
                    'in_month': d.month == anchor.month,
                    'is_today': d == today,
                })
                d += timedelta(days=1)
            weeks.append(row)

        prev_anchor = (first_of_month - timedelta(days=1)).replace(day=1)
        next_anchor = (first_of_month + timedelta(days=32)).replace(day=1)
        ctx.update({
            'weeks': weeks,
            'prev_anchor': prev_anchor,
            'next_anchor': next_anchor,
            'period_label': anchor.strftime('%B %Y'),
        })

    elif view_mode == 'day':
        day_events = list(grid_events.filter(date=anchor).order_by('start_time'))
        prev_anchor = anchor - timedelta(days=1)
        next_anchor = anchor + timedelta(days=1)
        ctx.update({
            'day_events': day_events,
            'prev_anchor': prev_anchor,
            'next_anchor': next_anchor,
            'period_label': anchor.strftime('%A, %B %-d, %Y'),
        })

    else:  # week — Sun→Sat
        week_start = anchor - timedelta(days=anchor.isoweekday() % 7)
        week_end = week_start + timedelta(days=6)
        days = [week_start + timedelta(days=i) for i in range(7)]

        week_events = grid_events.filter(date__gte=week_start, date__lte=week_end)
        events_by_day = {d: [] for d in days}
        for ev in week_events:
            if ev.date in events_by_day:
                events_by_day[ev.date].append(ev)

        days_with_events = [(d, events_by_day[d]) for d in days]

        prev_anchor = week_start - timedelta(weeks=1)
        next_anchor = week_start + timedelta(weeks=1)
        if week_start.month == week_end.month:
            period_label = week_start.strftime('%B %-d') + '–' + week_end.strftime('%-d, %Y')
        else:
            period_label = week_start.strftime('%b %-d') + ' – ' + week_end.strftime('%b %-d, %Y')

        ctx.update({
            'days_with_events': days_with_events,
            'week_start': week_start,
            'prev_anchor': prev_anchor,
            'next_anchor': next_anchor,
            'period_label': period_label,
        })

    return render(request, 'raid_scheduler/board.html', ctx)


# ── scheduling form ───────────────────────────────────────────────────────────

@login_required
def schedule(request):
    hard_conflicts = []
    soft_warnings = []
    preselected_target_ids = []

    if request.method == 'POST':
        form = RaidEventForm(request.POST)
        preselected_target_ids = request.POST.getlist('targets')

        if form.is_valid():
            event_date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            is_public = form.cleaned_data['is_public']
            circuit = form.cleaned_data.get('circuit')
            ack = form.cleaned_data.get('warnings_acknowledged', False)

            # Validate targets manually (not a ModelForm field)
            target_ids = request.POST.getlist('targets')
            selected_targets = list(RaidTarget.objects.filter(pk__in=target_ids)) if target_ids else []

            if not selected_targets:
                form.add_error(None, 'Please add at least one raid target.')
            else:
                hard_conflicts, soft_warnings = check_conflicts(
                    selected_targets, event_date, start_time, is_public, circuit,
                )

                if hard_conflicts:
                    messages.error(request, 'This raid cannot be scheduled due to a conflict.')
                elif soft_warnings and not ack:
                    pass  # re-render with warnings + acknowledge checkbox
                else:
                    event = form.save(commit=False)
                    event.created_by = request.user
                    event.circuit_name = form.cleaned_data.get('circuit_name', '')
                    event.save()
                    event.targets.set(selected_targets)
                    notify_raid_scheduled(event)
                    messages.success(
                        request,
                        f"Raid scheduled: {form.cleaned_data['title']} on {event_date.strftime('%A, %b %-d')}.",
                    )
                    return redirect('raid_scheduler:board')
    else:
        form = RaidEventForm()

    return render(request, 'raid_scheduler/schedule.html', {
        'form': form,
        'hard_conflicts': hard_conflicts,
        'soft_warnings': soft_warnings,
        'preselected_target_ids': preselected_target_ids,
        'targets_json': RaidEventForm.targets_json(),
    })


# ── close event ───────────────────────────────────────────────────────────────

@login_required
@require_POST
def close_event(request, pk):
    event = get_object_or_404(RaidEvent, pk=pk)

    # Permission: creator, circuit officer, or superuser
    is_officer = False
    if event.circuit:
        is_officer = CircuitMembership.objects.filter(
            circuit=event.circuit,
            member=request.user,
            role='officer',
            status='active',
        ).exists()

    if not (request.user.is_superuser or request.user == event.created_by or is_officer):
        messages.error(request, 'You do not have permission to close this event.')
        return redirect('raid_scheduler:board')

    if event.status in (RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE):
        event.status = RaidEvent.STATUS_CLOSED
        event.save(update_fields=['status'])
        messages.success(request, f"Raid closed: {event.title} on {event.date}.")
    else:
        messages.warning(request, 'That event is already closed or expired.')

    return redirect('raid_scheduler:board')


# ── edit event ────────────────────────────────────────────────────────────────

@login_required
def edit_event(request, pk):
    event = get_object_or_404(
        RaidEvent.objects.prefetch_related('targets'),
        pk=pk,
    )

    # Same permission model as close_event
    is_officer = False
    if event.circuit:
        is_officer = CircuitMembership.objects.filter(
            circuit=event.circuit,
            member=request.user,
            role='officer',
            status='active',
        ).exists()

    if not (request.user.is_superuser or request.user == event.created_by or is_officer):
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('raid_scheduler:event_detail', pk=pk)

    if event.status not in (RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE):
        messages.error(request, 'Only scheduled or active events can be edited.')
        return redirect('raid_scheduler:event_detail', pk=pk)

    hard_conflicts = []
    soft_warnings = []
    preselected_target_ids = list(event.targets.values_list('pk', flat=True))

    if request.method == 'POST':
        form = RaidEventForm(request.POST, instance=event)
        preselected_target_ids = request.POST.getlist('targets')

        if form.is_valid():
            event_date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            is_public = form.cleaned_data['is_public']
            circuit = form.cleaned_data.get('circuit')
            ack = form.cleaned_data.get('warnings_acknowledged', False)

            target_ids = request.POST.getlist('targets')
            selected_targets = list(RaidTarget.objects.filter(pk__in=target_ids)) if target_ids else []

            if not selected_targets:
                form.add_error(None, 'Please add at least one raid target.')
            else:
                hard_conflicts, soft_warnings = check_conflicts(
                    selected_targets, event_date, start_time, is_public, circuit,
                    exclude_pk=pk,
                )

                if hard_conflicts:
                    messages.error(request, 'This raid cannot be rescheduled due to a conflict.')
                elif soft_warnings and not ack:
                    pass  # re-render with warnings + acknowledge checkbox
                else:
                    # Capture what changed for Discord notification
                    changes = []
                    old_date = event.date
                    old_time = event.start_time
                    old_target_ids = set(event.targets.values_list('pk', flat=True))
                    old_title = event.title
                    old_public = event.is_public

                    updated = form.save(commit=False)
                    updated.circuit_name = form.cleaned_data.get('circuit_name', '')
                    updated.save()
                    updated.targets.set(selected_targets)

                    if old_title != updated.title:
                        changes.append(f'title: "{old_title}" → "{updated.title}"')
                    if old_date != updated.date:
                        changes.append(
                            f'date: {old_date.strftime("%b %-d")} → {updated.date.strftime("%b %-d")}'
                        )
                    if old_time != updated.start_time:
                        changes.append(
                            f'time: {old_time.strftime("%-I:%M %p")} → {updated.start_time.strftime("%-I:%M %p")}'
                        )
                    new_target_ids = set(updated.targets.values_list('pk', flat=True))
                    if old_target_ids != new_target_ids:
                        changes.append('raid targets updated')
                    if old_public != updated.is_public:
                        changes.append(
                            f'visibility: {"public" if old_public else "private"} → {"public" if updated.is_public else "private"}'
                        )

                    notify_raid_updated(updated, changes)

                    messages.success(
                        request,
                        f"Raid updated: {updated.title} on {updated.date.strftime('%A, %b %-d')}.",
                    )
                    return redirect('raid_scheduler:event_detail', pk=pk)
    else:
        form = RaidEventForm(instance=event)

    rsvp_count = event.signups.count()

    return render(request, 'raid_scheduler/schedule.html', {
        'form': form,
        'hard_conflicts': hard_conflicts,
        'soft_warnings': soft_warnings,
        'preselected_target_ids': preselected_target_ids,
        'targets_json': RaidEventForm.targets_json(),
        'editing_event': event,
        'rsvp_count': rsvp_count,
    })


# ── AJAX conflict check ───────────────────────────────────────────────────────

def conflict_check(request):
    """AJAX GET → JSON {hard: [...], soft: [...]}."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET only'}, status=405)

    target_ids = request.GET.getlist('targets')
    date_str = request.GET.get('date')
    time_str = request.GET.get('start_time')
    is_public = request.GET.get('is_public', 'true').lower() in ('true', '1', 'on')
    circuit_id = request.GET.get('circuit')

    try:
        targets = list(RaidTarget.objects.filter(pk__in=target_ids)) if target_ids else []
        event_date = date.fromisoformat(date_str)
        h, m = time_str.split(':')[:2]
        start_time = time(int(h), int(m))
    except Exception:
        return JsonResponse({'hard': [], 'soft': []})

    circuit = None
    if circuit_id:
        try:
            circuit = RaidCircuit.objects.get(pk=circuit_id)
        except RaidCircuit.DoesNotExist:
            pass

    exclude_pk = request.GET.get('exclude_pk')
    try:
        exclude_pk = int(exclude_pk) if exclude_pk else None
    except (ValueError, TypeError):
        exclude_pk = None

    hard, soft = check_conflicts(targets, event_date, start_time, is_public, circuit, exclude_pk=exclude_pk)
    return JsonResponse({'hard': hard, 'soft': soft})


# ── RSVP ──────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def rsvp_event(request, pk):
    event = get_object_or_404(RaidEvent, pk=pk)

    if event.status not in (RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE):
        messages.error(request, 'This event is no longer accepting RSVPs.')
        return redirect('raid_scheduler:event_detail', pk=pk)

    if not event.circuit:
        messages.error(request, 'RSVPs are only available for circuit-linked events.')
        return redirect('raid_scheduler:event_detail', pk=pk)

    membership = CircuitMembership.objects.filter(
        circuit=event.circuit,
        member=request.user,
        status='active',
    ).first()
    if not membership:
        messages.error(request, 'You must be an active member of this circuit to RSVP.')
        return redirect('raid_scheduler:event_detail', pk=pk)

    status = request.POST.get('status', '')
    note = request.POST.get('note', '').strip()[:255]
    display_name = request.POST.get('display_name', '').strip()[:100]

    if status == 'remove':
        RaidSignup.objects.filter(event=event, member=membership).delete()
        messages.success(request, 'Your RSVP has been removed.')
    elif status in (RaidSignup.STATUS_CONFIRMED, RaidSignup.STATUS_TENTATIVE, RaidSignup.STATUS_DECLINED):
        # Persist display name to membership so it pre-fills on future RSVPs
        if display_name and display_name != membership.display_name:
            membership.display_name = display_name
            membership.save(update_fields=['display_name'])
        signup, created = RaidSignup.objects.get_or_create(
            event=event,
            member=membership,
            defaults={'status': status, 'note': note},
        )
        if not created:
            signup.status = status
            signup.note = note
            signup.save(update_fields=['status', 'note'])
        messages.success(request, 'Your RSVP has been saved.')
    else:
        messages.error(request, 'Invalid RSVP status.')

    url = reverse('raid_scheduler:event_detail', kwargs={'pk': pk})
    anchor = '#rsvp' if status in (RaidSignup.STATUS_CONFIRMED, RaidSignup.STATUS_TENTATIVE, RaidSignup.STATUS_DECLINED, 'remove') else ''
    return redirect(url + anchor)


# ── event detail ──────────────────────────────────────────────────────────────

def event_detail(request, pk):
    event = get_object_or_404(
        RaidEvent.objects.select_related('circuit', 'created_by')
                         .prefetch_related('targets', 'signups__member__member'),
        pk=pk,
    )

    # Visibility: private events require authenticated user with access
    if not event.is_public:
        if not request.user.is_authenticated:
            return redirect(f'{request.build_absolute_uri("/accounts/login/")}?next={request.path}')
        if not request.user.is_superuser:
            has_access = False
            if event.circuit:
                has_access = CircuitMembership.objects.filter(
                    circuit=event.circuit,
                    member=request.user,
                    status='active',
                ).exists()
            if not has_access:
                has_access = event.signups.filter(member__member=request.user).exists()
            if not has_access:
                from django.http import Http404
                raise Http404

    editable_pks = _closeable_pks(request.user, RaidEvent.objects.filter(pk=pk))
    is_closeable = event.pk in editable_pks
    is_editable = is_closeable and event.status in (RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE)

    can_rsvp = False
    user_signup = None
    rsvp_membership = None
    if request.user.is_authenticated and event.circuit and event.status in (RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE):
        rsvp_membership = CircuitMembership.objects.filter(
            circuit=event.circuit,
            member=request.user,
            status='active',
        ).first()
        if rsvp_membership:
            can_rsvp = True
            user_signup = event.signups.filter(member=rsvp_membership).first()

    return render(request, 'raid_scheduler/event_detail.html', {
        'event': event,
        'is_closeable': is_closeable,
        'is_editable': is_editable,
        'can_rsvp': can_rsvp,
        'user_signup': user_signup,
        'membership': rsvp_membership,
    })


# ── raid history ──────────────────────────────────────────────────────────────

# ── iCalendar (.ics) export ────────────────────────────────────────────────────

def _ics_escape(text):
    text = str(text).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')
    text = text.replace('\r\n', '\\n').replace('\n', '\\n').replace('\r', '\\n')
    return text


def _build_ics(events, request, cal_name='EQ Archives Raid Schedule'):
    now_utc = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//EQ Archives//Raid Scheduler//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        f'X-WR-CALNAME:{_ics_escape(cal_name)}',
        'X-WR-CALDESC:EverQuest Mac raid schedule',
    ]

    for event in events:
        start_naive = datetime.combine(event.date, event.start_time)
        end_naive = start_naive + timedelta(hours=2)
        aware_start = timezone.make_aware(start_naive)
        aware_end = timezone.make_aware(end_naive)
        dtstart = aware_start.astimezone(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        dtend = aware_end.astimezone(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')

        uid = f'raidevent-{event.pk}@eqarchives'
        summary = _ics_escape(event.title)

        desc_parts = []
        circuit_name = event.circuit_display
        if circuit_name != '—':
            desc_parts.append(f'Circuit: {circuit_name}')
        targets = [t.name for t in event.targets.all()]
        if targets:
            desc_parts.append(f'Targets: {", ".join(targets)}')
        if event.notes:
            desc_parts.append(event.notes)
        description = _ics_escape('\n'.join(desc_parts))

        url = request.build_absolute_uri(
            reverse('raid_scheduler:event_detail', kwargs={'pk': event.pk})
        )

        vevent_status = 'CANCELLED' if event.status == RaidEvent.STATUS_CANCELLED else 'CONFIRMED'

        lines += [
            'BEGIN:VEVENT',
            f'UID:{uid}',
            f'DTSTAMP:{now_utc}',
            f'DTSTART:{dtstart}',
            f'DTEND:{dtend}',
            f'SUMMARY:{summary}',
        ]
        if description:
            lines.append(f'DESCRIPTION:{description}')
        lines += [
            f'URL:{url}',
            f'STATUS:{vevent_status}',
            'END:VEVENT',
        ]

    lines.append('END:VCALENDAR')
    return '\r\n'.join(lines)


def event_ics(request, pk):
    """Download a single raid event as an .ics file."""
    event = get_object_or_404(
        RaidEvent.objects.select_related('circuit').prefetch_related('targets'),
        pk=pk,
    )
    if not event.is_public:
        if not request.user.is_authenticated:
            from django.http import Http404
            raise Http404
        if not request.user.is_superuser:
            has_access = False
            if event.circuit:
                has_access = CircuitMembership.objects.filter(
                    circuit=event.circuit, member=request.user, status='active',
                ).exists()
            if not has_access:
                has_access = event.signups.filter(member__member=request.user).exists()
            if not has_access:
                from django.http import Http404
                raise Http404

    content = _build_ics([event], request, cal_name=event.title)
    response = HttpResponse(content, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="raid-{event.pk}.ics"'
    return response


def calendar_feed(request):
    """Subscribable .ics feed of all upcoming public events."""
    events = (
        RaidEvent.objects.select_related('circuit').prefetch_related('targets')
        .filter(is_public=True, status__in=(RaidEvent.STATUS_SCHEDULED, RaidEvent.STATUS_ACTIVE))
        .order_by('date', 'start_time')
    )
    content = _build_ics(events, request, cal_name='EQ Archives — Raid Schedule')
    response = HttpResponse(content, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = 'inline; filename="eq-raids.ics"'
    return response


_HISTORY_STATUSES = (RaidEvent.STATUS_CLOSED, RaidEvent.STATUS_EXPIRED, RaidEvent.STATUS_CANCELLED)


def history(request):
    qs = RaidEvent.objects.select_related('circuit').prefetch_related(
        'targets', 'signups',
    ).filter(status__in=_HISTORY_STATUSES)

    # Apply same visibility rules as the live board
    if not request.user.is_authenticated:
        qs = qs.filter(is_public=True)
    elif not request.user.is_superuser:
        member_circuit_ids = CircuitMembership.objects.filter(
            member=request.user, status='active',
        ).values_list('circuit_id', flat=True)
        signup_event_ids = RaidEvent.objects.filter(
            signups__member__member=request.user,
        ).values_list('pk', flat=True)
        qs = qs.filter(
            Q(is_public=True)
            | Q(circuit_id__in=member_circuit_ids)
            | Q(pk__in=signup_event_ids)
        ).distinct()

    # Search: title or target name
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(targets__name__icontains=q)
        ).distinct()

    # Circuit filter
    circuit_id = request.GET.get('circuit', '').strip()
    if circuit_id == 'other':
        qs = qs.filter(circuit__isnull=True)
    elif circuit_id:
        try:
            qs = qs.filter(circuit_id=int(circuit_id))
        except ValueError:
            circuit_id = ''

    # Date range
    date_from = request.GET.get('from', '').strip()
    date_to = request.GET.get('to', '').strip()
    try:
        qs = qs.filter(date__gte=date.fromisoformat(date_from)) if date_from else qs
    except ValueError:
        date_from = ''
    try:
        qs = qs.filter(date__lte=date.fromisoformat(date_to)) if date_to else qs
    except ValueError:
        date_to = ''

    qs = qs.order_by('-date', '-start_time')

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    # Circuit choices for the filter dropdown (from all visible history)
    circuit_choices = list(
        RaidEvent.objects.filter(status__in=_HISTORY_STATUSES, circuit__isnull=False)
        .values('circuit_id', 'circuit__name')
        .distinct()
        .order_by('circuit__name')
    )

    return render(request, 'raid_scheduler/history.html', {
        'page_obj': page_obj,
        'q': q,
        'circuit_id': circuit_id,
        'date_from': date_from,
        'date_to': date_to,
        'circuit_choices': circuit_choices,
    })
