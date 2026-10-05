"""Control decisions shared by the dashboard and hardware worker (no GPIO imports)."""
from datetime import datetime, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from . import models as m

ALASKA = ZoneInfo('America/Anchorage')
OUTPUTS = {
    'nursery_heater': (m.AirHeaterStatus, 'air_heater_on', 0),
    'water_heater': (m.WaterHeaterStatus, 'water_heater_on', 5),
    'fan': (m.FanStatus, 'fan_on', 13),
    'vent': (m.VentStatus, 'vent_on', 19),
    'pump': (m.PumpStatus, 'pump_on', 6),
    'garden_valve': (m.GardenValveStatus, 'garden_valve_open', 16),
    'greenhouse_planter_valve': (m.GreenhousePlanterValveStatus, 'greenhouse_planter_valve_open', 20),
    'greenhouse_tree_valve': (m.GreenhouseTreeValveStatus, 'greenhouse_tree_valve_open', 21),
}
SCHEDULED = tuple(OUTPUTS)[4:]


def lock_controls():
    # SQLite has no SELECT FOR UPDATE. Take its write lock before reading states.
    # Both dashboard writes and each hardware output decision use this lock.
    m.OutputControl.objects.update(automatic=F('automatic'))


def modes():
    return dict(m.OutputControl.objects.values_list('name', 'automatic'))


def mode_summary(values):
    if all(values.values()):
        return 'Automatic'
    if not any(values.values()):
        return 'Manual'
    return 'Mixed'


@transaction.atomic
def set_mode(name, automatic):
    lock_controls()
    if name == 'all':
        m.OutputControl.objects.update(automatic=automatic)
        m.SystemStatus.objects.create(automatic=automatic)
    else:
        if name not in OUTPUTS:
            raise ValueError('Unknown output')
        m.OutputControl.objects.filter(name=name).update(automatic=automatic)


def record_output(name, desired):
    model, field, _ = OUTPUTS[name]
    old = model.objects.last()
    if old is None:
        return model.objects.create(**{field: desired})
    if getattr(old, field) != desired:
        # Copy schedule fields, but never shift the schedule on an output change.
        old.pk = None
        setattr(old, field, desired)
        old.save()
    return old


@transaction.atomic
def manual_toggle(name):
    lock_controls()
    if m.OutputControl.objects.get(name=name).automatic:
        raise ValueError('Select MANUAL before changing this output')
    model, field, _ = OUTPUTS[name]
    old = model.objects.last()
    record_output(name, not getattr(old, field))


def local_start(day, hour, minute):
    # During the spring gap, 02:xx becomes 03:xx. On the autumn fold choose
    # the first occurrence. Future days always use the configured wall time.
    local = datetime(day.year, day.month, day.day, hour, minute, tzinfo=ALASKA)
    return local.astimezone(dt_timezone.utc)


def schedule_active(row, now):
    """Skip expired windows in O(1), preserving the local calendar-day anchor."""
    if row.frequency <= 0 or row.duration <= 0 or row.duration > row.frequency * 1440:
        return False  # Legacy zero/invalid schedules are disabled.
    start = row.next_start_time
    duration = timedelta(minutes=row.duration)
    if now >= start + duration:
        anchor = start.astimezone(ALASKA).date()
        elapsed_days = (now.astimezone(ALASKA).date() - anchor).days
        jumps = max(0, elapsed_days // row.frequency)
        day = anchor + timedelta(days=jumps * row.frequency)
        start = local_start(day, row.start_hour, row.start_minute)
        # Before today's start, yesterday's overnight window may still be active.
        if start > now and jumps > 0:
            day -= timedelta(days=row.frequency)
            start = local_start(day, row.start_hour, row.start_minute)
        if now >= start + duration:
            start = local_start(day + timedelta(days=row.frequency), row.start_hour, row.start_minute)
        row.next_start_time = start
        # Updating schedule metadata must not fabricate a new output transition.
        type(row).objects.filter(pk=row.pk).update(next_start_time=start)
    return start <= now < start + duration


@transaction.atomic
def set_schedule(name, hour, minute, duration, frequency):
    hour, minute, duration, frequency = map(int, (hour, minute, duration, frequency))
    if not (0 <= hour <= 23 and 0 <= minute <= 59 and 1 <= frequency <= 365
            and 0 <= duration <= min(1440, frequency * 1440)):
        raise ValueError('Use a valid time, 0–1440 minutes, and a frequency of 1–365 days')
    lock_controls()
    model, _, _ = OUTPUTS[name]
    row = model.objects.last()
    now = timezone.now()
    day = now.astimezone(ALASKA).date()
    start = local_start(day, hour, minute)
    if start < now:
        start = local_start(day + timedelta(days=1), hour, minute)
    row.pk = None
    row.start_hour, row.start_minute = hour, minute
    row.duration, row.frequency = duration, frequency
    row.next_start_time = start
    row.save()


def seasonal_heat(now):
    local = now.astimezone(ALASKA)
    return (local.month, local.day) < (5, 15)


def fresh(health, now):
    return health is not None and health.last_valid is not None and (
        0 <= (now - health.last_valid).total_seconds() < 60)


def heater_desired(health, setpoint, current, now):
    if not fresh(health, now):
        return seasonal_heat(now)
    if health.last_value < setpoint:
        return True
    if health.last_value > setpoint + 2:
        return False
    return current


def vent_desired(temperature, humidity, setpoint, air_setpoint, current, now):
    # A failed channel cannot cancel a valid opening request from the other.
    temp_ok, humid_ok = fresh(temperature, now), fresh(humidity, now)
    if (temp_ok and temperature.last_value > 80) or (humid_ok and humidity.last_value > setpoint):
        return True
    if temp_ok and humid_ok and humidity.last_value < setpoint - 5 and (
            temperature.last_value < 77 or temperature.last_value <= air_setpoint):
        return False
    return current


@transaction.atomic
def run_outputs(gpio, now=None):
    now = now or timezone.now()
    lock_controls()
    health = {h.name: h for h in m.SensorHealth.objects.all()}
    current_modes = modes()
    air_setpoint = m.AirTempSetpoint.objects.last().air_temp_setpoint
    water_setpoint = m.WaterTempSetpoint.objects.last().water_temp_setpoint
    humidity_setpoint = m.HumiditySetpoint.objects.last().humidity_setpoint
    for name, (model, field, pin) in OUTPUTS.items():
        row = model.objects.last()
        desired = getattr(row, field)
        active = schedule_active(row, now) if name in SCHEDULED else False
        if current_modes[name]:
            if name == 'nursery_heater':
                desired = heater_desired(health.get('nursery'), air_setpoint, desired, now)
            elif name == 'water_heater':
                desired = heater_desired(health.get('water'), water_setpoint, desired, now)
            elif name == 'fan':
                desired = True
            elif name == 'vent':
                desired = vent_desired(health.get('nursery'), health.get('humidity'),
                                       humidity_setpoint, air_setpoint, desired, now)
            elif name == 'pump':
                water = health.get('water')
                desired = active and fresh(water, now) and water.last_value > 32
            else:
                desired = active
        # Reassert every cycle, including within hysteresis after a restart.
        gpio.output(pin, gpio.HIGH if desired else gpio.LOW)
        record_output(name, desired)
