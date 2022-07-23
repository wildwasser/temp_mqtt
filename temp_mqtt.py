import paho.mqtt.client as mqtt
import glob
import time
import decimal
from statistics import mean
import json
import busio
import blinkt
import colorsys

delay = 900 #seconds
history_length = int(24/((delay/60)/60)) #900 sec converts to a 3 hr average per LED, over 24hrs
print("history_length: ", history_length)
#set up mqtt server connection:
MQTT_SERVER = '192.168.10.56'
MQTT_PORT = 1883
MQTT_TOPIC = 'aquarium'
# Set these to use authorisation
MQTT_USER = None
MQTT_PASS = None
client = mqtt.Client()
client.connect(MQTT_SERVER, MQTT_PORT, 60)


#set up directory for temp monitoring
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#define functions for temperature monitoring
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = round((float(temp_string) / 1000.0),1)
        temp_c += 1.0
        payload = {"temperature": temp_c}
        client.connect(MQTT_SERVER, MQTT_PORT, 30)
        client.publish("aquarium", json.dumps(payload))
        return temp_c

##############################  LED Stuff ##################################################################
blinkt.set_clear_on_exit(True)
sat = 0.9
val = 0.01
temp_set = 26.0
led_count = blinkt.NUM_PIXELS
num_colours = 150
temp_min = 20.0
temp_max = 37.0
temp_range = temp_max - temp_min
scaler_ratio = float(temp_range) / float(num_colours)

# Function to scale the temperature value to fit within the dimensions of the graph
def scaler(temp):
    temp0 = temp - temp_min
    if temp < 24.0:
        temp1 = 0.78
    elif temp > 29.5:
        temp1 = 0.0
    else:
        temp1 = (1.0 - (temp0*scaler_ratio))
    return round(temp1,2)

# Set up the initial history list using the set temperature as fake data points
list_history = []
for i in range(history_length):
    romper = 26.0
    list_history.append(scaler(romper))
#    print(i, romper)

# Set up the initial led list using the set temperature value as fake data points
list_leds = []
for i in range(led_count):
    romper = 26.0
    list_leds.append(scaler(romper))

# Function to remove the oldest, and append the newest value to the list of historical data
def rotate(input):
    del list_history[0]
    list_history.append(input)
    list_truncated = [list_history[(i*history_length)//led_count:((i+1)*history_length)//led_count] for i in range(led_count)]
    list0 = []
    for i in range(led_count):
        list0.append(mean(list_truncated[i]))
    return list0

#Function to go through the history list and display the scaled temps on the 8 LEDs
def show_leds():
    for x in range(led_count):
        v = led_count - x -1
        hue = list_leds[x]
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, val)]
        blinkt.set_pixel(v, r, g, b)
    blinkt.show()
################################################################




##################  infinite loop #############################################
##################  infinite loop #############################################
##################  infinite loop #############################################
while True:
    # Read the temperature and rotate the history graphlist
    temperature = read_temp()
    list_leds = rotate(scaler(temperature))
    show_leds()
    time.sleep(delay)
