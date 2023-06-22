#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2

import paho.mqtt.client as mqtt
import time
#import pytz
#from datetime import datetime, timedelta, timezone
#import json
import numpy as np
#from json import JSONEncoder
#from threading import Thread
import atexit
import os
from runlib import *
#import gzip,shutil

brokerAddress="vernemq" 
clientID="0003"
userName="save-raw-data2"
userPassword="7XS*c2-Hfh*sCMj."
dataBuffer={}
last_date=""

##while 1: #time.sleep(10) 

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetric'
}
                              
def cleanup():
    global mqttc
    mqttc.publish("/GMT/USVC/SAVERAWDATA/STATUS","DISCONNECTED",1,True)
    print("\nDisconnecting...\n")
    mqttc.disconnect()
    time.sleep(1)
    print("Exit\n")         
    
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_connect(client, userdata, flags, rc):
    print("MQTT server connected")
    client.publish("/GMT/USVC/SAVERAWDATA/STATUS","CONNECTED",1,True)


atexit.register(cleanup)
mqttc = mqtt.Client(clientID)
mqttc.username_pw_set(userName, password=userPassword)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.will_set("/GMT/USVC/SAVERAWDATA/STATUS","DISCONNECTED",qos=1, retain=True)
mqttc.connect(brokerAddress,1883,10)
print("Subscribe to topic: "+ "/GMT/DEV/+/DATA/+/RAW/#")
mqttc.subscribe("/GMT/DEV/+/DATA/+/RAW/#")
time.sleep(1)
print("Start mqtt receiving loop")
mqttc.loop_forever()
