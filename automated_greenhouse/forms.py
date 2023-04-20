from django import forms
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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
    air_temp_setpoint = forms.IntegerField(initial=80, min_value=60, max_value=90, label="Air Temp Setpoint")

class HumidityForm(forms.Form):
    humidity_setpoint = forms.IntegerField(initial=80, min_value=60, max_value=90, label="Humidity Setpoint")

class WaterForm(forms.Form):
    water_setpoint = forms.IntegerField(initial=80, min_value=60, max_value=90, label="Water Temp Setpoint")

class SystemStatusForm(forms.Form):
    change_status = forms.BooleanField(label='Change System Control:')

class NurseryHeaterForm(forms.Form):
    toggle_nursery_heater = forms.BooleanField(label='Toggle Nursery Heater:')

class WaterHeaterForm(forms.Form):
    toggle_water_heater = forms.BooleanField(label='Toggle Water Heater:')

class PumpForm(forms.Form):
    toggle_pump = forms.BooleanField(label='Toggle Pump:')

class DrainValveForm(forms.Form):
    toggle_drain_valve = forms.BooleanField(label='Toggle Drain Valve:')

class FanForm(forms.Form):
    toggle_fan = forms.BooleanField(label='Toggle Fan:')

class VentForm(forms.Form):
    toggle_vent = forms.BooleanField(label='Toggle Vent:')
