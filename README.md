# swegon-to-mqtt
Daemon for Swegon Casa over Modbus for use with Home Assistant

This daemon is made to run using systemd on a debian based system (for instance raspberry pi W zero) with a USB to modbus dongle (for instance this .

# Hardware
Tested on the following hardware:
- Raspberry PI Zero W
- FTDI USB to modubs / RS485 dongle (https://www.ftdichip.com/Products/Cables/USBRS485.htm))
- Swegon Casa R120 with a modbus adapter

# Disclaimer
A lot of this code is quick and dirty, so any improvements are welcome!

I have an issue with my Swegon Casa system where it keeps resetting about 20 times throughout the day. The clear indication of this is if the clock has been reset on the unit. I have been in contact with Swegon support without them being willing to resolve it. Therefore, the code contains a number of workarounds and filters to avoid the resets propagating into Home Assistant.

# Setup
1. Clone the repo into /opt/swegon-to-mqtt
2. Modify the MQTT setup portion of swegon-to-mqtt to match your mqtt server (and the one used by home assistant).
3. Run setup.sh:
``` 
cd /opt/swegon-to-mqtt
./setup.sh
```

Enjoy!
