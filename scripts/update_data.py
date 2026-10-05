"""Development simulator: use only with a separate test database, never on the Pi."""
import random
from time import sleep

from automated_greenhouse.control import run_outputs
from automated_greenhouse.sensors import initialize_health, record_scan, check_faults


class SimulatedGPIO:
    HIGH = 1
    LOW = 0

    @staticmethod
    def output(pin, value):
        pass


def run():
    initialize_health()
    while True:
        record_scan('nursery', random.randint(60, 70))
        record_scan('greenhouse', random.randint(32, 36))
        record_scan('humidity', random.randint(65, 75))
        record_scan('water', random.randint(50, 55))
        run_outputs(SimulatedGPIO)
        check_faults()
        sleep(5)
