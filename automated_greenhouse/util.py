from .models import User, SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from .models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus
from .models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus
from datetime import timedelta, datetime 
import json

def update_air_temp_setpoint(setpoint):
    new_setpoint = AirTempSetpoint(air_temp_setpoint=int(setpoint))
    new_setpoint.save()

def update_humidity_setpoint(setpoint):
    new_setpoint = HumiditySetpoint(humidity_setpoint=int(setpoint))
    new_setpoint.save()

def update_water_temp_setpoint(setpoint):
    new_setpoint = WaterTempSetpoint(water_temp_setpoint=int(setpoint))
    new_setpoint.save()

def toggle_system_status():
    old_status = SystemStatus.objects.order_by('-id')[0]
    new_status = SystemStatus(automatic = False) if old_status.automatic else SystemStatus(automatic = True)
    new_status.save()

def toggle_nursery_heater():
    old_heater_status = AirHeaterStatus.objects.order_by('-id')[0]
    new_heater_status = AirHeaterStatus(air_heater_on = False) if old_heater_status.air_heater_on else AirHeaterStatus(air_heater_on = True)
    new_heater_status.save()

def toggle_water_heater():
    old_heater_status = WaterHeaterStatus.objects.order_by('-id')[0]
    new_heater_status = WaterHeaterStatus(water_heater_on = False) if old_heater_status.water_heater_on else WaterHeaterStatus(water_heater_on = True)
    new_heater_status.save()

def toggle_pump():
    old_pump_status = PumpStatus.objects.order_by('-id')[0]
    new_pump_status = PumpStatus(pump_on = False) if old_pump_status.pump_on else PumpStatus(pump_on = True)
    new_pump_status.start_hour = old_pump_status.start_hour
    new_pump_status.start_minute = old_pump_status.start_minute
    new_pump_status.duration = old_pump_status.duration
    new_pump_status.save()

def toggle_garden_valve():
    old_valve_status = GardenValveStatus.objects.order_by('-id')[0]
    new_valve_status = GardenValveStatus(garden_valve_open = False) if old_valve_status.garden_valve_open else GardenValveStatus(garden_valve_open = True)
    new_valve_status.start_hour = old_valve_status.start_hour
    new_valve_status.start_minute = old_valve_status.start_minute
    new_valve_status.duration = old_valve_status.duration
    new_valve_status.save()

def toggle_greenhouse_planter_valve():
    old_valve_status = GreenhousePlanterValveStatus.objects.order_by('-id')[0]
    new_valve_status = GreenhousePlanterValveStatus(greenhouse_planter_valve_open = False) if old_valve_status.greenhouse_planter_valve_open else GreenhousePlanterValveStatus(greenhouse_planter_valve_open = True)
    new_valve_status.start_hour = old_valve_status.start_hour
    new_valve_status.start_minute = old_valve_status.start_minute
    new_valve_status.duration = old_valve_status.duration
    new_valve_status.save()

def toggle_greenhouse_tree_valve():
    old_valve_status = GreenhouseTreeValveStatus.objects.order_by('-id')[0]
    new_valve_status = GreenhouseTreeValveStatus(greenhouse_tree_valve_open = False) if old_valve_status.greenhouse_tree_valve_open else GreenhouseTreeValveStatus(greenhouse_tree_valve_open = True)
    new_valve_status.start_hour = old_valve_status.start_hour
    new_valve_status.start_minute = old_valve_status.start_minute
    new_valve_status.duration = old_valve_status.duration
    new_valve_status.save()

def toggle_fan():
    old_status = FanStatus.objects.order_by('-id')[0]
    new_status = FanStatus(fan_on = False) if old_status.fan_on else FanStatus(fan_on = True)
    new_status.save()

def toggle_vent():
    old_status = VentStatus.objects.order_by('-id')[0]
    new_status = VentStatus(vent_on = False) if old_status.vent_on else VentStatus(vent_on = True)
    new_status.save()

def set_garden_valve_times(hour, minute, duration):
    old_valve_status = GardenValveStatus.objects.order_by('-id')[0]
    new_valve_status = GardenValveStatus(garden_valve_open = True) if old_valve_status.garden_valve_open else GardenValveStatus(garden_valve_open = False)
    new_valve_status.start_hour = hour
    new_valve_status.start_minute = minute
    new_valve_status.duration = duration
    new_valve_status.save()

def set_greenhouse_valve_times(hour, minute, duration):
    old_valve_status = GreenhouseTreeValveStatus.objects.order_by('-id')[0]
    new_valve_status = GreenhouseTreeValveStatus(greenhouse_tree_valve_open = True) if old_valve_status.greenhouse_tree_valve_open else GreenhouseTreeValveStatus(greenhouse_tree_valve_open = False)
    new_valve_status.start_hour = hour
    new_valve_status.start_minute = minute
    new_valve_status.duration = duration
    new_valve_status.save()



NUMBER_OF_CHART_DATAPOINTS = 20

def get_date_time_labels():

    time_labels = [x.created_at for x in OutsideAirTemp.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    time_labels.reverse()
    result = []
    for time in time_labels:
        result.append(str(time + timedelta(hours=-8))[6:16])
    return json.dumps(result)


def get_historical_nursery_temps():
    historical_nursery_temps = [x.nursery_air_temp for x in NurseryAirTemp.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    historical_nursery_temps.reverse()
    json.dumps(historical_nursery_temps)
    return historical_nursery_temps

def get_historical_greenhouse_temps():
    historical_greenhouse_temps = [x.outside_air_temp for x in OutsideAirTemp.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    historical_greenhouse_temps.reverse()
    json.dumps(historical_greenhouse_temps)
    return historical_greenhouse_temps

def get_historical_humidity():
    get_historical_humidity = [x.humidity for x in Humidity.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    get_historical_humidity.reverse()
    json.dumps(get_historical_humidity)
    return get_historical_humidity

def get_historical_water_temps():
    historical_water_temps = [x.water_temp for x in WaterTemp.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    historical_water_temps.reverse()
    json.dumps(historical_water_temps)
    return historical_water_temps
