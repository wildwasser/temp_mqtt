import paho.mqtt.client as mqtt
import glob
import time
import json
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

c1 = 50
c2 = 0
delay = 1800
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

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

#draw.rectangle((x, top, x + shape_width, bottom), outline=255, fill=0)


# Load default font.
font = ImageFont.load_default()
#font = ImageFont.truetype('/home/pi/VCR_OSD_MONO_1.001.ttf', 16)

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php

#####################   GRAPH STUFF  ##########################################################

set_temp = 26.0
history_length = 48
history_ratio = width/history_length
graph_max = 12
graph_min = height
graph_range = graph_min - graph_max
temp_min = set_temp - 1.0
temp_max = set_temp + 3.0
temp_range = temp_max - temp_min
scaler_ratio = graph_range / temp_range
historylist = []
graphlist = []

# Function to scale the temperature value to fit within the dimensions of the graph
def scaler(temp):
    temp0 = temp - temp_min
    temp1 = int(temp0*scaler_ratio)
    temp2 = graph_min - temp1
    return temp2

# Set up the initial history list using the set temperature as fake data points
for i in range(0, history_length):
    historylist.append(set_temp)

# Set up the first graph data list using the set temperature as fake data points
for n in range (0,history_length):
    romper = ((int(n*history_ratio),scaler(historylist[n-1]),int((n+1)*history_ratio)-1, height))
    graphlist.append(romper)

# Function to remove the oldest, and append the newest value to the list of historical data
def rotate(input):
    del historylist[0]
    historylist.append(input)
    rotatelist = []
    for n in range(0,history_length):
        romper = ((int(n*history_ratio), scaler(historylist[n]), int((n+1)*history_ratio)-1, height))
        rotatelist.append(romper)
    return rotatelist




##################  infinite loop #############################################
while True:
        # Read the temperature and rotate the history graphlist
    temperature = read_temp()
    graphlist = rotate(temperature)
        # Start the countdown and display the data/graph again but with inverted colours
    for count in range(0, delay):
        # Clear the image
        draw.rectangle((0, 0, width, height), outline=c1, fill=c1)
        # Draw the text
        draw.text((x+1, top + 6), "Temp: " + str(temperature), font=font, fill=c2)
        # Iterate through the graph points
        for r in graphlist:
            draw.rectangle(r, outline=c2, fill=c2)
        # Set up the active blinker animation
        if (count % 2) == 0:
            draw.rectangle((int(width*count/delay)-1, 0, width, 1), outline=c2, fill=c2)
        else:
            draw.rectangle((int(width*count/delay)-1, 0, width, 1), outline=c2, fill=c2)
            draw.rectangle((int(width*count/delay)-1, 0, int(width*count/delay)+2, 1), outline=c1 fill=c1)

        # Display image.
        disp.image(image)
        disp.show()
        time.sleep(1)

############################  Do it all again, but with inverted colours!  ####################################
    # Read the temperature and rotate the history graphlist
    temperature = read_temp()
    graphlist = rotate(temperature)
        # Start the countdown and display the data/graph
    for count in range(0, delay):
        # Clear the image
        draw.rectangle((0, 0, width, height), outline=c2, fill=c2)
        # Draw the text
        draw.text((x+1, top + 6), "Temp: " + str(temperature), font=font, fill=c1)
        # Iterate through the graph points
        for r in graphlist:
            draw.rectangle(r, outline=c1, fill=c1)
        # Set up the active blinker animation
        if (count % 2) == 0:
            draw.rectangle((int(width*count/delay)-1, 0, width, 1), outline=c1, fill=c1)
        else:
            draw.rectangle((int(width*count/delay)-1, 0, width, 1), outline=c1, fill=c1)
            draw.rectangle((int(width*count/delay)-1, 0, int(width*count/delay)+2, 1), outline=c2, fill=c2)

        # Display image.
        disp.image(image)
        disp.show()
        time.sleep(1)
