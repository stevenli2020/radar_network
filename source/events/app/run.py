#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2

import paho.mqtt.client as mqtt
import time
from datetime import datetime, timedelta, timezone
import atexit
import messageCallBack

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
    
atexit.register(cleanup)
mqttc = mqtt.Client(clientID)
mqttc.username_pw_set(userName, password=userPassword)
mqttc.will_set("/GMT/USVC/EVENTS/STATUS","DISCONNECTED",1,True)
mqttc.on_message = messageCallBack.on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.connect(brokerAddress)
print("Subscribe to topic: "+ "/GMT/DEV/+/DATA/+/JSON")
mqttc.subscribe("/GMT/DEV/+/DATA/+/JSON")
print("Subscribe to topic: "+ "/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF")
mqttc.subscribe("/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF")
print("Subscribe to topic: "+ "/GMT/DEV/+/REQ/#")
mqttc.subscribe("/GMT/DEV/+/REQ/#")
time.sleep(1)
print("Start mqtt receiving loop")
mqttc.loop_forever()