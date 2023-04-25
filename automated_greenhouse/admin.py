from django.contrib import admin
from .models import User, SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel, LastFrostGreenhouse
from .models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus, SystemError
from .models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus


# Register your models here.
admin.site.register(OutsideAirTemp)
admin.site.register(WaterTemp)
admin.site.register(NurseryAirTemp)
admin.site.register(User)
admin.site.register(SystemStatus)
admin.site.register(Humidity)
admin.site.register(WaterLevel)
admin.site.register(PumpStatus)
admin.site.register(FanStatus)
admin.site.register(VentStatus)
admin.site.register(AirHeaterStatus)
admin.site.register(WaterHeaterStatus)
admin.site.register(GardenValveStatus)
admin.site.register(GreenhouseTreeValveStatus)
admin.site.register(GreenhousePlanterValveStatus)
admin.site.register(AirTempSetpoint)
admin.site.register(WaterTempSetpoint)
admin.site.register(HumiditySetpoint)
admin.site.register(LastFrostGreenhouse)
admin.site.register(SystemError)