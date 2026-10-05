from datetime import datetime, timedelta, timezone as utc
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings

from . import models as m
from .control import (ALASKA, OUTPUTS, SCHEDULED, heater_desired, local_start,
                      manual_toggle, modes, run_outputs, schedule_active,
                      seasonal_heat, set_mode, set_schedule, vent_desired)
from .sensors import initialize_health, record_scan, check_faults
from .management.commands.prune_history import retention_cutoff
from scripts.hardware import parse_probe, read_sensors


def at(month=4, day=20, hour=8, minute=0):
    return datetime(2026, month, day, hour, minute, tzinfo=ALASKA).astimezone(utc.utc)


class ControlTests(TestCase):
    def setUp(self):
        for name, (model, _, _) in OUTPUTS.items():
            model.objects.create()
            m.OutputControl.objects.update_or_create(name=name, defaults={'automatic': True})
        m.SystemStatus.objects.create(automatic=True)
        m.AirTempSetpoint.objects.create(air_temp_setpoint=70)
        m.WaterTempSetpoint.objects.create(water_temp_setpoint=60)
        m.HumiditySetpoint.objects.create(humidity_setpoint=70)
        m.WaterLevel.objects.create()
        initialize_health(at())
        for name, value in [('nursery', 65), ('water', 55), ('humidity', 65), ('greenhouse', 45)]:
            record_scan(name, value, at())
        self.gpio = SimpleNamespace(HIGH=1, LOW=0, output=Mock())

    def schedule(self, name='pump', now=None, frequency=1):
        model = OUTPUTS[name][0]
        row = model.objects.last()
        row.start_hour, row.start_minute, row.duration, row.frequency = 8, 0, 20, frequency
        row.next_start_time = now or at()
        row.save()
        return row

    def test_migration_preserves_existing_global_manual_mode(self):
        import importlib
        from django.apps import apps
        m.OutputControl.objects.all().delete()
        m.SystemStatus.objects.create(automatic=False)
        migration = importlib.import_module('automated_greenhouse.migrations.0015_initialize_output_modes')
        migration.initialize(apps, None)
        self.assertEqual(len(modes()), 8)
        self.assertFalse(any(modes().values()))
        self.assertFalse(m.AirHeaterStatus.objects.last().air_heater_on)

    def test_mixed_modes_leave_manual_heater_off(self):
        set_mode('nursery_heater', False)
        run_outputs(self.gpio, at())
        self.assertFalse(m.AirHeaterStatus.objects.last().air_heater_on)
        self.assertTrue(m.WaterHeaterStatus.objects.last().water_heater_on)
        self.assertTrue(m.FanStatus.objects.last().fan_on)
        self.assertEqual(self.gpio.output.call_count, 8)

    def test_bulk_modes_preserve_output_state(self):
        set_mode('all', False)
        self.assertFalse(any(modes().values()))
        manual_toggle('nursery_heater')
        set_mode('all', True)
        self.assertTrue(all(modes().values()))
        self.assertTrue(m.AirHeaterStatus.objects.last().air_heater_on)

    def test_manual_toggle_never_moves_schedule(self):
        for name in SCHEDULED:
            with self.subTest(name=name):
                start = self.schedule(name).next_start_time
                set_mode(name, False)
                manual_toggle(name)
                manual_toggle(name)
                self.assertEqual(OUTPUTS[name][0].objects.last().next_start_time, start)

    def test_expired_windows_advance_even_in_manual(self):
        for name in SCHEDULED:
            self.schedule(name)
            set_mode(name, False)
            manual_toggle(name)
        run_outputs(self.gpio, at(day=23, hour=12))
        for name in SCHEDULED:
            model, field, _ = OUTPUTS[name]
            row = model.objects.last()
            self.assertTrue(getattr(row, field))
            self.assertEqual(row.next_start_time, at(day=24))

    def test_return_to_auto_mid_window_then_expiry(self):
        self.schedule('garden_valve')
        set_mode('garden_valve', False)
        run_outputs(self.gpio, at(minute=10))
        self.assertFalse(m.GardenValveStatus.objects.last().garden_valve_open)
        set_mode('garden_valve', True)
        run_outputs(self.gpio, at(minute=10))
        self.assertTrue(m.GardenValveStatus.objects.last().garden_valve_open)
        run_outputs(self.gpio, at(minute=20))
        self.assertFalse(m.GardenValveStatus.objects.last().garden_valve_open)
        self.assertEqual(m.GardenValveStatus.objects.last().next_start_time, at(day=21))

    def test_return_to_auto_outside_window_turns_off(self):
        self.schedule('garden_valve')
        set_mode('garden_valve', False)
        manual_toggle('garden_valve')
        set_mode('garden_valve', True)
        run_outputs(self.gpio, at(hour=12))
        self.assertFalse(m.GardenValveStatus.objects.last().garden_valve_open)

    def test_restart_skips_years_preserving_frequency(self):
        row = self.schedule(frequency=3)
        now = at().replace(year=2030) + timedelta(hours=4)
        self.assertFalse(schedule_active(row, now))
        self.assertGreater(row.next_start_time, now)
        self.assertEqual((row.next_start_time.astimezone(ALASKA).date() - at().astimezone(ALASKA).date()).days % 3, 0)

    def test_restart_during_overnight_window(self):
        row = self.schedule()
        row.duration = 1200
        row.save()
        self.assertTrue(schedule_active(row, at(day=23, hour=2)))
        self.assertEqual(row.next_start_time, at(day=22))

    def test_no_initial_reading_faults_after_ten_minutes(self):
        from .sensors import SENSORS
        for model, _, _ in SENSORS.values():
            model.objects.all().delete()
        m.SensorHealth.objects.all().delete()
        initialize_health(at())
        check_faults(at() + timedelta(seconds=599))
        self.assertEqual(m.AlertNotification.objects.count(), 0)
        check_faults(at() + timedelta(seconds=600))
        self.assertEqual(m.AlertNotification.objects.count(), 4)

    def test_schedule_across_dst_keeps_local_start(self):
        row = self.schedule(now=at(month=3, day=7), frequency=1)
        self.assertTrue(schedule_active(row, at(month=3, day=8, minute=10)))
        self.assertEqual(row.next_start_time, at(month=3, day=8))
        row = self.schedule(now=at(month=10, day=31))
        self.assertTrue(schedule_active(row, at(month=11, day=1, minute=10)))
        self.assertEqual(row.next_start_time, at(month=11, day=1))

    def test_zero_schedule_disabled_and_invalid_new_schedule_rejected(self):
        self.assertFalse(schedule_active(m.PumpStatus.objects.last(), at()))
        for args in [(8, 0, 20, 0), (24, 0, 20, 1), (8, 0, -1, 1)]:
            with self.assertRaises(ValueError):
                set_schedule('pump', *args)

    def test_stale_boundary_and_local_seasonal_boundary(self):
        now = at(month=5, day=14, hour=23, minute=59)
        health = SimpleNamespace(last_valid=now - timedelta(seconds=59), last_value=80)
        self.assertFalse(heater_desired(health, 70, False, now))
        health.last_valid -= timedelta(seconds=1)
        self.assertTrue(heater_desired(health, 70, False, now))
        self.assertFalse(heater_desired(health, 70, True, now + timedelta(minutes=1)))
        self.assertFalse(seasonal_heat(at(month=10)))

    def test_both_stale_heaters_use_seasonal_fallback_but_manual_wins(self):
        for now, expected in [(at(), True), (at(month=5, day=15), False)]:
            run_outputs(self.gpio, now + timedelta(seconds=60))
            self.assertEqual(m.AirHeaterStatus.objects.last().air_heater_on, expected)
            self.assertEqual(m.WaterHeaterStatus.objects.last().water_heater_on, expected)
        set_mode('nursery_heater', False)
        run_outputs(self.gpio, at() + timedelta(seconds=60))
        self.assertFalse(m.AirHeaterStatus.objects.last().air_heater_on)

    def test_pump_stops_when_freezing_or_stale(self):
        self.schedule()
        run_outputs(self.gpio, at())
        self.assertTrue(m.PumpStatus.objects.last().pump_on)
        record_scan('water', 32, at() + timedelta(seconds=5))
        run_outputs(self.gpio, at() + timedelta(seconds=5))
        self.assertFalse(m.PumpStatus.objects.last().pump_on)
        record_scan('water', 55, at() + timedelta(seconds=10))
        run_outputs(self.gpio, at() + timedelta(seconds=10))
        self.assertTrue(m.PumpStatus.objects.last().pump_on)
        run_outputs(self.gpio, at() + timedelta(seconds=70))
        self.assertFalse(m.PumpStatus.objects.last().pump_on)

    def test_hysteresis_reasserts_gpio_after_restart(self):
        record_scan('nursery', 71, at())
        m.AirHeaterStatus.objects.create(air_heater_on=True)
        run_outputs(self.gpio, at())
        self.gpio.output.assert_any_call(0, 1)

    def test_vent_conflicting_inputs_create_one_consistent_transition(self):
        record_scan('nursery', 85, at())
        record_scan('humidity', 85, at())
        before = m.VentStatus.objects.count()
        run_outputs(self.gpio, at())
        self.assertTrue(m.VentStatus.objects.last().vent_on)
        self.assertEqual(m.VentStatus.objects.count(), before + 1)
        self.gpio.output.assert_any_call(19, 1)

    def test_fault_once_recovery_once_and_new_outage(self):
        check_faults(at() + timedelta(seconds=599))
        self.assertEqual(m.AlertNotification.objects.count(), 0)
        check_faults(at() + timedelta(minutes=10))
        check_faults(at() + timedelta(minutes=11))
        self.assertEqual(m.AlertNotification.objects.filter(subject__contains='fault').count(), 4)
        initialize_health(at() + timedelta(minutes=11))
        check_faults(at() + timedelta(minutes=12))
        self.assertEqual(m.AlertNotification.objects.count(), 4)
        record_scan('nursery', 68, at() + timedelta(minutes=12))
        record_scan('nursery', 68, at() + timedelta(minutes=13))
        self.assertEqual(m.AlertNotification.objects.filter(subject__contains='recovered').count(), 1)
        check_faults(at() + timedelta(minutes=23))
        self.assertEqual(m.AlertNotification.objects.filter(subject__contains='fault').count(), 5)

    def test_invalid_scans_do_not_refresh_health(self):
        for value in [None, float('nan'), float('inf'), 300]:
            with self.assertRaises((ValueError, TypeError)):
                record_scan('nursery', value, at() + timedelta(minutes=1))
        self.assertEqual(m.SensorHealth.objects.get(name='nursery').last_valid, at())
        with self.assertRaises(ValueError):
            parse_probe('a b NO\na t=22000')
        self.assertEqual(parse_probe('a b YES\na t=20000'), 68)

    def test_faulty_probe_does_not_skip_other_sensors(self):
        scans = ['a NO\nb t=0', 'a YES\nb t=20000', 'a YES\nb t=21000']
        with patch('scripts.hardware.Path.read_text', side_effect=scans), patch('scripts.hardware.log_error'):
            read_sensors(SimpleNamespace(DHT11=11, read_retry=Mock(return_value=(50, 20))))
        self.assertEqual(m.SensorHealth.objects.get(name='water').last_value, 68)
        self.assertEqual(m.SensorHealth.objects.get(name='humidity').last_value, 50)

    def test_control_posts_require_superuser_and_manual_mode(self):
        data = {'set_mode': 'manual', 'output': 'all'}
        self.assertEqual(self.client.post('/', data).status_code, 403)
        user = m.User.objects.create_user(username='viewer', password='test')
        self.client.force_login(user)
        self.assertEqual(self.client.post('/', data).status_code, 403)
        user.is_superuser = True
        user.save()
        self.client.post('/', {'toggle_nursery_heater': 'on'})
        self.assertFalse(m.AirHeaterStatus.objects.last().air_heater_on)
        self.client.post('/', data)
        self.client.post('/', {'toggle_nursery_heater': 'on'})
        self.assertTrue(m.AirHeaterStatus.objects.last().air_heater_on)

    def test_mixed_dashboard_has_eight_modes_and_correct_buttons(self):
        user = m.User.objects.create_superuser(username='admin', email='', password='test')
        self.client.force_login(user)
        set_mode('nursery_heater', False)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'System Status: Mixed')
        self.assertContains(response, 'name="output"', count=9)
        self.assertContains(response, 'id="nursery_heater_button"')
        self.assertNotContains(response, 'id="water_heater_button"')
        self.assertEqual(self.client.get('/api/api_get_system_status').json()['system_status'], 'Mixed')

    def test_retention_preserves_latest_states_frost_and_pending_mail(self):
        old = at().replace(year=2020)
        for model in [m.NurseryAirTemp, m.AirTempSetpoint, m.PumpStatus]:
            first = model.objects.first()
            model.objects.filter(pk=first.pk).update(created_at=old)
            latest = model.objects.create()
            model.objects.filter(pk=latest.pk).update(created_at=old)
        frost = m.LastFrostGreenhouse.objects.create(id=0)
        m.LastFrostGreenhouse.objects.filter(pk=0).update(created_at=old)
        pending = m.AlertNotification.objects.create(subject='pending', body='', created_at=old)
        sent = m.AlertNotification.objects.create(subject='sent', body='', created_at=old, sent_at=old)
        call_command('prune_history', stdout=StringIO())
        self.assertEqual(m.NurseryAirTemp.objects.count(), 2)
        call_command('prune_history', apply=True, stdout=StringIO())
        self.assertEqual(m.NurseryAirTemp.objects.count(), 1)
        self.assertEqual(m.AirTempSetpoint.objects.count(), 1)
        self.assertEqual(m.PumpStatus.objects.count(), 1)
        self.assertEqual(m.LastFrostGreenhouse.objects.get(pk=frost.pk).created_at, old)
        self.assertTrue(m.AlertNotification.objects.filter(pk=pending.pk).exists())
        self.assertFalse(m.AlertNotification.objects.filter(pk=sent.pk).exists())
        self.assertEqual(m.OutputControl.objects.count(), 8)

    def test_calendar_retention_month_end(self):
        cutoff = retention_cutoff(at(month=5, day=31))
        self.assertEqual((cutoff.month, cutoff.day), (2, 28))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                       EMAIL_HOST='test.example', DEFAULT_FROM_EMAIL='greenhouse@example.com',
                       GREENHOUSE_ALERT_RECIPIENT='your-account@yahoo.com')
    def test_mail_worker_delivery_retry_and_deduplication(self):
        alert = m.AlertNotification.objects.create(subject='fault', body='test')
        with patch('automated_greenhouse.management.commands.send_sensor_alerts.send_mail', side_effect=OSError):
            call_command('send_sensor_alerts', stdout=StringIO(), stderr=StringIO())
        alert.refresh_from_db()
        self.assertEqual(alert.attempts, 1)
        self.assertIsNone(alert.sent_at)
        m.AlertNotification.objects.filter(pk=alert.pk).update(next_attempt=at().replace(year=2020))
        call_command('send_sensor_alerts', stdout=StringIO())
        call_command('send_sensor_alerts', stdout=StringIO())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['your-account@yahoo.com'])
