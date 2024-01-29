#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2

import paho.mqtt.client as mqtt
import time
from datetime import datetime, timedelta, timezone
import atexit
from messageCallBack import *
import _thread

brokerAddress="vernemq" 
clientID="0005"
userName="events"
userPassword="ENK0BgJ0XLI-htVx"

##while 1: #time.sleep(10)

def cleanup():
    global mqttc
    mqttc.publish("/GMT/USVC/EVENTS/STATUS","DISCONNECTED",1,True)
    print("\nDisconnecting...\n")
    mqttc.disconnect()
    time.sleep(1)
    print("Exit\n")
    
def on_connect(client, userdata, flags, rc):
    print("MQTT server connected")
    client.publish("/GMT/USVC/EVENTS/STATUS","CONNECTED",1,True)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection. Reason: " + mqtt.connack_string(rc))
    
def status_update(mqtt_client):
    time.sleep(2)
    print("Subscribe to topic: "+ "/GMT/DEV/+/STATUS/#")
    while True:
        print("Check device statuses: ")
        mqtt_client.subscribe("/GMT/DEV/+/STATUS/#")
        time.sleep(60)
    
    
atexit.register(cleanup)
mqttc = mqtt.Client(clientID)
mqttc.username_pw_set(userName, password=userPassword)
mqttc.will_set("/GMT/USVC/EVENTS/STATUS","DISCONNECTED",1,True)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.connect(brokerAddress)
print("Subscribe to topic: "+ "/GMT/DEV/+/DATA/+/JSON")
mqttc.subscribe("/GMT/DEV/+/DATA/+/JSON")
print("Subscribe to topic: "+ "/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF")
mqttc.subscribe("/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF")
print("Subscribe to topic: "+ "/GMT/DEV/+/REQ/#")
mqttc.subscribe("/GMT/DEV/+/REQ/#")
_thread.start_new_thread( status_update, (mqttc, ) )
time.sleep(1)
print("Start mqtt receiving loop")
mqttc.loop_forever()
