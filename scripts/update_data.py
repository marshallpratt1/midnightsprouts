from automated_greenhouse.models import SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from automated_greenhouse.models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus
from automated_greenhouse.models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus
import random
from time import sleep

def run():
    while True:
        new_object = NurseryAirTemp(nursery_air_temp = random.randint(60,70))
        new_object.save()
        new_object = OutsideAirTemp(outside_air_temp = random.randint(50,60))
        new_object.save()
        new_object = Humidity(humidity = random.randint(65,75))
        new_object.save()
        new_object = WaterTemp(water_temp = random.randint(50,55))
        new_object.save()
        new_object = AirHeaterStatus(air_heater_on = random.randint(0,1))
        new_object.save()
        new_object = PumpStatus(pump_on = random.randint(0,1))
        new_object.save()
        new_object = FanStatus(fan_on = random.randint(0,1))
        new_object.save()
        new_object = VentStatus(vent_on = random.randint(0,1))
        new_object.save()
        new_object = WaterHeaterStatus(water_heater_on = random.randint(0,1))
        new_object.save()
        new_object = GardenValveStatus(garden_valve_open = random.randint(0,1))
        new_object.save()
        new_object = GreenhousePlanterValveStatus(greenhouse_planter_valve_open = random.randint(0,1))
        new_object.save()
        new_object = GreenhouseTreeValveStatus(greenhouse_tree_valve_open = random.randint(0,1))
        new_object.save()
        #new_object = SystemStatus(automatic = random.randint(0,1))
        #new_object.save()

        sleep(2)
