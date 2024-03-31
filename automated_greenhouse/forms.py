from django import forms
from .models import User, PumpStatus, GardenValveStatus, GreenhouseTreeValveStatus, GreenhousePlanterValveStatus
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address')

    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password1', 
            'password2', 
            ]

class AirTempForm(forms.Form):
    air_temp_setpoint = forms.IntegerField(initial=80, min_value=50, max_value=90, label="Air Temp Setpoint")

class HumidityForm(forms.Form):
    humidity_setpoint = forms.IntegerField(initial=80, min_value=50, max_value=100, label="Humidity Setpoint")

class WaterForm(forms.Form):
    water_setpoint = forms.IntegerField(initial=60, min_value=40, max_value=70, label="Water Temp Setpoint")

class SystemStatusForm(forms.Form):
    change_status = forms.BooleanField(label='Change System Control:')

class ClearLogsForm(forms.Form):
    clear_logs = forms.BooleanField(label='Clear Error Logs:')

class NurseryHeaterForm(forms.Form):
    toggle_nursery_heater = forms.BooleanField(label='Toggle Nursery Heater:')

class WaterHeaterForm(forms.Form):
    toggle_water_heater = forms.BooleanField(label='Toggle Water Heater:')

class PumpForm(forms.Form):
    toggle_pump = forms.BooleanField(label='Toggle Pump:')

class PumpTimeForm(forms.Form):
    pump_start_hour = forms.IntegerField(label='Start time, hour (24hr time):', min_value=0, max_value=23)
    start_minute = forms.IntegerField(label=mark_safe('Start time, minute:'), min_value=0, max_value=59)
    duration = forms.IntegerField(label=mark_safe('Duration in minutes:'), min_value=0)
    frequency = forms.IntegerField(label=mark_safe('Repeat every __ days:'), min_value=0)

    def __init__(self, *args, **kwargs):
        kwargs.update(initial = {
            'pump_start_hour': PumpStatus.objects.last().start_hour,
            'start_minute': PumpStatus.objects.last().start_minute,
            'duration' : PumpStatus.objects.last().duration,
            'frequency' : PumpStatus.objects.last().frequency,
        })
        super(PumpTimeForm, self).__init__(*args, **kwargs)

class GardenValveForm(forms.Form):
    toggle_garden_valve = forms.BooleanField(label='Toggle Garden Valve:')

class GardenValveTimeForm(forms.Form):
    garden_start_hour = forms.IntegerField(label='Start time, hour (24hr time):', min_value=0, max_value=23)
    start_minute = forms.IntegerField(label='Start time, minute:', min_value=0, max_value=59)
    duration = forms.IntegerField(label='Duration in minutes:', min_value=0)
    frequency = forms.IntegerField(label=mark_safe('Repeat every __ days:'), min_value=0)

    def __init__(self, *args, **kwargs):
        kwargs.update(initial = {
            'garden_start_hour': GardenValveStatus.objects.last().start_hour,
            'start_minute': GardenValveStatus.objects.last().start_minute,
            'duration' : GardenValveStatus.objects.last().duration,
            'frequency' : GardenValveStatus.objects.last().frequency,
        })
        super(GardenValveTimeForm, self).__init__(*args, **kwargs)

class GreenhousePlanterValveForm(forms.Form):
    toggle_greenhouse_planter_valve = forms.BooleanField(label='Toggle Greenhouse Planter Valve:')

class GreenhousePlanterValveTimeForm(forms.Form):
    planter_start_hour = forms.IntegerField(label='Start time, hour (24hr time):', min_value=0, max_value=23)
    start_minute = forms.IntegerField(label='Start time, minute:', min_value=0, max_value=59)
    duration = forms.IntegerField(label='Duration in minutes:', min_value=0)
    frequency = forms.IntegerField(label=mark_safe('Repeat every __ days:'), min_value=0)

    def __init__(self, *args, **kwargs):
        kwargs.update(initial = {
            'planter_start_hour': GreenhousePlanterValveStatus.objects.last().start_hour,
            'start_minute': GreenhousePlanterValveStatus.objects.last().start_minute,
            'duration' : GreenhousePlanterValveStatus.objects.last().duration,
            'frequency' : GreenhousePlanterValveStatus.objects.last().frequency,
        })
        super(GreenhousePlanterValveTimeForm, self).__init__(*args, **kwargs)

class GreenhouseTreeValveForm(forms.Form):
    toggle_greenhouse_tree_valve = forms.BooleanField(label='Toggle Greenhouse Tree Valve:')

class GreenhouseTreeValveTimeForm(forms.Form):
    tree_start_hour = forms.IntegerField(label='Start time, hour (24hr time):', min_value=0, max_value=23)
    start_minute = forms.IntegerField(label='Start time, minute:', min_value=0, max_value=59)
    duration = forms.IntegerField(label='Duration in minutes:', min_value=0)
    frequency = forms.IntegerField(label=mark_safe('Repeat every __ days:'), min_value=0)

    def __init__(self, *args, **kwargs):
        kwargs.update(initial = {
            'tree_start_hour': GreenhouseTreeValveStatus.objects.last().start_hour,
            'start_minute': GreenhouseTreeValveStatus.objects.last().start_minute,
            'duration' : GreenhouseTreeValveStatus.objects.last().duration,
            'frequency' : GreenhouseTreeValveStatus.objects.last().frequency,
        })
        super(GreenhouseTreeValveTimeForm, self).__init__(*args, **kwargs)

class FanForm(forms.Form):
    toggle_fan = forms.BooleanField(label='Toggle Fan:')

class VentForm(forms.Form):
    toggle_vent = forms.BooleanField(label='Toggle Vent:')
