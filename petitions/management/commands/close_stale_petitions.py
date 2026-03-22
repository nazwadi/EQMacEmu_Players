from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from petitions.models import Petition, PetitionReply
from petitions.utils import notify_petitioner


class Command(BaseCommand):
    help = 'Auto-close petitions that have been Pending Player for too long without a response.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=7,
            help='Number of days of inactivity before closing (default: 7)',
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff = timezone.now() - timedelta(days=days)

        system_user = User.objects.filter(is_superuser=True).order_by('pk').first()
        if not system_user:
            self.stderr.write(self.style.ERROR('No superuser found — cannot create audit entries.'))
            return

        stale = Petition.objects.filter(
            status=Petition.STATUS_PENDING_PLAYER,
            updated_at__lte=cutoff,
        )

        count = stale.count()
        for petition in stale:
            petition.status = Petition.STATUS_CLOSED
            petition.save()

            PetitionReply.objects.create(
                petition=petition,
                user=system_user,
                body=f"Petition automatically closed after {days} days without a player response.",
                is_staff=True,
                is_system=True,
            )

            notify_petitioner(
                petition,
                f"Your petition #{petition.pk} was automatically closed due to inactivity. "
                f"You may reopen it at any time by replying.",
            )

        self.stdout.write(self.style.SUCCESS(f'Closed {count} stale petition(s).'))
