import os
import glob
import time
from datetime import datetime
import Adafruit_DHT
import RPi.GPIO as GPIO
from django.utils import timezone
from automated_greenhouse.models import SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel, SystemError
from automated_greenhouse.models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, GardenValveStatus, GreenhousePlanterValveStatus, GreenhouseTreeValveStatus
from automated_greenhouse.models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint, LastFrostGreenhouse
from automated_greenhouse.util import *

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#initilize all GPIO pins
DHT_DATA_PIN = 22
AIR_HEATER = 0
WATER_HEATER = 5
PUMP_TOGGLE = 6
FAN_TOGGLE = 13
VENT_TOGGLE = 19
VALVE_TOGGLE_1 = 16
VALVE_TOGGLE_2 = 20
VALVE_TOGGLE_3 = 21
#set GPIO to output
GPIO.setup(AIR_HEATER,GPIO.OUT)
GPIO.setup(WATER_HEATER,GPIO.OUT)
GPIO.setup(PUMP_TOGGLE,GPIO.OUT)
GPIO.setup(FAN_TOGGLE,GPIO.OUT)
GPIO.setup(VENT_TOGGLE,GPIO.OUT)
GPIO.setup(VALVE_TOGGLE_1,GPIO.OUT)
GPIO.setup(VALVE_TOGGLE_2,GPIO.OUT)
GPIO.setup(VALVE_TOGGLE_3,GPIO.OUT)
temp_buffer = 2 #temp buffer for air and water temp
humidity_buffer = 5 #humidity buffer
HIGH_TEMP_THRESHOLD = 80 #vent if temp gets above 80
STOP_HIGH_TEMP_THRESHOLD = 77 #stop venting at 77
HIGH_TEMP_TOGGLE = False
PROBE_MESSAGES = {
    0: "There was an error with the Greenhouse Air Temperature Probe",
    1: "There was an error with the Water Temperature Probe",
}
NURSERY_TEMP_ERROR_MESSAGE = "There was an error with the Nursery Temperature and Humidity Sensor"

sensor_paths = ['/sys/bus/w1/devices/28-0306979407ca/w1_slave', '/sys/bus/w1/devices/28-030d979455e5/w1_slave']


#reads temp data from ds18b20 and saves it to database
#this reads temperatures for water and greenhouse
def read_temp():
    id = 0
    try:
        for sensor_id, sensor_path in enumerate(sensor_paths):
            with open(sensor_path, 'r') as file:
                lines = file.readlines()
            if (lines != None and len(lines[0]) > 3 and lines[0].strip()[-3:] != 'YES'):
                return None
            position = lines[1].find('t=')
            temp = float(lines[1][position+2:]) / 1000.0
            temp_f = temp * 1.8 + 32
            current_temp = "%.1f" % temp_f
            if current_temp is not None:
                if sensor_id == 0:
                    data_to_send = OutsideAirTemp(outside_air_temp = current_temp, created_at=timezone.now())
                    data_to_send.save()
                    if current_temp <= 32: 
                        new_frost_time = LastFrostGreenhouse.objects.get_or_create(id = 0)
                        new_frost_time.save()
                elif sensor_id == 1:
                    data_to_send = WaterTemp(water_temp = current_temp, created_at=timezone.now())
                    data_to_send.save()
            id += 1
    except:
        new_error = SystemError(error_message=PROBE_MESSAGES)
        new_error.save()
#reads humidity and temp data from DHT11 and saves it to database
#this reads temperature and humiditity for inside the nursery
def read_humidity():
<<<<<<< HEAD
=======
    try:
        current_humidity, current_temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_DATA_PIN)
        if(current_temp != None):
            current_temp_f = current_temp * 1.8 + 32    
        current_temp_f = "%.1f" % current_temp_f
        # dscard bad sensor data
        if(current_humidity < 100):
            temp_data_to_send = NurseryAirTemp(nursery_air_temp = current_temp_f, created_at=timezone.now())
            humidity_data_to_send = Humidity(humidity = current_humidity, created_at=timezone.now())
            temp_data_to_send.save()
            humidity_data_to_send.save()
    except:
        new_error = SystemError(error_message=NURSERY_TEMP_ERROR_MESSAGE)
        new_error.save()
>>>>>>> dba9a67221103fc817a84295cb2ea3131d1ba0ac
#function for handling all automatic mode logic
def automatic_mode():
    #initilize objects status and setpoints by checking last database entry
    air_temp_setpoint = AirTempSetpoint.objects.last().air_temp_setpoint
    air_temp = NurseryAirTemp.objects.last().nursery_air_temp
    air_heater_status = AirHeaterStatus.objects.last().air_heater_on
    water_temp_setpoint = WaterTempSetpoint.objects.last().water_temp_setpoint
    water_temp = WaterTemp.objects.last().water_temp
    water_heater_status = WaterHeaterStatus.objects.order_by('id').last().water_heater_on
    fan_status = FanStatus.objects.order_by('id').last().fan_on
    humidity_setpoint = HumiditySetpoint.objects.order_by('id').last().humidity_setpoint
    humidity = Humidity.objects.order_by('id').last().humidity
    vent_status = VentStatus.objects.order_by('id').last().vent_on
    pump = PumpStatus.objects.order_by('id').last()
    garden_valve = GardenValveStatus.objects.order_by('id').last()
    greenhouse_planter_valve = GreenhousePlanterValveStatus.objects.order_by('id').last()
    greenhouse_tree_valve = GreenhouseTreeValveStatus.objects.order_by('id').last()

    #THESE RUN OFF SETPOINTS
    #automatic air heater toggle
    if(air_temp_setpoint > air_temp):
        GPIO.output(AIR_HEATER, GPIO.HIGH)
        if(air_heater_status == False):
            toggle_nursery_heater()
    elif(air_temp_setpoint + temp_buffer < air_temp):
        GPIO.output(AIR_HEATER, GPIO.LOW)
        if(air_heater_status == True):
            toggle_nursery_heater()

    #automatic water heater toggle, don't turn on pump if water is freezing
    if(water_temp_setpoint > water_temp):
        GPIO.output(WATER_HEATER, GPIO.HIGH)
        if(water_heater_status == False):
            toggle_water_heater()
    elif(water_temp_setpoint + temp_buffer < water_temp):
        GPIO.output(WATER_HEATER, GPIO.LOW)
        if(water_heater_status == True):
            toggle_water_heater()

    #automatic fan toggle
    if(fan_status == False):
        GPIO.output(FAN_TOGGLE, GPIO.HIGH)
        toggle_fan()
    else:
        GPIO.output(FAN_TOGGLE, GPIO.HIGH)

    #automatic vent toggle
    if(humidity_setpoint < humidity):
        GPIO.output(VENT_TOGGLE, GPIO.HIGH)
        if(vent_status == False):
            toggle_vent()
    elif((humidity_setpoint - humidity_buffer > humidity) and air_temp < STOP_HIGH_TEMP_THRESHOLD):        
        GPIO.output(VENT_TOGGLE, GPIO.LOW)
        if(vent_status == True):
            toggle_vent()
    #toggle vent if it gets too hot    
    if(air_temp > HIGH_TEMP_THRESHOLD):
        GPIO.output(VENT_TOGGLE, GPIO.HIGH)
        if(vent_status == False):
            toggle_vent()
    elif((air_temp <= air_temp_setpoint) and (humidity_setpoint - humidity_buffer > humidity)):
        GPIO.output(VENT_TOGGLE, GPIO.LOW)
        if(vent_status == True):
            toggle_vent()

    #THESE RUN OFF TIMERS
    #automatic pump toggle
    if(NOW_TIME.hour == pump.start_hour and NOW_TIME.minute >= pump.start_minute and NOW_TIME.minute < pump.start_minute + pump.duration):
        #safety check, don't turn on pump if water is freezing
        if (water_temp > 32):
            GPIO.output(PUMP_TOGGLE, GPIO.HIGH)
            if(pump.pump_on == False):
                toggle_pump()
    else:
        GPIO.output(PUMP_TOGGLE, GPIO.LOW)
        if(pump.pump_on == True):
            toggle_pump()

    #automatic valve1
    if(NOW_TIME.hour == garden_valve.start_hour and NOW_TIME.minute >= garden_valve.start_minute and NOW_TIME.minute < garden_valve.start_minute + garden_valve.duration):
        GPIO.output(VALVE_TOGGLE_1, GPIO.HIGH)
        if(garden_valve.garden_valve_open == False):
            toggle_garden_valve()
    else:
        GPIO.output(VALVE_TOGGLE_1, GPIO.LOW)
        if(garden_valve.garden_valve_open == True):
            toggle_garden_valve()

    #automatic valve2
    if(NOW_TIME.hour == greenhouse_planter_valve.start_hour and NOW_TIME.minute >= greenhouse_planter_valve.start_minute and NOW_TIME.minute < greenhouse_planter_valve.start_minute + garden_valve.duration):
        GPIO.output(VALVE_TOGGLE_2, GPIO.HIGH)
        if(greenhouse_planter_valve.greenhouse_planter_valve_open == False):
            toggle_greenhouse_planter_valve()
    else:
        GPIO.output(VALVE_TOGGLE_2, GPIO.LOW)
        if(greenhouse_planter_valve.greenhouse_planter_valve_open == True):
            toggle_greenhouse_planter_valve()

    #automatic valve3
    if(NOW_TIME.hour == greenhouse_tree_valve.start_hour and NOW_TIME.minute >= greenhouse_tree_valve.start_minute and NOW_TIME.minute < greenhouse_tree_valve.start_minute + garden_valve.duration):
        GPIO.output(VALVE_TOGGLE_3, GPIO.HIGH)
        if(greenhouse_tree_valve.greenhouse_tree_valve_open == False):
            toggle_greenhouse_tree_valve()
    else:
        GPIO.output(VALVE_TOGGLE_3, GPIO.LOW)
        if(greenhouse_tree_valve.greenhouse_tree_valve_open == True):
            toggle_greenhouse_tree_valve()

#function for allowing user to toggle all output on or off manually
def manual_mode():
    #initilize objects status by checking last database entry
    air_heater_status = AirHeaterStatus.objects.order_by('id').last().air_heater_on
    water_heater_status = WaterHeaterStatus.objects.order_by('id').last().water_heater_on
    fan_status = FanStatus.objects.order_by('id').last().fan_on
    vent_status = VentStatus.objects.order_by('id').last().vent_on
    pump_status = PumpStatus.objects.order_by('id').last().pump_on
    garden_valve_status = GardenValveStatus.objects.order_by('id').last().garden_valve_open
    greenhouse_planter_valve_status = GreenhousePlanterValveStatus.objects.order_by('id').last().greenhouse_planter_valve_open
    greenhouse_tree_valve_status = GreenhouseTreeValveStatus.objects.order_by('id').last().greenhouse_tree_valve_open
    
    #Air temp Status   
    if(air_heater_status == True):
        GPIO.output(AIR_HEATER, GPIO.HIGH)
    else:
        GPIO.output(AIR_HEATER, GPIO.LOW)
    #Water Temp Status
    if(water_heater_status == True):
        GPIO.output(WATER_HEATER, GPIO.HIGH)
    else:
        GPIO.output(WATER_HEATER, GPIO.LOW)
    #Fan Status
    if(fan_status == True):
        GPIO.output(FAN_TOGGLE, GPIO.HIGH)
    else:
        GPIO.output(FAN_TOGGLE, GPIO.LOW)
    #Vent Status
    if(vent_status == True):
        GPIO.output(VENT_TOGGLE, GPIO.HIGH)
    else:
        GPIO.output(VENT_TOGGLE, GPIO.LOW)
    #Pump Status   
    if(pump_status == True):
        GPIO.output(PUMP_TOGGLE, GPIO.HIGH)
    else:
        GPIO.output(PUMP_TOGGLE, GPIO.LOW)
     #Valve1 Status   
    if(garden_valve_status == True):
        GPIO.output(VALVE_TOGGLE_1, GPIO.HIGH)
    else:
        GPIO.output(VALVE_TOGGLE_1, GPIO.LOW)
    #Valve2 Status     
    if(greenhouse_planter_valve_status == True):
        GPIO.output(VALVE_TOGGLE_2, GPIO.HIGH)
    else:
        GPIO.output(VALVE_TOGGLE_2, GPIO.LOW)
    #Valve3 Status     
    if(greenhouse_tree_valve_status == True):
        GPIO.output(VALVE_TOGGLE_3, GPIO.HIGH)
    else:
        GPIO.output(VALVE_TOGGLE_3, GPIO.LOW)
 
 #main
while True:
    NOW_TIME = datetime.now()
    read_temp()
    read_humidity()
    if(SystemStatus.objects.order_by('id').last().automatic == True):
        automatic_mode()
    else:
        manual_mode()
        
    
    time.sleep(5)
