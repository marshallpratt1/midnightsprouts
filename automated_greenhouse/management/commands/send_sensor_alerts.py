"""Run once a minute in a separate process; never from the control loop."""
import fcntl
from contextlib import contextmanager
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from automated_greenhouse.models import AlertNotification


@contextmanager
def worker_lock():
    with open(settings.BASE_DIR / '.sensor-alerts.lock', 'a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


class Command(BaseCommand):
    help = 'Deliver queued sensor fault/recovery emails; retry failures without blocking controls.'

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true', help='Send a setup test email to the configured recipient')

    def handle(self, *args, **options):
        if not settings.EMAIL_HOST or not settings.DEFAULT_FROM_EMAIL or not settings.GREENHOUSE_ALERT_RECIPIENT:
            raise CommandError('Configure EMAIL_HOST, DEFAULT_FROM_EMAIL, and GREENHOUSE_ALERT_RECIPIENT on the Pi first')
        with worker_lock() as acquired:
            if not acquired:
                return
            if options['test']:
                send_mail('Greenhouse alert setup test', 'Greenhouse email delivery is working.',
                          settings.DEFAULT_FROM_EMAIL, [settings.GREENHOUSE_ALERT_RECIPIENT])
                self.stdout.write('Test email sent')
                return
            # Oldest first, so a recovery cannot overtake its fault notification.
            for alert in AlertNotification.objects.filter(sent_at__isnull=True).order_by('id')[:50]:
                now = timezone.now()
                if alert.next_attempt > now:
                    break
                try:
                    count = send_mail(alert.subject, alert.body, settings.DEFAULT_FROM_EMAIL,
                                      [settings.GREENHOUSE_ALERT_RECIPIENT], fail_silently=False)
                    if count != 1:
                        raise RuntimeError('Email backend did not accept the message')
                except Exception:
                    alert.attempts += 1
                    alert.next_attempt = now + timedelta(minutes=min(60, 2 ** min(alert.attempts, 6)))
                    alert.save(update_fields=['attempts', 'next_attempt'])
                    self.stderr.write('Email delivery failed; notification retained for retry. Check SMTP settings/connectivity.')
                    break
                alert.sent_at = timezone.now()
                alert.save(update_fields=['sent_at'])
                self.stdout.write('Sent notification {}'.format(alert.pk))
