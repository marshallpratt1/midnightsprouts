from django.shortcuts import render
from .models import User, SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel, LastFrostGreenhouse
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
from django.contrib import messages


def index(request):
    # handle all forms here
    # each form will call utils.py to handle database updates
    if request.method == 'POST':
        success_message = 'Changes successfully applied!'
        failure_message = 'Something went wrong, please try again...'
        if 'change_status' in request.POST:
            try:
                util.toggle_system_status()
                messages.add_message(request, messages.SUCCESS, success_message)
            except:
                messages.add_message(request, messages.ERROR, failure_message)
        if SystemStatus.objects.last().automatic:
            try:
                if 'air_temp_setpoint' in request.POST:
                    util.update_air_temp_setpoint(request.POST['air_temp_setpoint'])
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'humidity_setpoint' in request.POST:
                    util.update_humidity_setpoint(request.POST['humidity_setpoint'])
                    messages.add_message(request, messages.SUCCESS,success_message)
                if 'water_setpoint' in request.POST:
                    util.update_water_temp_setpoint(request.POST['water_setpoint'])
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'water_setpoint' in request.POST:
                    util.update_water_temp_setpoint(request.POST['water_setpoint'])
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'garden_start_hour' in request.POST:
                    util.set_garden_valve_times(request.POST['garden_start_hour'],request.POST['start_minute'], request.POST['duration'])
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'tree_start_hour' in request.POST:
                    util.set_greenhouse_tree_valve_times(request.POST['tree_start_hour'],request.POST['start_minute'], request.POST['duration'])       
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'pump_start_hour' in request.POST:
                    util.set_pump_times(request.POST['pump_start_hour'],request.POST['start_minute'], request.POST['duration'])
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'planter_start_hour' in request.POST:
                    util.set_greenhouse_planter_valve_times(request.POST['planter_start_hour'],request.POST['start_minute'], request.POST['duration'])               
                    messages.add_message(request, messages.SUCCESS, success_message)
            except:
                messages.add_message(request, messages.ERROR, failure_message)
            return HttpResponseRedirect(reverse('index'))
        elif not SystemStatus.objects.last().automatic:
            try:
                if 'toggle_nursery_heater' in request.POST:
                    util.toggle_nursery_heater()
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'toggle_water_heater' in request.POST:
                    util.toggle_water_heater()
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'toggle_pump' in request.POST:
                    util.toggle_pump()
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'toggle_garden_valve' in request.POST:
                    util.toggle_garden_valve()
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'garden_start_hour' in request.POST:
                    util.set_garden_valve_times(request.POST['garden_start_hour'],request.POST['start_minute'], request.POST['duration'])
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'tree_start_hour' in request.POST:
                    util.set_greenhouse_tree_valve_times(request.POST['tree_start_hour'],request.POST['start_minute'], request.POST['duration'])       
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'pump_start_hour' in request.POST:
                    util.set_pump_times(request.POST['pump_start_hour'],request.POST['start_minute'], request.POST['duration'])
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'planter_start_hour' in request.POST:
                    util.set_greenhouse_planter_valve_times(request.POST['planter_start_hour'],request.POST['start_minute'], request.POST['duration'])       
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'toggle_greenhouse_planter_valve' in request.POST:
                    util.toggle_greenhouse_planter_valve()
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'toggle_greenhouse_tree_valve' in request.POST:
                    util.toggle_greenhouse_tree_valve()
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'toggle_fan' in request.POST:
                    util.toggle_fan()
                    messages.add_message(request, messages.SUCCESS, success_message)
                if 'toggle_vent' in request.POST:
                    util.toggle_vent()
                    messages.add_message(request, messages.SUCCESS, success_message)
            except:
                messages.add_message(request, messages.ERROR, failure_message)
            return HttpResponseRedirect(reverse('index'))
        #the user submitted a form while after system had switched status
        else:            
            messages.add_message(request, messages.ERROR, failure_message)
            return HttpResponseRedirect(reverse('index'))

    # automatic vs manual controls
    automatic = SystemStatus.objects.order_by('-id')[0].automatic
    system_message = 'Are you sure you want to switch the sytem to Manual?' if automatic else 'Are you sure you want to switch the sytem to Automatic?'
    last_frost_greenhouse, created = LastFrostGreenhouse.objects.get_or_create(id=0)
    # the context fetches all of the most recent database entries for website render
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
        'greenhouse_air_temp_object': OutsideAirTemp.objects.last(),
        'last_frost_greenhouse' : last_frost_greenhouse.created_at,
        'water_temp_object': WaterTemp.objects.last(),
        'nursery_air_temp_object': NurseryAirTemp.objects.last(),
        'humidity_object': Humidity.objects.last(),
        'water_level': WaterLevel.objects.last().water_level,
        'fan_status': FanStatus.objects.last().fan_on,
        'pump_status': PumpStatus.objects.last().pump_on,
        'pump_times' : PumpStatus.objects.last(),
        'vent_status': VentStatus.objects.last().vent_on,
        'air_heater_status': AirHeaterStatus.objects.last().air_heater_on,
        'water_heater_status': WaterHeaterStatus.objects.last().water_heater_on,
        'garden_valve_status': GardenValveStatus.objects.last().garden_valve_open,
        'garden_valve_start_hour' : GardenValveStatus.objects.last().start_hour,
        'greenhouse_planter_valve_status': GreenhousePlanterValveStatus.objects.last().greenhouse_planter_valve_open,
        'greenhouse_tree_valve_status': GreenhouseTreeValveStatus.objects.last().greenhouse_tree_valve_open,
        'greenhouse_tree_valve_start_hour' : GreenhouseTreeValveStatus.objects.last().start_hour,
        'greenhouse_planter_valve_start_hour' : GreenhousePlanterValveStatus.objects.last().start_hour,
        'garden_valve_start_hour' : GardenValveStatus.objects.last().start_hour,
        'pump_start_hour' : PumpStatus.objects.last().start_hour,
        'air_temp_setpoint': AirTempSetpoint.objects.last().air_temp_setpoint,
        'water_temp_setpoint': WaterTempSetpoint.objects.last().water_temp_setpoint,
        'humidity_setpoint': HumiditySetpoint.objects.last().humidity_setpoint,
        'historical_nursery_temps': util.get_historical_nursery_temps(),
        'historical_outside_temps': util.get_historical_greenhouse_temps(),
        'nursery_temp_time_labels': util.get_nursery_date_time_labels(),
        'greenhouse_temp_time_labels' : util.get_greenhouse_date_time_labels(),
        'humidity_time_labels' : util.get_humidity_date_time_labels(),
        'water_temp_time_labels' : util.get_water_date_time_labels(),
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


##########################################################################
# api functions below here
# these api functions are for use locally to improve the UI 
# and allow the user to watch the sensor data in near real time
##########################################################################
from django.http import JsonResponse
from datetime import timedelta

#offset for alaska daylight savings time. This is the only timezone this 
#program will be used in
AKDT_OFFSET = -8

def api_get_nursery_temp(request):          
    last_nursery_temp = NurseryAirTemp.objects.last()
    last_nursery_temp_time = str(last_nursery_temp.created_at + timedelta(hours=AKDT_OFFSET))[6:16]
    return JsonResponse ({
        'nursery_temp' : last_nursery_temp.nursery_air_temp,
        'nursery_temp_timestamp' : last_nursery_temp_time,
        'nursery_temp_id' : last_nursery_temp.id,
    })

def api_get_greenhouse_temp(request): 
    last_greenhouse_temp = OutsideAirTemp.objects.last()
    last_greenhouse_temp_time = str(last_greenhouse_temp.created_at + timedelta(hours=AKDT_OFFSET))[6:16]
    return JsonResponse ({
        'greenhouse_temp' : last_greenhouse_temp.outside_air_temp,
        'greenhouse_temp_timestamp' : last_greenhouse_temp_time,
        'greenhouse_temp_id' : last_greenhouse_temp.id,
    })

def api_get_nursery_humidity(request): 
    last_nursery_humidity = Humidity.objects.last()         
    last_nursery_humidity_time =  str(last_nursery_humidity.created_at + timedelta(hours=AKDT_OFFSET))[6:16]
    return JsonResponse ({
        'nursery_humidity' : last_nursery_humidity.humidity,
        'nursery_humidity_timestamp' : last_nursery_humidity_time,
        'nursery_humidity_id' : last_nursery_humidity.id,
    })

def api_get_water_temp(request):       
    last_water_temp = WaterTemp.objects.last()         
    last_water_temp_time =  str(last_water_temp.created_at + timedelta(hours=AKDT_OFFSET))[6:16]
    return JsonResponse ({
        'water_temp' : last_water_temp.water_temp,
        'water_temp_timestamp' : last_water_temp_time,
        'water_temp_id' : last_water_temp.id,
    })

#return current equipment status for website
def api_get_equipment_status(request):
    nursery_heater_status = 'ON' if AirHeaterStatus.objects.last().air_heater_on else 'OFF'
    water_heater_status = 'ON' if WaterHeaterStatus.objects.last().water_heater_on else 'OFF'
    water_pump_status = 'ON' if PumpStatus.objects.last().pump_on else 'OFF'
    fan_status = 'ON' if FanStatus.objects.last().fan_on else 'OFF'
    vent_status = 'ON' if VentStatus.objects.last().vent_on else 'OFF'
    garden_valve_status = 'OPEN' if GardenValveStatus.objects.last().garden_valve_open else 'CLOSED'
    greenhouse_planter_valve_status = 'OPEN' if GreenhousePlanterValveStatus.objects.last().greenhouse_planter_valve_open else 'CLOSED'
    greenhouse_tree_valve_status = 'OPEN' if GreenhouseTreeValveStatus.objects.last().greenhouse_tree_valve_open else 'CLOSED'
    return JsonResponse({
        'nursery_heater_status': nursery_heater_status,
        'water_heater_status' : water_heater_status,
        'water_pump_status' : water_pump_status,
        'fan_status' : fan_status,
        'vent_status' : vent_status,
        'garden_valve_status' : garden_valve_status,
        'greenhouse_planter_valve_status' : greenhouse_planter_valve_status,
        'greenhouse_tree_valve_status' : greenhouse_tree_valve_status,
    })

def api_get_system_status(request):
    system_status = 'Automatic' if SystemStatus.objects.last().automatic else 'Manual'
    return JsonResponse({
        'system_status' : system_status,
    })   
