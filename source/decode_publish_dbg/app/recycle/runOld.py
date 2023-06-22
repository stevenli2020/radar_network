#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2

import paho.mqtt.client as mqtt
import mysql.connector
import time
from datetime import datetime, timedelta, timezone
import json
import numpy as np
from json import JSONEncoder
from parseFrame import *
import copy
import pytz

brokerAddress="vernemq" 
clientID="0005"
userName="events"
userPassword="3e90edbe0f6cbef1cec300719e684a0e5de648a7"
dataBuffer=[]
SpecialSensors={}


# print(int("1ffe",16))
# exit()

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetric'
}

mqttc = mqtt.Client(clientID)
mqttc.username_pw_set(userName, password=userPassword)
# mqttc.will_set("/GMT/USVC/EVENTS/STATUS","DISCONNECTED",1,True)


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def on_message(mosq, obj, msg):
    global SpecialSensors,mqttc
    # print(msg.payload)
    in_data = ''
    topicList = msg.topic.split('/')
    devName = ''
    # my_obj = eval(in_data)
    # print(in_data)
    print(f"{msg.topic}, {msg.payload}")
    with open("logs", "a+") as myfile:
    #     myfile.write("<"+str(datetime.now(pytz.timezone('Asia/Singapore')))[:23]+">\n[payload] "+str(msg.payload)+"\n[topic]:"+msg.topic+"\n")
        myfile.write("<"+str(datetime.now(pytz.timezone('Asia/Singapore')))[:23]+">[topic]:"+msg.topic+"\n")
    if topicList[-1] == 'RAW':
        in_data = str(msg.payload).replace("b'", "").split(',')
        devName = topicList[3]
        # in_data = in_data.split(':')
        # print(in_data)
        # with open("logs", "a+") as myfile:
        #     # myfile.write("<"+str(datetime.now(pytz.timezone('Asia/Singapore')))[:23]+">\n[payload] "+str(in_data)+"\n")
        #     myfile.write("<"+str(datetime.now(pytz.timezone('Asia/Singapore')))[:23]+">[topic]:"+msg.topic+"\n")
        byteAD = bytearray()
        my_list = []
        for x in in_data:
            ts, hexD = x.split(':')  
            if "'" in hexD:
                hexD = hexD.replace("'", "")    
                byteAD = bytearray.fromhex(hexD)    
            else:
                byteAD = bytearray.fromhex(hexD)
            # try:
            #     byteAD = bytearray.fromhex(hex(hexD))
            # except:
            #     print("An exception occured")
            #     pass
            # byteAD = bytearray.fromhex(hexD)
            # print(f"{ts}, {byteAD}, {hexD}")
            tz = pytz.timezone('Asia/Singapore')
            ts = datetime.fromtimestamp(float(ts), tz)
            # print(ts)
            if len(hexD) > 104:
                outputDict = parseStandardFrame(byteAD)
                # print(outputDict)
                pubD = {
                    # "timestamp": str(ts)[:23],
                    # "error": outputDict['error'],
                    # "frameNum": outputDict['frameNum'],
                    # "pointCloud": outputDict['pointCloud'].tolist()
                }
                if "numDetectedTracks" in outputDict:
                    pubD['timestamp'] = str(ts)[:23]
                    pubD['numDetectedTracks'] = outputDict['numDetectedTracks']
                if "vitals" in outputDict:
                    pubD['vitals'] = outputDict['vitals']
                # if "numDetectedPoints" in outputDict:
                #     pubD['numDetectedPoints'] = outputDict['numDetectedPoints']
                if "trackData" in outputDict:
                    # formatted_list = ['%.2f' % elem for elem in outputDict['trackData'].tolist()]
                    unformat = outputDict['trackData'].tolist()
                    formatted_list = []
                    for i in range(len(unformat)):
                        new = []
                        for j in range(len(unformat[i])):
                            new.append(round(unformat[i][j], 2))
                        formatted_list.append(new)
                    pubD['trackData'] = formatted_list
                    saveInRoomData(devName,str(formatted_list), 1)
                if pubD:
                    dict_copy = copy.deepcopy(pubD)
                    my_list.append(dict_copy)
            else:
                saveOutRoomData(devName)
        pubPayload = {
            "DATA": my_list
        }
        op = len(pubPayload["DATA"])        
        if len(pubPayload["DATA"]) > 0:
            # print(f"on message {op}")
            mqttc.publish("/GMT/DEV/"+devName+"/DATA/JSON", json.dumps(pubPayload))
                # print(f"{ts}, {outputDict}")
    # elif topicList[-1] == 'JSON':
    #     print(msg.payload)

def saveInRoomData(mac, trackD, InR):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO PROCESSED_DATA (MAC, TRACK_DATA, OBJECT_LOCATION) VALUES (%s, %s, %s)", (mac, trackD, InR))
    connection.commit()
    cursor.close()
    connection.close()


def saveOutRoomData(mac):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO PROCESSED_DATA (MAC, OBJECT_LOCATION) VALUES (%s, %s)", (mac, 0))
    connection.commit()
    cursor.close()
    connection.close()

def createTable(dbName):
    connection = mysql.connector.connect(**config)
    # cursor = connection.cursor("CREATE TABLE IF NOT EXISTS %s (ID int NOT Null AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) CURRENT_TIMESTAMP(6), X json, Y json, Z json)",(dbName))
    # connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS "+dbName+" (ID INT AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) DEFAULT CURRENT_TIMESTAMP(6), ts timestamp(6) DEFAULT CURRENT_TIMESTAMP(6),frameNum INT(12), pointCloud json)")
    # cursor.execute("CREATE TABLE IF NOT EXISTS "+dbName+" (ID INT AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) DEFAULT CURRENT_TIMESTAMP(6), ts timestamp(6), byteArray longblob)")
    connection.commit()
    cursor.close()
    connection.close()

mqttc.on_message = on_message
mqttc.connect(brokerAddress)
mqttc.subscribe("/GMT/DEV/#")
# mqttc.publish("/GMT/USVC/EVENTS/STATUS","CONNECTED",1, True)
time.sleep(1)
print("Start mqtt receiving loop")
mqttc.loop_forever()
