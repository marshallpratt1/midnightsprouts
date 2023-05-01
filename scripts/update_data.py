from automated_greenhouse.models import SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel, LastFrostGreenhouse
from automated_greenhouse.models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus, SystemError
from automated_greenhouse.models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus
import random
from datetime import datetime, timezone, timedelta
from time import sleep
from automated_greenhouse.util import *

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

        pump = PumpStatus.objects.last()
        now_time = datetime.now(timezone.utc)
        if ((pump.next_start_time <= now_time) and (pump.next_start_time + timedelta(minutes=pump.duration) > now_time)):
            if(pump.pump_on == False):
                print("turning on pump")
                toggle_pump()
        else:
            if(pump.pump_on == True):
                print("turning off pump")
                toggle_pump()

        valve = GardenValveStatus.objects.last()
        now_time = datetime.now(timezone.utc)
        if ((valve.next_start_time <= now_time) and (valve.next_start_time + timedelta(minutes=valve.duration) > now_time)):
            if(valve.garden_valve_open == False):
                print("Opening garden valve")
                toggle_garden_valve()
        else:
            if(valve.garden_valve_open == True):
                print("Closing garden valve")
                toggle_garden_valve()
        
        valve = GreenhousePlanterValveStatus.objects.last()
        now_time = datetime.now(timezone.utc)
        if ((valve.next_start_time <= now_time) and (valve.next_start_time + timedelta(minutes=valve.duration) > now_time)):
            if(valve.greenhouse_planter_valve_open == False):
                print("Opening greenhouse planter valve")
                toggle_greenhouse_planter_valve()
        else:
            if(valve.greenhouse_planter_valve_open == True):
                print("Closing greenhouse planter valve")
                toggle_greenhouse_planter_valve()

        valve = GreenhouseTreeValveStatus.objects.last()
        now_time = datetime.now(timezone.utc)
        if ((valve.next_start_time <= now_time) and (valve.next_start_time + timedelta(minutes=valve.duration) > now_time)):
            if(valve.greenhouse_tree_valve_open == False):
                print("Opening greenhouse tree valve")
                toggle_greenhouse_tree_valve()
        else:
            if(valve.greenhouse_tree_valve_open == True):
                print("Closing greenhouse tree valve")
                toggle_greenhouse_tree_valve()

        count += 1
        sleep(2)