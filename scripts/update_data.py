from automated_greenhouse.models import SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel, LastFrostGreenhouse
from automated_greenhouse.models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus, SystemError
from automated_greenhouse.models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus
import random
from time import sleep

def run():
    greenhouse_temps = [34,34,35,36,35,35,34,34,34,33,33,32]
    count = 0
    while True:
        new_object = NurseryAirTemp(nursery_air_temp = random.randint(60,70))
        new_object.save()
        new_object = OutsideAirTemp(outside_air_temp = greenhouse_temps[count % len(greenhouse_temps)])
        new_object.save()
        if (new_object.outside_air_temp <= 32):
            new_object, created = LastFrostGreenhouse.objects.get_or_create(id = 0)
            new_object.save()
            new_object = SystemError(error_message = "The temperature is too low!")
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
        count += 1
        sleep(2)