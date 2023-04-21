from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta, datetime
# Create your models here.


class User(AbstractUser):
    pass


class SystemStatus(models.Model):
    automatic = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)


class OutsideAirTemp(models.Model):
    outside_air_temp = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True, )

    def __str__(self) -> str:
        return f"{self.outside_air_temp} °F at {self.created_at}"


class WaterTemp(models.Model):
    water_temp = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True)


class NurseryAirTemp(models.Model):
    nursery_air_temp = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True)


class Humidity(models.Model):
    humidity = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True)


class WaterLevel(models.Model):
    water_level = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)


class FanStatus(models.Model):
    fan_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)


class PumpStatus(models.Model):
    pump_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)


class VentStatus(models.Model):
    vent_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)


class AirHeaterStatus(models.Model):
    air_heater_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)


class WaterHeaterStatus(models.Model):
    water_heater_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)


class GardenValveStatus(models.Model):
    garden_valve_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

class GreenhousePlanterValveStatus(models.Model):
    greenhouse_planter_valve_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

class GreenhouseTreeValveStatus(models.Model):
    greenhouse_tree_valve_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)


class AirTempSetpoint(models.Model):
    air_temp_setpoint = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now=True)


class WaterTempSetpoint(models.Model):
    water_temp_setpoint = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now=True)


class HumiditySetpoint(models.Model):
    humidity_setpoint = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now=True)
