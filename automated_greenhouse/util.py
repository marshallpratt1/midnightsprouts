from .models import User, SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from .models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, Valve1Status
from .models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint
from datetime import timedelta, datetime

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
    new_pump_status.save()

def toggle_drain_valve():
    old_valve_status = Valve1Status.objects.order_by('-id')[0]
    new_valve_status = Valve1Status(valve1_open = False) if old_valve_status.valve1_open else Valve1Status(valve1_open = True)
    new_valve_status.save()

def toggle_fan():
    old_status = FanStatus.objects.order_by('-id')[0]
    new_status = FanStatus(fan_on = False) if old_status.fan_on else FanStatus(fan_on = True)
    new_status.save()

def toggle_vent():
    old_status = VentStatus.objects.order_by('-id')[0]
    new_status = VentStatus(vent_on = False) if old_status.vent_on else VentStatus(vent_on = True)
    new_status.save()

def get_date_time_labels(dt_str):
    result = []
    for time in dt_str:
        result.append(str(time + timedelta(hours = -9))[6:16])
    return result