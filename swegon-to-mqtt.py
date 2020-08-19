#!/usr/bin/python3

import os
import sys
import datetime
import paho.mqtt.client as mqtt
import random
import queue
import json
import hassautoconf as autoconf

from time import sleep
import swegon


#--------------------------------------------------
# Global settings
#--------------------------------------------------

LOGFILE = "/var/log/swegon-to-mqtt/swegon-to-mqtt.log"
verbose = True

CLIENT_NAME = "swegon-modus-daemon"
SENSOR_FREQ = 15
BROKER = "#MQTT IP HERE"
CERT = "#MQTT CERTIFICATE HERE"

BASE_TOPIC_SETTINGS = "swegon/settings"
BASE_TOPIC_SENSORS = "swegon/sensors"
BASE_TOPIC_STATUS = "swegon/status"
BASE_TOPIC_ALARMS = "swegon/alarms"

TOPIC_FANSET            = "swegon/fan/set"
TOPIC_FIREPLACE         = "swegon/fan/trigger_fireplace"
TOPIC_TEMPSET           = "swegon/temp/set"
TOPIC_RESET_ALARMS      = "swegon/alarms/reset"
TOPIC_VACATION_MODE_SET = "swegon/vacation/set"

TOPIC_SETTINGS = "swegon/settings/sensor"
TOPIC_SENSORS = "swegon/sensors/sensor"
TOPIC_STATUS = "swegon/status/sensor"
TOPIC_ALARMS = "swegon/alarms/sensor"

TOPIC_VACATION_MODE_STATUS = "swegon/sensors/vacation_mode_status"
VACATION_MODES = {"ON": True,
                  "OFF": False}
vacation_mode = [False]
targettemp_stored_value = [20.0]
normal_target_temp = [20.0]
vacation_targettemp = [8.0]

EXPIRE_AFTER = 4800 # Seconds since last seen is considered offline

#--------------------------------------------------
# Misc debug / parser
#--------------------------------------------------
def debug(text):
    logfile = open(LOGFILE, "a")
    line = str(datetime.datetime.now()) + " " + text
    if (verbose):
        print(line)
    logfile.write(line + "\n")
    logfile.close()


#--------------------------------------------------
# MQTT Control and Functions
#--------------------------------------------------
def subscribe_topics():
    # Must check that subscribtion is successful
    client.subscribe(TOPIC_FANSET)
    client.subscribe(TOPIC_FIREPLACE)
    client.subscribe(TOPIC_TEMPSET)
    client.subscribe(TOPIC_RESET_ALARMS)
    client.subscribe(TOPIC_VACATION_MODE_SET)

# All init of MQTT connection."
def mqtt_init():
    def on_connect(client, userdata, flags, rc):
        if rc==0:
            debug("Connected to " + BROKER)
            subscribe_topics()
            client.connected_flag=True #set flag
        else:
            debug("Bad connection Returned code=" + str(rc))

    def on_disconnect(client, userdata, rc):
        debug("Disconnected from " + BROKER + ". Return code: " + str(rc))
        client.connected_flag=False

    def on_subscribe(client, userdata, mid, granted_qos):
        debug("Subscribed to topic, mid: " + str(mid))

    def on_message(client, userdata, message):
        debug("Received message on " + message.topic)
        topic = message.topic
        payload = message.payload.decode('utf-8')
        q.put([topic, payload])

    global client # Estabslish global client
    global q
    q = queue.Queue()
    client = mqtt.Client(CLIENT_NAME)
    client.on_connect=on_connect  #bind call back function
    client.on_message=on_message
    client.on_disconnect=on_disconnect
    client.on_subscribe=on_subscribe
    mqtt.Client.connected_flag=False #create flags in class
    cert_with_path = os.path.dirname(sys.argv[0]) + "/" + CERT
    client.tls_set(ca_certs=cert_with_path,tls_version=2)
    client.tls_insecure_set(True)
    client.loop_start()
    debug("Connecting to broker " + BROKER)

    #Establish connection, and retry until success
    try:
        client.connect(BROKER)      #connect to broker
    except:
        attempts = 1
        while not client.connected_flag:
            try:
                client.connect(BROKER)      #connect to broker
            except:
                debug("Connection attempt " + str(attempts) + " failed, retrying")
                attempts = attempts + 1
                sleep(5)
    while not client.connected_flag: #Make sure we are connected.
        sleep(1)



#--------------------------------------------------
# Main loop controls
#--------------------------------------------------
def process_message(message, swegoncasa):
    topic = message[0]
    payload = message[1]
    if   ( topic == TOPIC_FANSET ):
        swegoncasa.set_fan_mode(payload)
    elif ( topic == TOPIC_FIREPLACE ):
        swegoncasa.trigger_fireplace()
    elif ( topic == TOPIC_TEMPSET ):
        swegoncasa.set_temperature(payload)
    elif ( topic == TOPIC_RESET_ALARMS ):
        swegoncasa.reset_alarms()
    elif ( topic == TOPIC_VACATION_MODE_SET ):
        set_vacation_mode(payload, swegoncasa)


def set_vacation_mode(payload, swegoncasa):
    vacation_mode[0] = VACATION_MODES[payload]
    if vacation_mode[0]: # Entering vacation mode, store temperature
        debug("Entering vacation mode.")
        debug("Storing normal temperature " + str(targettemp_stored_value[0]))
        debug("Restoring vacation temperature " + str(vacation_targettemp[0]))
        normal_target_temp[0] = targettemp_stored_value[0]
        swegoncasa.set_temperature(vacation_targettemp[0])
    else:
        debug("Entering normal mode.")
        debug("Storing vacation temperature " + str(targettemp_stored_value[0]))
        debug("Restoring normal temperature " + str(normal_target_temp[0]))
        vacation_targettemp[0] = targettemp_stored_value[0]
        swegoncasa.set_temperature(normal_target_temp[0])

    value = "OFF"
    if vacation_mode[0]:
        value = "ON"
    client.publish(TOPIC_VACATION_MODE_STATUS, value, retain=True)


def update_sensors(swegoncasa):
    [settings, status, sensors, alarms] = swegoncasa.get_swegon_data()

    client.publish(TOPIC_SETTINGS, json.dumps(settings, sort_keys=True), retain=True)
    client.publish(TOPIC_STATUS  , json.dumps(status  , sort_keys=True), retain=True)
    client.publish(TOPIC_SENSORS , json.dumps(sensors), retain=True)
    client.publish(TOPIC_ALARMS  , json.dumps(alarms  , sort_keys=True), retain=True)
    targettemp_stored_value[0] = settings["Temperature setpoint"]


def register_sensors():
    # Write mode "On" to avoid seeing "Off"
    
    autoconf.register_sensor(client, BASE_TOPIC_ALARMS,   "Alarms",                  "alarm",                                            expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_SENSORS,  "Supply fan",              "fan",                                              expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_SENSORS,  "Exhaust fan",             "fan",                                              expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_SENSORS,  "Supply air temperature",  "temperature", "Supply Air after afterheater (T4)", expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_SENSORS,  "Exhaust air temperature", "temperature", "Exhaust Air Temperature (T5)",      expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_SENSORS,  "Outside air temperature", "temperature", "Outside Temperature (T1)",          expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_SENSORS,  "HX efficiency",           "efficiency",                                       expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_STATUS,   "Afterheater power",       "heat",                                             expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_STATUS,   "Operating mode",          "mode",                                             expire_after=EXPIRE_AFTER)
    autoconf.register_sensor(client, BASE_TOPIC_SETTINGS, "Fan mode",                "fan_mode",                                         expire_after=EXPIRE_AFTER)


def register_climate():
    # Done directly to avoid throwing a ton of parameters
    debug("Registering climate unit")

    config_topic = "homeassistant/climate/swegon/config"

    config = {}
    config["name"]                         = "Swegon Ventilation"
    config["current_temperature_topic"]    = TOPIC_SENSORS
    config["current_temperature_template"] = '{{ value_json["Supply Air after afterheater (T4)"]}}'
    config["temperature_command_topic"]    = TOPIC_TEMPSET
    config["temperature_state_topic"]      = TOPIC_SETTINGS
    config["temperature_state_template"]   = '{{ value_json["Temperature setpoint"]}}'
    config["mode_state_topic"]             = "swegon/system/mode"
    config["modes"]                        = "auto"
    config["fan_modes"]                    = ["Compensate", "Away", "Home","Boost"]
    config["fan_mode_state_topic"]         = TOPIC_SETTINGS
    config["fan_mode_state_template"]      = '{{ value_json["Fan mode"]}}'
    config["fan_mode_command_topic"]       = TOPIC_FANSET
    config["away_mode_command_topic"]      = TOPIC_VACATION_MODE_SET
    config["away_mode_state_topic"]        = TOPIC_VACATION_MODE_STATUS
    config["min_temp"]                     = 5
    config["max_temp"]                     = 20
    config["temp_step"]                    = 1

    client.publish(config_topic, json.dumps(config, ensure_ascii=False).encode("utf-8"), retain=True)
    client.publish("swegon/system/mode","auto", retain=True)


#--------------------------------------------------
# Main loop
#--------------------------------------------------
def main():
    sleep(5)
    mqtt_init()

    swegoncasa = swegon.Swegon(debug)

    register_sensors()
    register_climate()

    # mainloop
    sensor_counter = 0

    while True:
        # First, make sure we are connected
        while not client.connected_flag: #wait in loop
            sleep(1)

        # Process any waiting messages
        while not q.empty():
            message = q.get()
            process_message(message, swegoncasa)
            sleep(1)
            update_sensors(swegoncasa) # Update all sensors
            sensor_counter = 4 # Trigger second update soon after

        sensor_counter -= 1
        if sensor_counter <= 0:
            update_sensors(swegoncasa) # Update all sensors
            sensor_counter = SENSOR_FREQ
        sleep(1) # Wait

    # Should never end here, but if so, close nicely
    client.loop_stop()    #Stop loop
    client.disconnect() # disconnect



if __name__ == "__main__":
    main()
