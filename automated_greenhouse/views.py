from django.shortcuts import render
from .models import User, SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from .models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus
from .models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus
from django.db import IntegrityError
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, AirTempForm, HumidityForm, WaterForm, SystemStatusForm, GreenhouseTreeValveTimeForm
from .forms import NurseryHeaterForm, WaterHeaterForm, GardenValveForm, GreenhousePlanterValveForm, GreenhouseTreeValveForm, FanForm, VentForm, PumpForm
from .forms import GreenhousePlanterValveTimeForm, GardenValveTimeForm, GreenhouseTreeValveTimeForm, PumpTimeForm
from . import util
import json


def index(request):
    # handle all forms here
    # each form will call utils.py to handle database updates
    if request.method == 'POST':
        if 'air_temp_setpoint' in request.POST:
            util.update_air_temp_setpoint(request.POST['air_temp_setpoint'])
        if 'humidity_setpoint' in request.POST:
            util.update_humidity_setpoint(request.POST['humidity_setpoint'])
        if 'water_setpoint' in request.POST:
            util.update_water_temp_setpoint(request.POST['water_setpoint'])
        if 'water_setpoint' in request.POST:
            util.update_water_temp_setpoint(request.POST['water_setpoint'])
        if 'change_status' in request.POST:
            util.toggle_system_status()
        if 'toggle_nursery_heater' in request.POST:
            util.toggle_nursery_heater()
        if 'toggle_water_heater' in request.POST:
            util.toggle_water_heater()
        if 'toggle_pump' in request.POST:
            util.toggle_pump()
        if 'toggle_garden_valve' in request.POST:
            util.toggle_garden_valve()
        if 'garden_start_hour' in request.POST:
            util.set_garden_valve_times(request.POST['garden_start_hour'],request.POST['start_minute'], request.POST['duration'])
        if 'tree_start_hour' in request.POST:
            util.set_greenhouse_tree_valve_times(request.POST['tree_start_hour'],request.POST['start_minute'], request.POST['duration'])       
        if 'pump_start_hour' in request.POST:
            util.set_pump_times(request.POST['pump_start_hour'],request.POST['start_minute'], request.POST['duration'])
        if 'planter_start_hour' in request.POST:
            util.set_greenhouse_planter_valve_times(request.POST['planter_start_hour'],request.POST['start_minute'], request.POST['duration'])       
        if 'toggle_greenhouse_planter_valve' in request.POST:
            util.toggle_greenhouse_planter_valve()
        if 'toggle_greenhouse_tree_valve' in request.POST:
            util.toggle_greenhouse_tree_valve()
        if 'toggle_fan' in request.POST:
            util.toggle_fan()
        if 'toggle_vent' in request.POST:
            util.toggle_vent()

    # automatic vs manual controls
    automatic = SystemStatus.objects.order_by('-id')[0].automatic
    system_message = 'Are you sure you want to switch the sytem to Manual?' if automatic else 'Are you sure you want to switch the sytem to Automatic?'

    # the context fetches all of the most recent database entries for website render
    number_of_datapoints = 20
    return render(request, 'automated_greenhouse/index.html', {
        'air_form': AirTempForm,
        'humidity_form': HumidityForm,
        'water_form': WaterForm,
        'system_form': SystemStatusForm,
        'nursery_heater_form': NurseryHeaterForm,
        'water_heater_form': WaterHeaterForm,
        'water_pump_form': PumpForm,
        'garden_valve_form': GardenValveForm,
        'greenhouse_planter_valve_form': GreenhousePlanterValveForm,
        'greenhouse_tree_valve_form': GreenhouseTreeValveForm,
        'greenhouse_tree_valve_time_form': GreenhouseTreeValveTimeForm,
        'greenhouse_planter_valve_time_form' : GreenhousePlanterValveTimeForm,
        'garden_valve_time_form' : GardenValveTimeForm,
        'pump_time_form' : PumpTimeForm,
        'fan_form': FanForm,
        'vent_form': VentForm,
        'automatic': automatic,
        'system_message': system_message,
        'outside_air_temp': OutsideAirTemp.objects.order_by('-id').first().outside_air_temp,
        'water_temp': WaterTemp.objects.order_by('-id').first().water_temp,
        'nursery_air_temp': NurseryAirTemp.objects.order_by('-id').first().nursery_air_temp,
        'humidity': Humidity.objects.order_by('-id').first().humidity,
        'water_level': WaterLevel.objects.order_by('-id').first().water_level,
        'fan_status': FanStatus.objects.order_by('-id').first().fan_on,
        'pump_status': PumpStatus.objects.order_by('-id').first().pump_on,
        'vent_status': VentStatus.objects.order_by('-id').first().vent_on,
        'air_heater_status': AirHeaterStatus.objects.order_by('-id').first().air_heater_on,
        'water_heater_status': WaterHeaterStatus.objects.order_by('-id').first().water_heater_on,
        'garden_valve_status': GardenValveStatus.objects.order_by('-id').first().garden_valve_open,
        'garden_valve_start_hour' : GardenValveStatus.objects.order_by('-id').first().start_hour,
        'greenhouse_planter_valve_status': GreenhousePlanterValveStatus.objects.order_by('-id').first().greenhouse_planter_valve_open,
        'greenhouse_tree_valve_status': GreenhouseTreeValveStatus.objects.order_by('-id').first().greenhouse_tree_valve_open,
        'greenhouse_tree_valve_start_hour' : GreenhouseTreeValveStatus.objects.order_by('-id').first().start_hour,
        'greenhouse_planter_valve_start_hour' : GreenhousePlanterValveStatus.objects.order_by('-id').first().start_hour,
        'garden_valve_start_hour' : GardenValveStatus.objects.order_by('-id').first().start_hour,
        'pump_start_hour' : PumpStatus.objects.order_by('-id').first().start_hour,
        'air_temp_setpoint': AirTempSetpoint.objects.order_by('-id').first().air_temp_setpoint,
        'water_temp_setpoint': WaterTempSetpoint.objects.order_by('-id').first().water_temp_setpoint,
        'humidity_setpoint': HumiditySetpoint.objects.order_by('-id').first().humidity_setpoint,
        'historical_nursery_temps': util.get_historical_nursery_temps(),
        'historical_outside_temps': util.get_historical_greenhouse_temps(),
        'temps_labels': util.get_date_time_labels(),
        'historical_humidity': util.get_historical_humidity(),
        'historical_water_temps': util.get_historical_water_temps(),
    })

# register new user


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "automated_greenhouse/register.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "automated_greenhouse/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "automated_greenhouse/register.html", {"form": RegisterForm()})
