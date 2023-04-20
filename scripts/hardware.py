import os
import glob
import time
import Adafruit_DHT
import RPi.GPIO as GPIO
from django.utils import timezone
from automated_greenhouse.models import SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from automated_greenhouse.models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, Valve1Status
from automated_greenhouse.models import AirTempSetpoint, WaterTempSetpoint, HumiditySetpoint

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
DHT_DATA_PIN = 22
AIR_HEATER = 0
WATER_HEATER = 5
PUMP_TOGGLE = 6
FAN_TOGGLE = 13
VENT_TOGGLE = 19
GPIO.setup(AIR_HEATER,GPIO.OUT)
GPIO.setup(WATER_HEATER,GPIO.OUT)
GPIO.setup(PUMP_TOGGLE,GPIO.OUT)
GPIO.setup(FAN_TOGGLE,GPIO.OUT)
GPIO.setup(VENT_TOGGLE,GPIO.OUT)

sensor_paths = ['/sys/bus/w1/devices/28-0306979407ca/w1_slave', '/sys/bus/w1/devices/28-030d979455e5/w1_slave']



def read_temp():
    for sensor_id, sensor_path in enumerate(sensor_paths):
        with open(sensor_path, 'r') as file:
            lines = file.readlines()
        if lines[0].strip()[-3:] != 'YES':
            return None
        position = lines[1].find('t=')
        temp = float(lines[1][position+2:]) / 1000.0
        temp_f = temp * 1.8 + 32
        current_temp = "%.1f" % temp_f
        if current_temp is not None:
            if sensor_id == 0:
                data_to_send = OutsideAirTemp(outside_air_temp = current_temp, created_at=timezone.now())
                data_to_send.save()
            elif sensor_id == 1:
                data_to_send = WaterTemp(water_temp = current_temp, created_at=timezone.now())
                data_to_send.save()
                
def read_humidity():
    current_humidity, current_temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_DATA_PIN)
    current_temp_f = current_temp *1.8 + 32
    current_temp_f = "%.1f" % current_temp_f
    temp_data_to_send = NurseryAirTemp(nursery_air_temp = current_temp_f, created_at=timezone.now())
    humidity_data_to_send = Humidity(humidity = current_humidity, created_at=timezone.now())
    temp_data_to_send.save()
    humidity_data_to_send.save()

def automatic_mode():
    #automatic air heater toggle
    if(AirTempSetpoint.objects.order_by('id').last().air_temp_setpoint > NurseryAirTemp.objects.order_by('id').last().nursery_air_temp):
        GPIO.output(AIR_HEATER, GPIO.HIGH)
        GPIO.output(FAN_TOGGLE, GPIO.HIGH)
    else:
        GPIO.output(AIR_HEATER, GPIO.LOW)
        GPIO.output(FAN_TOGGLE, GPIO.LOW)
    #automatic water heater toggle
    if(WaterTempSetpoint.objects.order_by('id').last().water_temp_setpoint > WaterTemp.objects.order_by('id').last().water_temp):
        GPIO.output(WATER_HEATER, GPIO.HIGH)
    else:
        GPIO.output(WATER_HEATER, GPIO.LOW)
    #automatic pump toggle
    if(WaterTempSetpoint.objects.order_by('id').last().water_temp_setpoint > WaterTemp.objects.order_by('id').last().water_temp):
        GPIO.output(PUMP_TOGGLE, GPIO.HIGH)
    else:
        GPIO.output(PUMP_TOGGLE, GPIO.LOW)
    #automatic fan toggle
    if(WaterTempSetpoint.objects.order_by('id').last().water_temp_setpoint > WaterTemp.objects.order_by('id').last().water_temp):
        GPIO.output(FAN_TOGGLE, GPIO.HIGH)
    else:
        GPIO.output(FAN_TOGGLE, GPIO.LOW)
    #automatic vent toggle
    if(WaterTempSetpoint.objects.order_by('id').last().water_temp_setpoint > WaterTemp.objects.order_by('id').last().water_temp):
        GPIO.output(VENT_TOGGLE, GPIO.HIGH)
    else:
        GPIO.output(VENT_TOGGLE, GPIO.LOW)


while True:
    read_temp()
    read_humidity()
    #if(SystemStatus.objects.order_by('-id')[0].automatic == true)
    automatic_mode()
        
    
    time.sleep(5)
