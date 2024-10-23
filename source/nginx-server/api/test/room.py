#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2
import numpy as np
import mysql.connector
import sys
np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)
config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}

roomName=sys.argv[1]
timeRange=sys.argv[2]

N,U=timeRange.split(" ")

NUM = int(N)
if U.upper() == "DAY":
    TOTAL_SECONDS = NUM * 86400
elif U.upper() == "HOUR":
    TOTAL_SECONDS = NUM * 3600
elif U.upper() == "WEEK":
    TOTAL_SECONDS = NUM * 604800
elif U.upper() == "MONTH":
    TOTAL_SECONDS = NUM * 2592000
else:
    print("Time range error, exit")
    exit()
  
connection = mysql.connector.connect(**config)
cursor = connection.cursor(dictionary=True)      

sql = "SELECT GROUP_CONCAT(MAC SEPARATOR '\\',\\'') FROM ROOMS_DETAILS LEFT JOIN RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID WHERE ROOM_NAME = '%s';" % (roomName)
print(sql)
cursor.execute(sql)
dbresult = cursor.fetchone() 
try:
    List = "IN ('"+dbresult[next(iter(dbresult))]+"')"
except:
    print("No data related to room name")
    exit()    

sql = "SELECT COUNT(*) AS CNT FROM `PROCESSED_DATA` WHERE MAC %s AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND OBJECT_LOCATION = 1;" %(List, timeRange)
print(sql)
# exit()
cursor.execute(sql)
dbresult = cursor.fetchone() 
if dbresult == None:
    print("No data")
    exit()
IN_ROOM_SECONDS = int(dbresult["CNT"]*2)

sql = "SELECT COUNT(*) AS CNT FROM `PROCESSED_DATA` WHERE MAC %s AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND IN_BED = 1;" %(List, timeRange)
print(sql)
cursor.execute(sql)
dbresult = cursor.fetchone() 
if dbresult == None:
    print("No data")
    exit()
IN_BED_SECONDS = int(dbresult["CNT"]*2)


print("IN_ROOM_SECONDS = %d, IN_BED_SECONDS = %d, IN_ROOM_PCT = %.2f%%" %(IN_ROOM_SECONDS, IN_BED_SECONDS, round(IN_ROOM_SECONDS*100/TOTAL_SECONDS,4)))

cursor.close()
connection.close() 