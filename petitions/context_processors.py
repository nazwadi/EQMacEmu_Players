from .models import Notification, Petition
from .utils import is_staff_member


def petition_context(request):
    if not request.user.is_authenticated:
        return {}

    unread_count = Notification.objects.filter(
        user=request.user,
        read=False
    ).count()

    staff = is_staff_member(request.user)

    # For staff: count of open petitions that need attention (open or pending player reply)
    open_petition_count = (
        Petition.objects.filter(
            status__in=[Petition.STATUS_OPEN, Petition.STATUS_PENDING_PLAYER]
        ).count()
        if staff else 0
    )

    return {
        'unread_notification_count': unread_count,
        'user_is_staff': staff,
        'open_petition_count': open_petition_count,
    }
