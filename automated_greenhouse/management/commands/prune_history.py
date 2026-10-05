import calendar

from django.core.management.base import BaseCommand
from django.utils import timezone

from automated_greenhouse import models as m
from automated_greenhouse.control import ALASKA

HISTORY = (
    m.OutsideAirTemp, m.NurseryAirTemp, m.WaterTemp, m.Humidity, m.WaterLevel,
    m.SystemStatus, m.AirTempSetpoint, m.WaterTempSetpoint, m.HumiditySetpoint,
    m.FanStatus, m.VentStatus, m.AirHeaterStatus, m.WaterHeaterStatus, m.PumpStatus,
    m.GardenValveStatus, m.GreenhousePlanterValveStatus, m.GreenhouseTreeValveStatus,
)


def retention_cutoff(now):
    local = now.astimezone(ALASKA)
    month_index = local.year * 12 + local.month - 1 - 3
    year, month = divmod(month_index, 12)
    month += 1
    return local.replace(year=year, month=month,
                         day=min(local.day, calendar.monthrange(year, month)[1]))


class Command(BaseCommand):
    help = 'Preview three-calendar-month history cleanup; --apply deletes in small batches.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')

    def handle(self, *args, **options):
        cutoff = retention_cutoff(timezone.now())
        self.stdout.write('Cutoff: {} ({})'.format(cutoff.isoformat(), 'APPLY' if options['apply'] else 'PREVIEW'))
        for model in HISTORY + (m.SystemError, m.AlertNotification):
            query = model.objects.filter(created_at__lt=cutoff)
            if model in HISTORY:
                latest = model.objects.order_by('-pk').values_list('pk', flat=True).first()
                if latest is not None:
                    query = query.exclude(pk=latest)
            if model is m.AlertNotification:
                query = query.filter(sent_at__isnull=False)  # Never discard queued mail.
            count = query.count()
            self.stdout.write('{}: {}'.format(model.__name__, count))
            if options['apply']:
                while True:
                    ids = list(query.order_by('pk').values_list('pk', flat=True)[:1000])
                    if not ids:
                        break
                    model.objects.filter(pk__in=ids).delete()
        # LastFrostGreenhouse, OutputControl, SensorHealth, and users are deliberately excluded.
