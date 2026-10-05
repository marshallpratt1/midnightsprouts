from .models import User, SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from .models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus
from .models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus
from datetime import timedelta, datetime, timezone
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
    from .control import modes, set_mode
    set_mode('all', not all(modes().values()))

def toggle_nursery_heater():
    from .control import manual_toggle
    manual_toggle('nursery_heater')

def toggle_water_heater():
    from .control import manual_toggle
    manual_toggle('water_heater')

def toggle_pump():
    from .control import manual_toggle
    manual_toggle('pump')

def toggle_garden_valve():
    from .control import manual_toggle
    manual_toggle('garden_valve')

def toggle_greenhouse_planter_valve():
    from .control import manual_toggle
    manual_toggle('greenhouse_planter_valve')

def toggle_greenhouse_tree_valve():
    from .control import manual_toggle
    manual_toggle('greenhouse_tree_valve')

def toggle_fan():
    from .control import manual_toggle
    manual_toggle('fan')

def toggle_vent():
    from .control import manual_toggle
    manual_toggle('vent')

def set_garden_valve_times(hour, minute, duration, frequency):
    from .control import set_schedule
    set_schedule('garden_valve', hour, minute, duration, frequency)

def set_greenhouse_tree_valve_times(hour, minute, duration, frequency):
    from .control import set_schedule
    set_schedule('greenhouse_tree_valve', hour, minute, duration, frequency)

def set_greenhouse_planter_valve_times(hour, minute, duration, frequency):
    from .control import set_schedule
    set_schedule('greenhouse_planter_valve', hour, minute, duration, frequency)

def set_pump_times(hour, minute, duration, frequency):
    from .control import set_schedule
    set_schedule('pump', hour, minute, duration, frequency)

NUMBER_OF_CHART_DATAPOINTS = 100
AKDT_OFFSET = -8

def get_greenhouse_date_time_labels():
    time_labels = [x.created_at for x in OutsideAirTemp.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    time_labels.reverse()
    result = []
    for time in time_labels:
        result.append(str(time + timedelta(hours=AKDT_OFFSET))[6:16])
    return json.dumps(result)

def get_nursery_date_time_labels():
    time_labels = [x.created_at for x in NurseryAirTemp.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    time_labels.reverse()
    result = []
    for time in time_labels:
        result.append(str(time + timedelta(hours=AKDT_OFFSET))[6:16])
    return json.dumps(result)

def get_humidity_date_time_labels():
    time_labels = [x.created_at for x in Humidity.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    time_labels.reverse()
    result = []
    for time in time_labels:
        result.append(str(time + timedelta(hours=AKDT_OFFSET))[6:16])
    return json.dumps(result)

def get_water_date_time_labels():
    time_labels = [x.created_at for x in OutsideAirTemp.objects.order_by('-id')[:NUMBER_OF_CHART_DATAPOINTS]]
    time_labels.reverse()
    result = []
    for time in time_labels:
        result.append(str(time + timedelta(hours=AKDT_OFFSET))[6:16])
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
