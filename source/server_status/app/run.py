#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2

import mysql.connector
import time
import _thread
from datetime import datetime, timedelta, timezone 
import paho.mqtt.client as mqtt
import signal
import atexit

def handle_exit():
    global BYTES_SENT_PREV,BYTES_RECEIVED_PREV
    print('\r\nSaving data ...')
    with open("save", "w+") as f:
        f.seek(0)
        f.write(str(int(time.time()))+"\r\nBYTES_SENT_PREV="+str(BYTES_SENT_PREV)+"\r\nBYTES_RECEIVED_PREV="+str(BYTES_RECEIVED_PREV))
        f.truncate()
    exit()   

atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

INTERVAL = 10

brokerAddress="vernemq" 
clientID="0007"
userName="server_status"
userPassword="ae0c3024df9f197152882c32dc17e5f09b478739"
mqttc=mqtt.Client(clientID)
    
CPU_PREV={}
BYTES_SENT_PREV=0
BYTES_RECEIVED_PREV=0
TIME_SENT_PREV=0
TIME_RECEIVED_PREV=0
SENT_B=0
RCVD_B=0

with open("save") as f:
    TIME_PREV=f.readline()
    BYTES_SENT_PREV=int(f.readline().split("=")[1])
    BYTES_RECEIVED_PREV=int(f.readline().split("=")[1])
    TIME_SENT_PREV=int(TIME_PREV)
    TIME_RECEIVED_PREV=int(TIME_PREV)

print(BYTES_SENT_PREV, BYTES_RECEIVED_PREV)

def on_message(mosq, obj, msg):
    global BYTES_SENT_PREV,BYTES_RECEIVED_PREV,SENT_B,RCVD_B,TIME_PREV,TIME_RECEIVED_PREV,TIME_SENT_PREV
    # print(msg.topic + " - " + str(msg.payload))
    T = int(time.time())
    
    if "/bytes/sent" in msg.topic:
        SENT_B = round((int(msg.payload) - BYTES_SENT_PREV)/(T-TIME_SENT_PREV),4)
        BYTES_SENT_PREV = int(msg.payload)
        # print("T =",T-TIME_SENT_PREV)
        TIME_SENT_PREV = T
        
    if "/bytes/received" in msg.topic:
        RCVD_B = round((int(msg.payload) - BYTES_RECEIVED_PREV)/(T-TIME_RECEIVED_PREV),4)
        BYTES_RECEIVED_PREV = int(msg.payload)
        # print("T =",T-TIME_RECEIVED_PREV)
        TIME_RECEIVED_PREV = T
        
    # print(SENT_B,RCVD_B)
    
def MQTT_Loop(HOST, UN, PWD):
    global mqttc
    tzinfo=timezone(timedelta(hours=8))
    print("<"+str(datetime.now(tzinfo))[:23]+">")    
    print("[MQTT_Loop] Service started")     
    while 1:
        mqttc.username_pw_set(UN, password=PWD)
        mqttc.on_message = on_message
        mqttc.will_set("/FSSN/USVC/SERVER_STATUS/STATUS","DISCONNECTED",1,True)
        mqttc.connect(HOST)
        time.sleep(0.5)
        mqttc.subscribe("$SYS/+/bytes/#")
        mqttc.publish("/FSSN/USVC/SERVER_STATUS/STATUS","CONNECTED",1, True)
        print("Start mqtt receiving loop")
        mqttc.loop_forever() 
        print("Mqtt loop interrupted")
        time.sleep(2)

def getCPU():
    global CPU_PREV
    with open('/proc/stat') as f:
        CPU=f.readline().split()  
    if CPU_PREV=={}:
        CPU_PREV=CPU
        return 0
    previdle=int(CPU_PREV[4])
    previowait=int(CPU_PREV[5])
    prevuser=int(CPU_PREV[1])
    prevnice=int(CPU_PREV[2])
    prevsystem=int(CPU_PREV[3])
    previrq=int(CPU_PREV[6])
    prevsoftirq=int(CPU_PREV[7])
    prevsteal=int(CPU_PREV[8])

    idle=int(CPU[4])
    iowait=int(CPU[5])
    user=int(CPU[1])
    nice=int(CPU[2])
    system=int(CPU[3])
    irq=int(CPU[6])
    softirq=int(CPU[7])
    steal=int(CPU[8])    

    PrevIdle=previdle+previowait
    Idle=idle+iowait
    PrevNonIdle=prevuser+prevnice+prevsystem+previrq+prevsoftirq+prevsteal
    NonIdle=user+nice+system+irq+softirq+steal
    PrevTotal=PrevIdle+PrevNonIdle
    Total=Idle+NonIdle
    totald=Total-PrevTotal
    idled=Idle-PrevIdle
    CPU_Percentage=(totald-idled)/totald
    CPU_PREV=CPU
    return round(CPU_Percentage,4)
    
def getMEM():
    with open('/proc/meminfo') as f:
        TOTAL=int(int(f.readline().split()[1])/1024)
        TMP=f.readline()
        AVAIL=int(int(f.readline().split()[1])/1024)
        USED=TOTAL-AVAIL
    return [TOTAL,USED]
    
_thread.start_new_thread( MQTT_Loop,(brokerAddress, userName, userPassword))  

time.sleep(1)
while 1:
    CPU_PCT=getCPU()
    MEM=getMEM()
    MEM_TOTAL=MEM[0]
    MEM_USED=MEM[1]
    
    db = mysql.connector.connect(
      host="db",
      user="flask",
      password="CrbI1q)KUV1CsOj-",
      database="Gaitmetric"
    )    
    cursor = db.cursor(dictionary=True,buffered=True)    
    cursor.execute("SELECT COUNT(ID) AS N FROM EVENTS WHERE TIME >= DATE_SUB(NOW(), INTERVAL 1 HOUR);")
    R = cursor.fetchone()
    EVENTS_PER_HOUR = R["N"]
    print('{"MEM_USED":'+str(MEM_USED)+',"MEM_TOTAL":'+str(MEM_TOTAL)+',"CPU":'+str(CPU_PCT)+',"BPS_SENT":'+str(SENT_B)+',"BPS_RCVD":'+str(RCVD_B)+',"EVENTS_PER_HOUR":'+str(EVENTS_PER_HOUR)+'}')
    cursor.execute("INSERT INTO `STATUS`(`MEM_USED`, `MEM_TOTAL`, `CPU`, `BPS_SEND`, `BPS_RCVD`, `EVENTS_PER_HOUR`) VALUES ("+str(MEM_USED)+","+str(MEM_TOTAL)+","+str(CPU_PCT)+","+str(SENT_B)+","+str(RCVD_B)+","+str(EVENTS_PER_HOUR)+");")
    # cursor.execute("INSERT INTO `STATUS` (`STATUS`) VALUES ('"+'{"MEM_AVAIL":'+str(MEM_AVAIL)+',"MEM_TOTAL":'+str(MEM_TOTAL)+',"CPU":'+str(CPU_PCT)+',"BPS_SENT":'+str(SENT_B)+',"BPS_RCVD":'+str(RCVD_B)+',"EVENTS_PER_HOUR":'+str(EVENTS_PER_HOUR)+'}'+"')")
    ID = cursor.lastrowid
    if ID>1000000:
        cursor.execute("DELETE FROM `STATUS` WHERE `ID`<"+str(ID-1000000)+";")
    db.commit()  
    cursor.close()
    db.close()    
    time.sleep(INTERVAL)
    