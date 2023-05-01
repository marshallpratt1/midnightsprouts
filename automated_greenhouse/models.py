from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta, datetime
# Create your models here.
AKDT_OFFSET = -8

class User(AbstractUser):
    pass


class SystemStatus(models.Model):
    automatic = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.automatic:
            return f"System changed to AUTOMATIC: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        return f"System changed to MANUAL: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class SystemError(models.Model):
    error_message = models.TextField()
    created_at = created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.error_message} occured: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class OutsideAirTemp(models.Model):
    outside_air_temp = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True, )

    def __str__(self):
        return f"{self.outside_air_temp}F: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
    
class LastFrostGreenhouse(models.Model):
    created_at = models.DateTimeField(auto_now=True)

class WaterTemp(models.Model):
    water_temp = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.water_temp}F: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class NurseryAirTemp(models.Model):
    nursery_air_temp = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nursery_air_temp}F: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class Humidity(models.Model):
    humidity = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.humidity}% humidity: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class WaterLevel(models.Model):
    water_level = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

class AirTempSetpoint(models.Model):
    air_temp_setpoint = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.air_temp_setpoint}F added as setpoint: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class WaterTempSetpoint(models.Model):
    water_temp_setpoint = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.water_temp_setpoint}F added as setpoint: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class HumiditySetpoint(models.Model):
    humidity_setpoint = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return f"{self.humidity_setpoint}% added as setpoint: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class FanStatus(models.Model):
    fan_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        previous = FanStatus.objects.filter(id=self.id-1)[0]
        if previous.fan_on and not self.fan_on:
            return f"Fan turned off: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        elif not previous.fan_on and self.fan_on:
            return f"Fan turned on: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        else:
            return f"Fan status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        
class VentStatus(models.Model):
    vent_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            previous = VentStatus.objects.filter(id=self.id-1)[0]
            if previous.vent_on and not self.vent_on:
                return f"Vent turned off: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
            elif not previous.vent_on and self.vent_on:
                return f"Vent turned on: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
            else:
                return f"Vent status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class AirHeaterStatus(models.Model):
    air_heater_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        previous = AirHeaterStatus.objects.filter(id=self.id-1)[0]
        if previous.air_heater_on and not self.air_heater_on:
            return f"Heater turned off: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        elif not previous.air_heater_on and self.air_heater_on:
            return f"Heater turned on: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        else:
            return f"Heater status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class WaterHeaterStatus(models.Model):
    water_heater_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        previous = WaterHeaterStatus.objects.filter(id=self.id-1)[0]
        if previous.water_heater_on and not self.water_heater_on:
            return f"Heater turned off: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        elif not previous.water_heater_on and self.water_heater_on:
            return f"Heater turned on: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        else:
            return f"Heater status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"


class PumpStatus(models.Model):
    pump_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    start_hour = models.IntegerField(default=0)
    start_minute = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    frequency = models.IntegerField(default=0)
    next_start_time = models.DateTimeField(default=timezone.now) #this gets stored in local alaska time

    def __str__(self):
        if PumpStatus.objects.filter(id=self.id-1).exits():
            previous = PumpStatus.objects.filter(id=self.id-1)[0]
            if previous.start_hour != self.start_hour or previous.start_minute != self.start_minute or previous.duration != self.duration or previous.frequency != self.frequency:
                return f"New pump times created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
            if not previous.pump_on and self.pump_on:
                return f"On: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
            if previous.pump_on and not self.pump_on:
                return f"Off: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        return f"Pump status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"


class GardenValveStatus(models.Model):
    garden_valve_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    start_hour = models.IntegerField(default=0)
    start_minute = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    frequency = models.IntegerField(default=0)
    next_start_time = models.DateTimeField(default=timezone.now) #this gets stored in local alaska time

    def __str__(self):
        previous = GardenValveStatus.objects.filter(id=self.id-1)[0]
        if previous.start_hour != self.start_hour or previous.start_minute != self.start_minute or previous.duration != self.duration or previous.frequency != self.frequency:
            return f"New garden valve times created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        if not previous.garden_valve_open and self.garden_valve_open:
            return f"Opened: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        if previous.garden_valve_open and not self.garden_valve_open:
            return f"Closed: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        return f"Garden valve status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class GreenhousePlanterValveStatus(models.Model):
    greenhouse_planter_valve_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    start_hour = models.IntegerField(default=0)
    start_minute = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    frequency = models.IntegerField(default=0)
    next_start_time = models.DateTimeField(default=timezone.now) #this gets stored in local alaska time

    def __str__(self):
        previous = GreenhousePlanterValveStatus.objects.filter(id=self.id-1)[0]
        if previous.start_hour != self.start_hour or previous.start_minute != self.start_minute or previous.duration != self.duration or previous.frequency != self.frequency:
            return f"New Greenhouse Planter valve times created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        if not previous.greenhouse_planter_valve_open and self.greenhouse_planter_valve_open:
            return f"Opened: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        if previous.greenhouse_planter_valve_open and not self.greenhouse_planter_valve_open:
            return f"Closed: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        return f"Greenhouse Planter valve status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"

class GreenhouseTreeValveStatus(models.Model):
    greenhouse_tree_valve_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    start_hour = models.IntegerField(default=0)
    start_minute = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    frequency = models.IntegerField(default=0)
    next_start_time = models.DateTimeField(default=timezone.now) #this gets stored in local alaska time

    def __str__(self):
        previous = GreenhouseTreeValveStatus.objects.filter(id=self.id-1)[0]
        if previous.start_hour != self.start_hour or previous.start_minute != self.start_minute or previous.duration != self.duration or previous.frequency != self.frequency:
            return f"New Greenhouse Tree valve times created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        if not previous.greenhouse_tree_valve_open and self.greenhouse_tree_valve_open:
            return f"Opened: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        if previous.greenhouse_tree_valve_open and not self.greenhouse_tree_valve_open:
            return f"Closed: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"
        return f"Greenhouse Tree valve status object created: {(self.created_at + timedelta(hours=AKDT_OFFSET)).strftime('%B %d, %Y at: %X')}"