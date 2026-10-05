"""Persist valid scans and queue one fault/recovery pair per sensor outage."""
import math
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from . import models as m
from .control import ALASKA, seasonal_heat

SENSORS = {
    'greenhouse': (m.OutsideAirTemp, 'outside_air_temp', 'Greenhouse temperature'),
    'water': (m.WaterTemp, 'water_temp', 'Water temperature'),
    'nursery': (m.NurseryAirTemp, 'nursery_air_temp', 'Nursery temperature'),
    'humidity': (m.Humidity, 'humidity', 'Nursery humidity'),
}


def initialize_health(now=None):
    now = now or timezone.now()
    for name, (model, field, _) in SENSORS.items():
        last = model.objects.last()
        defaults = {'monitoring_since': now}
        if last:
            defaults.update(last_valid=last.created_at, last_value=getattr(last, field))
        m.SensorHealth.objects.get_or_create(name=name, defaults=defaults)


def valid_value(name, value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Non-finite sensor reading')
    low, high = (0, 100) if name == 'humidity' else (-67, 257)
    if not low <= value <= high:
        raise ValueError('Sensor reading outside physical range')
    return value


def fallback_description(name, now):
    output = {'nursery': 'nursery_heater', 'water': 'water_heater'}.get(name)
    if output:
        mode = m.OutputControl.objects.get(name=output)
        if not mode.automatic:
            return 'Heater is in MANUAL: the manual command remains in effect.'
        action = 'ON' if seasonal_heat(now) else 'OFF'
        return 'Heater AUTO stale-sensor fallback: {} (Anchorage May 15 cutoff).'.format(action)
    if name == 'humidity':
        return 'Vent retains its state unless valid nursery temperature requests opening.'
    return 'Greenhouse temperature and last-frost detection are unavailable.'


def queue_fault(health, now):
    since = health.last_valid or health.monitoring_since
    if not health.fault_queued and now - since >= timedelta(minutes=10):
        label = SENSORS[health.name][2]
        last = health.last_valid.astimezone(ALASKA).isoformat() if health.last_valid else 'No valid scan since monitoring began'
        body = ('{} has had no valid scan for at least 10 minutes.\n'
                'Last valid scan: {}\nLast value: {}\n{}\n'
                'Detected: {}\n').format(label, last, health.last_value,
                                         fallback_description(health.name, now), now.astimezone(ALASKA).isoformat())
        if health.name == 'water':
            body += 'An AUTO pump is inhibited while its water sensor is stale.\n'
        m.AlertNotification.objects.create(subject='Greenhouse sensor fault: ' + label, body=body)
        health.fault_queued = True
        health.save(update_fields=['fault_queued'])


@transaction.atomic
def record_scan(name, value, now=None):
    now = now or timezone.now()
    value = valid_value(name, value)
    model, field, label = SENSORS[name]
    health = m.SensorHealth.objects.get(name=name)
    # Also catch an outage that ends on the first scan after the ten-minute mark.
    queue_fault(health, now)
    model.objects.create(**{field: value})
    if health.fault_queued:
        m.AlertNotification.objects.create(
            subject='Greenhouse sensor recovered: ' + label,
            body='{} recovered at {}. Reading: {}. Normal AUTO logic resumes; MANUAL commands remain in effect.'.format(
                label, now.astimezone(ALASKA).isoformat(), value))
    health.last_valid, health.last_value, health.fault_queued = now, value, False
    health.save(update_fields=['last_valid', 'last_value', 'fault_queued'])
    if name == 'greenhouse' and value <= 32:
        frost, _ = m.LastFrostGreenhouse.objects.get_or_create(id=0)
        frost.save()


@transaction.atomic
def check_faults(now=None):
    now = now or timezone.now()
    for health in m.SensorHealth.objects.all():
        queue_fault(health, now)
