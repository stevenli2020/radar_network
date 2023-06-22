#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2

import paho.mqtt.client as mqtt
import mysql.connector
import time
from datetime import datetime, timedelta, timezone
import json

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

def on_message(mosq, obj, msg):
    global SpecialSensors,mqttc
    # print(msg)
    in_data = str(msg.payload)[2:-1]
    # my_obj = eval(in_data)
    print(msg.payload)
    print(in_data)
    tzinfo = timezone(timedelta(hours=8))
    # print(msg.topic + " - " + in_data)
    with open("logs", "a+") as myfile:
        myfile.write("<"+str(datetime.now(tzinfo))[:23]+">\n[SENT] "+in_data+"\n[RECEIVED]: \n")
    TOPIC=msg.topic.split("/")
    print(TOPIC)
    if len(TOPIC)>3:
        return
    now = datetime.now(tzinfo)
    dbName = TOPIC[-1]+now.strftime("%Y%m%d")
    createTable(dbName)
    # print(type(msg.payload))
    print(msg.payload[0])
    print(msg.payload[1])
    print(msg.payload[2])
    # print(my_obj['ts'], my_obj['pointCloud'])
    # connection = mysql.connector.connect(**config)
    # cursor = connection.cursor()
    # cursor.execute("INSERT INTO "+dbName+" (ts, byteArray) VALUES (%s,%s)", (msg.payload['ts'], msg.payload['bytearray'].tostring()))
    
    # connection.commit()
    # cursor.close()
    # connection.close()
    # if "/STATUS" not in msg.topic:
    #     if in_data in dataBuffer:
    #         return
    #     else:
    #         dataBuffer.append(in_data)
    #         if len(dataBuffer)>256:
    #             del dataBuffer[0] 
    # MSG=(in_data).split(":")
    # if len(TOPIC)<5 or len(MSG)<4:
        # print("Data error: "+msg.topic + " -> " + str(msg.payload))
        # return
    # db = mysql.connector.connect(
    #   host="db",
    #   user="flask",
    #   password="CrbI1q)KUV1CsOj-",
    #   database="Gaitmetric"
    # )    
    # cursor = db.cursor(dictionary=True,buffered=True)  
    # if TOPIC[2]!="USVC" and TOPIC[3]=="E":
    #     COORDINATOR_ID=TOPIC[2]
    #     CLUSTER_ID=TOPIC[4]
    #     NODE_ID=TOPIC[5]
    #     EVENT_ID=int(MSG[1], 16)
    #     NODE_TYPE=MSG[0]
    #     NODE_BATT=int(MSG[2], 16)
    #     if NODE_BATT>=4200:
    #         NODE_BATT_PCT=100
    #     elif NODE_BATT<3200:
    #         NODE_BATT_PCT=0
    #     else:
    #         NODE_BATT_PCT = (NODE_BATT-3200)/10
    #     NODE_DATA=int(MSG[3], 16)
        
    #     mqttc.publish("/E/"+COORDINATOR_ID+"/"+CLUSTER_ID+"/"+NODE_ID+"/"+str(EVENT_ID),NODE_TYPE+"-"+str(NODE_BATT)+"-"+str(NODE_DATA)) 
        
    #     # print(MSG[3],NODE_DATA)
    #     if NODE_TYPE=="25":
    #         # print("Special sensor data arrived")
    #         # print(SpecialSensors)
    #         TS = time.time()
    #         if NODE_ID in SpecialSensors:
    #             if SpecialSensors[NODE_ID]["LAST"]==(EVENT_ID+NODE_BATT+NODE_DATA):
    #                 if SpecialSensors[NODE_ID]["LAST_TIME"]-TS<2:
    #                     repeated = True
    #                     return
    #                 else:
    #                     repeated = False
    #             else:
    #                 repeated = False
    #         else:
    #             SpecialSensors[NODE_ID]={}
    #             repeated = False                 
    #         if not repeated:
    #             SpecialSensors[NODE_ID]["LAST"]=EVENT_ID+NODE_BATT+NODE_DATA
    #             SpecialSensors[NODE_ID]["LAST_TIME"]=TS
    #             NODE_BATT_PCT = NODE_BATT
    #             NODE_BATT = 65535
    #         print(SpecialSensors)
    #     elif NODE_TYPE=="03":
    #         if NODE_DATA==0:
    #             NODE_DATA=1
    #         sql="SELECT * FROM `EVENTS` WHERE `NODE_ID`='"+NODE_ID+"' ORDER BY `ID` DESC LIMIT 1;";
    #         cursor.execute(sql)
    #         N=cursor.rowcount
    #         # print(sql)
    #         # print("ROWCOUNT="+str(N))
    #         if N>0:
    #             R = cursor.fetchone()
    #             EVENT_ID_LAST = R['EVENT_ID']
    #         else:
    #             R = cursor.fetchone()
    #             # print(R)
    #             EVENT_ID_LAST=0
    #         if (EVENT_ID-EVENT_ID_LAST) > NODE_DATA:
    #             NODE_DATA = EVENT_ID - EVENT_ID_LAST
    #     print(str(EVENT_ID)+" - "+str(NODE_TYPE)+","+str(NODE_BATT)+","+str(NODE_BATT_PCT)+","+str(NODE_DATA))            
    #     sql = "INSERT INTO `EVENTS` (`COORDINATOR`, `CLUSTER_ID`, `NODE_ID`, `TYPE`, `DATA_TYPE`, `EVENT_ID`, `BAT_LVL`, `BATT_PCT`,`SENSOR_DATA`) VALUES ('"+COORDINATOR_ID+"','"+CLUSTER_ID+"','"+NODE_ID+"','E','"+NODE_TYPE+"',"+str(EVENT_ID)+","+str(NODE_BATT)+","+str(NODE_BATT_PCT)+","+str(NODE_DATA)+")"
    #     # print(sql)
    #     cursor.execute(sql)
    #     # db.commit()
    #     if NODE_TYPE=="03":
    #         sql = "UPDATE `NODES` SET `EVENT_ID`="+str(EVENT_ID)+",`CLUSTER_ID`='"+CLUSTER_ID+"',`SENSOR_TYPE`='"+NODE_TYPE+"',`PARENT`='"+COORDINATOR_ID+"',`BATT_LVL`="+str(NODE_BATT)+",`BATT_PCT`="+str(NODE_BATT_PCT)+",`SENSOR_DATA`="+str(NODE_DATA)+",`CHECKVALUE`=`CHECKVALUE`+"+str(NODE_DATA)+" WHERE `MAC`='"+NODE_ID+"'"      
    #     else:
    #         sql = "UPDATE `NODES` SET `EVENT_ID`="+str(EVENT_ID)+",`CLUSTER_ID`='"+CLUSTER_ID+"',`SENSOR_TYPE`='"+NODE_TYPE+"',`PARENT`='"+COORDINATOR_ID+"',`BATT_LVL`="+str(NODE_BATT)+",`BATT_PCT`="+str(NODE_BATT_PCT)+",`SENSOR_DATA`="+str(NODE_DATA)+",`CHECKVALUE`="+str(NODE_DATA)+" WHERE `MAC`='"+NODE_ID+"'"
    #     # print(sql)
    #     cursor.execute(sql)
    #     db.commit()
    # elif TOPIC[2]!="USVC" and TOPIC[3]=="STATUS":
    #     COORDINATOR_ID=TOPIC[2]
    #     if str(msg.payload)[2:-1]=='CONNECTED':
    #         STATUS = "1"
    #     else:
    #         STATUS = "0"
    #         print(str(msg.payload).strip())
    #     print("Coordinator "+COORDINATOR_ID+" status - "+STATUS)     
    #     sql = "UPDATE `COORDINATORS` SET `CONNECTED`="+STATUS+" WHERE `MAC`='"+COORDINATOR_ID+"';"
    #     cursor.execute(sql)   
    #     sql = "INSERT INTO `STATUS_EVENTS` (`TIME`, `NAME`, `EVENT`) VALUES (NOW(),'"+TOPIC[2]+"','"+str(msg.payload)[2:-1]+"');"
    #     cursor.execute(sql)        
    #     db.commit() 
    # elif TOPIC[2]=="USVC":
    #     sql = "INSERT INTO `STATUS_EVENTS` (`TIME`, `NAME`, `EVENT`) VALUES (NOW(),'"+TOPIC[2]+"-"+TOPIC[3]+"','"+(str(msg.payload)[2:-1]).replace("'","")+"');"
    #     cursor.execute(sql)        
    #     db.commit()   
    # else:
        # print("Received coordinator heart beat, ignored")
    # cursor.close()
    # db.close()

def createTable(dbName):
    connection = mysql.connector.connect(**config)
    # cursor = connection.cursor("CREATE TABLE IF NOT EXISTS %s (ID int NOT Null AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) CURRENT_TIMESTAMP(6), X json, Y json, Z json)",(dbName))
    # connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    # cursor.execute("CREATE TABLE IF NOT EXISTS "+dbName+" (ID INT AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) DEFAULT CURRENT_TIMESTAMP(6), ts timestamp(6), pointCloud json)")
    cursor.execute("CREATE TABLE IF NOT EXISTS "+dbName+" (ID INT AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) DEFAULT CURRENT_TIMESTAMP(6), ts timestamp(6), byteArray longblob)")
    connection.commit()
    cursor.close()
    connection.close()

mqttc = mqtt.Client(clientID)
mqttc.username_pw_set(userName, password=userPassword)
# mqttc.will_set("/GMT/USVC/EVENTS/STATUS","DISCONNECTED",1,True)
mqttc.on_message = on_message
mqttc.connect(brokerAddress)
mqttc.subscribe("/GMT/#")
# mqttc.publish("/GMT/USVC/EVENTS/STATUS","CONNECTED",1, True)
time.sleep(1)
print("Start mqtt receiving loop")
mqttc.loop_forever()
