#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mysql.connector
import time
import requests
from datetime import datetime, timedelta, timezone 
import paho.mqtt.client as mqtt
import _thread


brokerAddress="vernemq" 
clientID="0004"
userName="zap-conn"
userPassword="4068f0880b399410602d694b3cc711c8a8f4727e"
mqttc = mqtt.Client(clientID)

_count = "100"
_sensorID = "TEST_STEVEN"


def MQTT_Loop(HOST, UN, PWD):
    global mqttc
    while 1:
        mqttc.username_pw_set(UN, password=PWD)
        mqttc.will_set("/FSSN/USVC/ZAP_CONNECT/STATUS","DISCONNECTED",1,True)
        mqttc.connect(HOST)
        mqttc.publish("/FSSN/USVC/ZAP_CONNECT/STATUS","CONNECTED",1, True)
        time.sleep(1)
        print("Start mqtt receiving loop")
        mqttc.loop_forever() 
        print("Mqtt loop interrupted")
        time.sleep(2)


_thread.start_new_thread( MQTT_Loop,(brokerAddress, userName, userPassword))
time.sleep(2)

while 1:
    db = mysql.connector.connect(
      host="db",
      user="flask",
      password="CrbI1q)KUV1CsOj-",
      database="Gaitmetric"
    )
    cursor = db.cursor(dictionary=True)    
    cursor.execute("SELECT * FROM NODES WHERE `ZAP_CONNECT`!=0;")
    result = cursor.fetchall()
    tzinfo = timezone(timedelta(hours=8))
    print("<"+str(datetime.now(tzinfo))[:23]+">")
    for row in result:
        CLUSTER_ID = row['CLUSTER_ID']
        NODE_ID = row['MAC']
        ts = datetime.now(tzinfo)
        TIMESTAMP = ts.strftime('%d-%b-%y %I:%M:%S%p')
        if row['SENSOR_TYPE'].lower() == "a9":
            cursor.execute("select CEIL(AVG(SENSOR_DATA)) AS Data from EVENTS where TIME >= DATE_SUB(NOW(),INTERVAL 30 MINUTE) AND NODE_ID='"+NODE_ID+"';")
            R = cursor.fetchone()
            if R['Data']==None:
                DATA = "Value1=%d&SensorID=%s&Timestamp=%s" % (0,CLUSTER_ID+"-"+NODE_ID,TIMESTAMP)
            else:
                DATA = "Value1=%d&SensorID=%s&Timestamp=%s" % (R['Data'],CLUSTER_ID+"-"+NODE_ID,TIMESTAMP)
            # x = requests.post(URL_WEB_HOOK_2, data = DATA, headers=HEADER)
        else:
            if row['SENSOR_TYPE'].lower() == "03":
                cursor.execute("select SUM(`SENSOR_DATA`) as CNT from EVENTS where TIME >= DATE_SUB(NOW(),INTERVAL 30 MINUTE) AND NODE_ID='"+NODE_ID+"';")
            elif row['SENSOR_TYPE'].lower() == "d3":
                cursor.execute("select COUNT(*) as CNT from EVENTS where TIME >= DATE_SUB(NOW(),INTERVAL 30 MINUTE) AND NODE_ID='"+NODE_ID+"';")
            R = cursor.fetchone()
            if R['CNT'] == None:
                CNT = 0
            else:
                CNT = int(R['CNT'])
            DATA = "Count=%d&SensorID=%s&Timestamp=%s" % (CNT,CLUSTER_ID+"-"+NODE_ID,TIMESTAMP)
            # x = requests.post(URL_WEB_HOOK_1, data = DATA, headers=HEADER)
        # print("[SENT] "+DATA+"\n[RECEIVED]: "+x.text)
        time.sleep(1)
        mqttc.publish("/FSSN/USVC/ZAP_CONNECT/EVENT",DATA,1, False)
        with open("logs", "a+") as myfile:
            myfile.write("<"+str(datetime.now(tzinfo))[:23]+">\n[SENT] "+DATA+"\n[RECEIVED]: \n")        
            # myfile.write("<"+str(datetime.now(tzinfo))[:23]+">\n[SENT] "+DATA+"\n[RECEIVED]: "+x.text+"\n")        
    
    
    
    cursor.close()
    db.close()   
    print("\n")

    dt = datetime.now() + timedelta(minutes=30)
    while datetime.now() < dt:
        time.sleep(2)


