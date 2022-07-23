# temp_mqtt
aquarium temp monitoring using a raspberry pi zero w

- DS18B20 1-wire thermometer (including wiring and resistor)
- Blinkt! 8 RGB LED Hat by Pimoroni
- Raspberry Pi Zero W
- MQTT server to collect temperature readings (linked to influxdb)

The aquarium temperature is read once every 15min, the results are published to an MQTT server which passes the data onto influxdb for recording. 

The latest temperature is added to a rotating list of data points for the last 24hrs. On each update the points over the last 24hrs are averaged in 8 groups (one for each LED) and then the colour of the average temperature is determined and sent to the 8 LED display. 

With the current settings of temperature to colour conversion, temperatures in the 26 to 30 °C range are displayed in shades of green to red, making it easy to check the progress of sudden temperature changes within the last 24hrs.


The script is set up as a service to enable automatic running/recovery of the script in case of power outages. Note that the script does not use any local saving of the data points, if the data isn't successfully sent to the MQTT server (or on to the influxdb) then the data is lost.


Helpful References:

Wiring of thermometer: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware

Blinkt!: https://github.com/pimoroni/blinkt
