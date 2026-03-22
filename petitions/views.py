import logging

import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import staff_required
from .models import (
    CannedResponse, Notification, Petition, PetitionCategory,
    PetitionReply, PlayerEmailPreference, StaffEmailPreference, StaffTag,
)
from .utils import get_user_characters, is_staff_member, notify_petitioner, notify_staff

logger = logging.getLogger('eqmacemu.security')

PETITION_LIMIT = 5


# ---------------------------------------------------------------------------
# Player views
# ---------------------------------------------------------------------------

@login_required
def petition_list(request):
    from django.db.models import Count
    petitions = (
        Petition.objects
        .filter(user=request.user)
        .annotate(
            unread_count=Count(
                'notification',
                filter=Q(notification__user=request.user, notification__read=False),
            )
        )
        .order_by('-updated_at')
    )
    active = [p for p in petitions if p.status in Petition.ACTIVE_STATUSES]
    closed = [p for p in petitions if p.status not in Petition.ACTIVE_STATUSES]
    pref, _ = PlayerEmailPreference.objects.get_or_create(user=request.user)
    return render(request, 'petitions/petition_list.html', {
        'active_petitions': active,
        'closed_petitions': closed,
        'email_pref': pref,
    })


PETITION_ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'zip', 'log'}
PETITION_MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024  # 10 MB


@login_required
def petition_create(request):
    # Check limit before showing the form
    active_count = Petition.objects.filter(
        user=request.user,
        status__in=Petition.ACTIVE_STATUSES
    ).count()

    if active_count >= PETITION_LIMIT:
        messages.error(
            request,
            f"You already have {active_count} open petitions. "
            f"Please wait for them to be resolved before filing more."
        )
        return redirect('petitions:list')

    categories = PetitionCategory.objects.filter(active=True)
    characters = list(get_user_characters(request.user))

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        category_id = request.POST.get('category')
        character_name = request.POST.get('character_name', '').strip()
        body = request.POST.get('body', '').strip()

        errors = []
        if not subject:
            errors.append("Subject is required.")
        if not category_id:
            errors.append("Category is required.")
        if not body:
            errors.append("Message is required.")
        if character_name and character_name not in characters:
            errors.append("Invalid character selected.")

        if not errors:
            try:
                category = PetitionCategory.objects.get(pk=category_id, active=True)
            except PetitionCategory.DoesNotExist:
                errors.append("Invalid category selected.")

        if not errors:
            with transaction.atomic():
                # Lock the user row to serialize concurrent petition creation
                User.objects.select_for_update().get(pk=request.user.pk)
                if Petition.objects.filter(
                    user=request.user,
                    status__in=Petition.ACTIVE_STATUSES
                ).count() >= PETITION_LIMIT:
                    messages.error(
                        request,
                        "You already have too many open petitions. "
                        "Please wait for them to be resolved before filing more."
                    )
                    return redirect('petitions:list')

                petition = Petition.objects.create(
                    user=request.user,
                    category=category,
                    subject=subject,
                    character_name=character_name,
                    status=Petition.STATUS_OPEN,
                )
                PetitionReply.objects.create(
                    petition=petition,
                    user=request.user,
                    body=body,
                    is_staff=False,
                )

            notify_staff(
                petition,
                f"New petition from {request.user.username}: {subject}",
                exclude_user=request.user,
            )
            logger.info('PETITION_CREATE user=%s petition=%s', request.user.username, petition.pk)
            messages.success(request, "Your petition has been submitted. Staff will respond as soon as possible.")
            return redirect('petitions:detail', pk=petition.pk)

        for error in errors:
            messages.error(request, error)

    return render(request, 'petitions/petition_create.html', {
        'categories': categories,
        'characters': characters,
    })


@login_required
def petition_detail(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    user_is_staff = is_staff_member(request.user)

    # Players can only see their own petitions
    if petition.user != request.user and not user_is_staff:
        messages.error(request, "You don't have permission to view that petition.")
        return redirect('petitions:list')

    # Mark notifications as read
    Notification.objects.filter(user=request.user, petition=petition, read=False).update(read=True)

    if request.method == 'POST':
        action = request.POST.get('action', 'reply')

        # --- Reassign ---
        if action == 'reassign' and user_is_staff:
            assignee_id = request.POST.get('assignee_id')
            if assignee_id:
                try:
                    assignee = User.objects.get(pk=assignee_id)
                    if not is_staff_member(assignee):
                        messages.error(request, "Can only assign petitions to staff members.")
                        return redirect('petitions:detail', pk=pk)
                    old_claimed = petition.claimed_by
                    petition.claimed_by = assignee
                    petition.status = Petition.STATUS_CLAIMED
                    petition.save()
                    note = (
                        f"Reassigned from {old_claimed.username} to {assignee.username}"
                        if old_claimed else f"Assigned to {assignee.username}"
                    )
                    PetitionReply.objects.create(
                        petition=petition, user=request.user,
                        body=note, is_staff=True, is_system=True,
                    )
                    messages.success(request, f"Petition assigned to {assignee.username}.")
                except User.DoesNotExist:
                    messages.error(request, "Invalid assignee.")
            return redirect('petitions:detail', pk=pk)

        # --- Reply (regular or internal note) ---
        body = request.POST.get('body', '').strip()
        is_internal = request.POST.get('is_internal') == 'on' and user_is_staff

        if not body:
            messages.error(request, "Reply cannot be empty.")
            return redirect('petitions:detail', pk=pk)

        attachment = request.FILES.get('attachment')
        if attachment:
            ext = attachment.name.rsplit('.', 1)[-1].lower() if '.' in attachment.name else ''
            if ext not in PETITION_ALLOWED_EXTENSIONS:
                messages.error(request, f"File type '.{ext}' is not allowed.")
                return redirect('petitions:detail', pk=pk)
            if attachment.size > PETITION_MAX_ATTACHMENT_BYTES:
                messages.error(request, "Attachment must be 10 MB or smaller.")
                return redirect('petitions:detail', pk=pk)

        if petition.is_locked and not user_is_staff:
            messages.error(request, "This petition has been locked and cannot receive further replies.")
            return redirect('petitions:detail', pk=pk)

        # Players replying to closed/resolved petitions reopen them
        if not user_is_staff and petition.status in [Petition.STATUS_CLOSED, Petition.STATUS_RESOLVED]:
            petition.status = Petition.STATUS_OPEN
            petition.save()

        reply_kwargs = dict(
            petition=petition,
            user=request.user,
            body=body,
            is_staff=user_is_staff,
            is_internal=is_internal,
        )
        if attachment:
            reply_kwargs['attachment'] = attachment

        PetitionReply.objects.create(**reply_kwargs)

        if user_is_staff and not is_internal:
            petition.status = Petition.STATUS_PENDING_PLAYER
            petition.save()
            notify_petitioner(petition, f"Staff replied to your petition: {petition.subject}")
        elif not user_is_staff:
            petition.status = Petition.STATUS_OPEN
            petition.save()
            notify_staff(
                petition,
                f"{request.user.username} replied to petition #{petition.pk}: {petition.subject}",
                exclude_user=request.user,
            )

        return redirect('petitions:detail', pk=pk)

    # Filter replies: players never see internal notes
    replies_qs = petition.replies.select_related('user')
    if not user_is_staff:
        replies_qs = replies_qs.filter(is_internal=False)
    replies = replies_qs.all()

    all_tags = StaffTag.objects.all() if user_is_staff else None
    applied_tag_ids = list(petition.staff_tags.values_list('id', flat=True)) if user_is_staff else []

    other_petitions = []
    canned_responses = []
    staff_members = []
    if user_is_staff:
        other_petitions = (
            Petition.objects.filter(user=petition.user)
            .exclude(pk=pk)
            .order_by('-updated_at')[:5]
        )
        canned_responses = CannedResponse.objects.all()
        staff_members = (
            User.objects.filter(Q(is_superuser=True) | Q(claimed_petitions__isnull=False))
            .exclude(pk=petition.user.pk)
            .distinct()
            .order_by('username')
        )

    return render(request, 'petitions/petition_detail.html', {
        'petition': petition,
        'replies': replies,
        'user_is_staff': user_is_staff,
        'all_tags': all_tags,
        'applied_tag_ids': applied_tag_ids,
        'status_choices': Petition.STATUS_CHOICES,
        'priority_choices': Petition.PRIORITY_CHOICES,
        'other_petitions': other_petitions,
        'canned_responses': canned_responses,
        'staff_members': staff_members,
    })


# ---------------------------------------------------------------------------
# Staff views
# ---------------------------------------------------------------------------

@staff_required
def staff_petition_list(request):
    # Bulk actions
    if request.method == 'POST':
        bulk_action = request.POST.get('bulk_action')
        petition_ids = request.POST.getlist('petition_ids')
        if petition_ids and bulk_action:
            qs = Petition.objects.filter(pk__in=petition_ids)
            if bulk_action == 'close':
                qs.update(status=Petition.STATUS_CLOSED)
                messages.success(request, f"Closed {len(petition_ids)} petition(s).")
            elif bulk_action == 'resolve':
                qs.update(status=Petition.STATUS_RESOLVED)
                messages.success(request, f"Resolved {len(petition_ids)} petition(s).")
            elif bulk_action == 'assign_me':
                qs.update(claimed_by=request.user, status=Petition.STATUS_CLAIMED)
                messages.success(request, f"Assigned {len(petition_ids)} petition(s) to you.")
        return redirect('petitions:staff_list')

    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    tag_filter = request.GET.get('tag', '')
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('q', '').strip()

    petitions = (
        Petition.objects
        .select_related('user', 'category', 'claimed_by')
        .prefetch_related('staff_tags')
        .order_by('-updated_at')
    )

    if status_filter:
        petitions = petitions.filter(status=status_filter)
    if category_filter:
        petitions = petitions.filter(category_id=category_filter)
    if tag_filter:
        petitions = petitions.filter(staff_tags__id=tag_filter)
    if priority_filter:
        petitions = petitions.filter(priority=priority_filter)
    if search_query:
        petitions = petitions.filter(
            Q(subject__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(character_name__icontains=search_query) |
            Q(replies__body__icontains=search_query)
        ).distinct()

    paginator = Paginator(petitions, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'petitions/staff_petition_list.html', {
        'page_obj': page_obj,
        'petitions': page_obj,
        'categories': PetitionCategory.objects.filter(active=True),
        'tags': StaffTag.objects.all(),
        'status_filter': status_filter,
        'category_filter': category_filter,
        'tag_filter': tag_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'status_choices': Petition.STATUS_CHOICES,
        'priority_choices': Petition.PRIORITY_CHOICES,
    })


@staff_required
def petition_claim(request, pk):
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        action = request.POST.get('action')

        if action == 'claim':
            petition.claimed_by = request.user
            petition.status = Petition.STATUS_CLAIMED
            petition.save()
            PetitionReply.objects.create(
                petition=petition, user=request.user,
                body=f"Claimed by {request.user.username}",
                is_staff=True, is_system=True,
            )
            messages.success(request, f"You have claimed petition #{pk}.")
        elif action == 'unclaim':
            petition.claimed_by = None
            petition.status = Petition.STATUS_OPEN
            petition.save()
            PetitionReply.objects.create(
                petition=petition, user=request.user,
                body=f"Unclaimed by {request.user.username}",
                is_staff=True, is_system=True,
            )
            messages.success(request, f"Petition #{pk} returned to the queue.")

    return redirect('petitions:detail', pk=pk)


@staff_required
def petition_status_update(request, pk):
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        new_status = request.POST.get('status')
        valid = [s[0] for s in Petition.STATUS_CHOICES]

        if new_status in valid and new_status != petition.status:
            old_display = petition.get_status_display()
            petition.status = new_status
            petition.save()

            PetitionReply.objects.create(
                petition=petition, user=request.user,
                body=f"Status changed from {old_display} to {petition.get_status_display()}",
                is_staff=True, is_system=True,
            )
            logger.info(
                'PETITION_STATUS user=%s petition=%s old=%s new=%s',
                request.user.username, pk, old_display, new_status,
            )
            if new_status in [Petition.STATUS_RESOLVED, Petition.STATUS_CLOSED]:
                notify_petitioner(
                    petition,
                    f"Your petition #{petition.pk} has been marked as {petition.get_status_display()}.",
                )
            messages.success(request, f"Status updated to {petition.get_status_display()}.")

    return redirect('petitions:detail', pk=pk)


@staff_required
def petition_lock_toggle(request, pk):
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        action = request.POST.get('action')

        if action == 'lock' and not petition.is_locked:
            petition.is_locked = True
            petition.save()
            PetitionReply.objects.create(
                petition=petition, user=request.user,
                body=f"Petition locked by {request.user.username} — no further replies permitted.",
                is_staff=True, is_system=True,
            )
            notify_petitioner(
                petition,
                f"Your petition #{petition.pk} has been locked and cannot receive further replies.",
            )
            messages.success(request, "Petition locked.")

        elif action == 'unlock' and petition.is_locked:
            petition.is_locked = False
            petition.save()
            PetitionReply.objects.create(
                petition=petition, user=request.user,
                body=f"Petition unlocked by {request.user.username}.",
                is_staff=True, is_system=True,
            )
            messages.success(request, "Petition unlocked.")

    return redirect('petitions:detail', pk=pk)


@staff_required
def petition_priority_update(request, pk):
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        new_priority = request.POST.get('priority')
        valid = [p[0] for p in Petition.PRIORITY_CHOICES]

        if new_priority in valid and new_priority != petition.priority:
            old_display = petition.get_priority_display()
            petition.priority = new_priority
            petition.save()
            PetitionReply.objects.create(
                petition=petition, user=request.user,
                body=f"Priority changed from {old_display} to {petition.get_priority_display()}",
                is_staff=True, is_system=True,
            )

    return redirect('petitions:detail', pk=pk)


@staff_required
def petition_update_tags(request, pk):
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        tag_ids = request.POST.getlist('tags')
        petition.staff_tags.set(StaffTag.objects.filter(id__in=tag_ids))
        messages.success(request, "Tags updated.")
    return redirect('petitions:detail', pk=pk)


@staff_required
def staff_tag_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            color = request.POST.get('color', 'secondary')
            if name:
                tag, created = StaffTag.objects.get_or_create(
                    name=name,
                    defaults={'color': color, 'created_by': request.user}
                )
                if created:
                    messages.success(request, f"Tag '{name}' created.")
                else:
                    messages.warning(request, f"Tag '{name}' already exists.")

        elif action == 'delete':
            tag_id = request.POST.get('tag_id')
            StaffTag.objects.filter(pk=tag_id).delete()
            messages.success(request, "Tag deleted.")

        return redirect('petitions:staff_tags')

    tags = StaffTag.objects.select_related('created_by').all()
    return render(request, 'petitions/staff_tag_list.html', {
        'tags': tags,
        'color_choices': StaffTag.COLOR_CHOICES,
    })


@staff_required
def staff_canned_responses(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            body = request.POST.get('body', '').strip()
            if name and body:
                _, created = CannedResponse.objects.get_or_create(
                    name=name,
                    defaults={'body': body, 'created_by': request.user}
                )
                if created:
                    messages.success(request, f"Response '{name}' created.")
                else:
                    messages.warning(request, f"A response named '{name}' already exists.")
            else:
                messages.error(request, "Name and body are both required.")

        elif action == 'delete':
            CannedResponse.objects.filter(pk=request.POST.get('response_id')).delete()
            messages.success(request, "Response deleted.")

        return redirect('petitions:staff_canned_responses')

    responses = CannedResponse.objects.select_related('created_by').all()
    return render(request, 'petitions/staff_canned_responses.html', {'responses': responses})


@login_required
def player_email_preference(request):
    if request.method == 'POST':
        enabled = request.POST.get('email_notifications') == 'on'
        PlayerEmailPreference.objects.update_or_create(
            user=request.user,
            defaults={'email_notifications': enabled}
        )
        messages.success(request, "Email preference saved.")
        return redirect('petitions:list')

    pref, _ = PlayerEmailPreference.objects.get_or_create(user=request.user)
    return render(request, 'petitions/player_email_preference.html', {'pref': pref})


@login_required
def petition_attachment(request, reply_pk):
    reply = get_object_or_404(PetitionReply.objects.select_related('petition'), pk=reply_pk)

    if not reply.attachment:
        raise Http404

    user_is_staff = is_staff_member(request.user)

    # Internal notes: staff only
    if reply.is_internal and not user_is_staff:
        raise PermissionDenied

    # Must be petition owner or staff
    if reply.petition.user != request.user and not user_is_staff:
        raise PermissionDenied

    # TODO: when R2/S3 storage is configured, replace this block with:
    #   return redirect(reply.attachment.url)  # presigned URL from django-storages
    filename = os.path.basename(reply.attachment.name)
    return FileResponse(reply.attachment.open('rb'), as_attachment=True, filename=filename)


@staff_required
def staff_email_preference(request):
    if request.method == 'POST':
        enabled = request.POST.get('email_notifications') == 'on'
        StaffEmailPreference.objects.update_or_create(
            user=request.user,
            defaults={'email_notifications': enabled}
        )
        messages.success(request, "Email notification preference saved.")
        return redirect('petitions:staff_list')

    pref, _ = StaffEmailPreference.objects.get_or_create(user=request.user)
    return render(request, 'petitions/staff_email_preference.html', {'pref': pref})
