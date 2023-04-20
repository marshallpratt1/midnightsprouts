import os
import glob
import time
import Adafruit_DHT
from django.utils import timezone
from automated_greenhouse.models import SystemStatus, OutsideAirTemp, WaterTemp, NurseryAirTemp, Humidity, WaterLevel
from automated_greenhouse.models import PumpStatus, FanStatus, VentStatus, AirHeaterStatus, WaterHeaterStatus, Valve1Status
DHT_DATA_PIN = 27

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
                data_to_send = NurseryAirTemp(nursery_air_temp = current_temp, created_at=timezone.now())
                data_to_send.save()
                
def read_humidity():
    current_humidity, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_DATA_PIN)
    data_to_send = Humidity(humidity = current_humidity, created_at=timezone.now())
    data_to_send.save()



while True:
    read_temp()
    read_humidity()
    
    time.sleep(5)
