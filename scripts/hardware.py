"""Run via `python manage.py runscript hardware` on the Pi."""
import logging
import time
from pathlib import Path

from automated_greenhouse import models as m
from automated_greenhouse.control import OUTPUTS, run_outputs
from automated_greenhouse.sensors import initialize_health, record_scan, check_faults

logger = logging.getLogger(__name__)
DHT_DATA_PIN = 22
SENSOR_PATHS = {
    'greenhouse': '/sys/bus/w1/devices/28-0306979407ca/w1_slave',
    'water': '/sys/bus/w1/devices/28-030d979455e5/w1_slave',
    'nursery': '/sys/bus/w1/devices/28-03039794473f/w1_slave',
}
_last_error = {}


def log_error(key, error):
    # Bound DB growth and repeated log noise during persistent failures.
    now = time.monotonic()
    if key not in _last_error or now - _last_error[key] >= 600:
        logger.error('%s: %s', key, error)
        try:
            m.SystemError.objects.create(error_message='{}: {}'.format(key, error))
        except Exception:
            logger.exception('Could not save error to database')
        _last_error[key] = now


def parse_probe(text):
    lines = text.splitlines()
    if len(lines) < 2 or not lines[0].strip().endswith('YES') or 't=' not in lines[1]:
        raise ValueError('Invalid DS18B20 scan or CRC')
    celsius = float(lines[1].split('t=', 1)[1]) / 1000
    if not -55 <= celsius <= 125:
        raise ValueError('DS18B20 reading outside physical range')
    return round(celsius * 1.8 + 32, 1)


def read_sensors(dht):
    for name, path in SENSOR_PATHS.items():
        try:
            record_scan(name, parse_probe(Path(path).read_text()))
        except Exception as error:
            log_error(name, error)
    try:
        # One attempt per control cycle; the library's long retry loop must not
        # stall heater fallback decisions or scheduled output shutoffs.
        humidity, _ = dht.read_retry(dht.DHT11, DHT_DATA_PIN, retries=1)
        record_scan('humidity', humidity)
    except Exception as error:
        log_error('humidity', error)


def run():
    import Adafruit_DHT
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for _, _, pin in OUTPUTS.values():
        GPIO.setup(pin, GPIO.OUT)
    initialize_health()
    while True:
        try:
            read_sensors(Adafruit_DHT)
            run_outputs(GPIO)
            check_faults()
        except Exception as error:
            log_error('Hardware control loop', error)
        finally:
            # Always back off, including when the database or control loop fails.
            time.sleep(5)


if __name__ == '__main__':
    run()
