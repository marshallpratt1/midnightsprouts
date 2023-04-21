from automated_greenhouse.models import SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from automated_greenhouse.models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus
from automated_greenhouse.models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus

def run():
    outside_air_temps = [30,30,30,30,30,35,35,35,35,35,40,40,40,40,40,45,45,45,45,45]
    air_temps = [70, 70, 70, 70, 70, 71, 71, 71, 71, 71, 72, 72, 72, 72, 72, 73, 73, 73, 73, 73 ]
    water_temps = [70, 70, 70, 70, 70, 71, 71, 71, 71, 71, 72, 72, 72, 72, 72, 73, 73, 73, 73, 73]
    humidity_levels = [70, 70, 70, 70, 70, 71, 71, 71, 71, 71, 72, 72, 72, 72, 72, 73, 73, 73, 73, 73]
    water_levels = [True, True, True, True, False, True, False, True, True, True, True, True, True, True, False, True, False, True, True, True]
    
    air_temp_setpoints = [80, 80, 82, 82, 85, 80, 80, 82, 82, 85]
    water_temp_setpoints = [75, 75, 70, 78, 80, 75, 75, 70, 78, 80]
    humidity_setpoints = [75, 75, 70, 78, 80, 75, 75, 70, 78, 80]

    new_automatic = SystemStatus()
    new_automatic.save()

    pump_status = PumpStatus()
    pump_status.save()
    fan_status = FanStatus()
    fan_status.save()
    vent_status = VentStatus()
    vent_status.save()
    air_heater_status = AirHeaterStatus()
    air_heater_status.save()
    water_heater_status = WaterHeaterStatus()
    water_heater_status.save()
    valve_status = GardenValveStatus()
    valve_status.save()
    valve_status = GreenhousePlanterValveStatus()
    valve_status.save()
    valve_status = GreenhouseTreeValveStatus()
    valve_status.save()
    air_temp_setpoint = AirTempSetpoint()
    air_temp_setpoint.save()
    water_setpoint = WaterTempSetpoint()
    water_setpoint.save()
    humidity_setpoint = HumiditySetpoint()
    humidity_setpoint.save()

    for i in range(len(outside_air_temps)):
        outside_air  = OutsideAirTemp(outside_air_temp = outside_air_temps[i])
        outside_air.save()
        water_temp = WaterTemp(water_temp = water_temps[i])
        water_temp.save()
        nursery_temp = NurseryAirTemp(nursery_air_temp = air_temps[i])
        nursery_temp.save()
        humidity_level = Humidity(humidity = humidity_levels[i])
        humidity_level.save()
        water_lev = WaterLevel(water_level = water_levels[i])
        water_lev.save()