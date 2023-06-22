#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2
import numpy as np
import mysql.connector
import sys, json
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
print(dbresult)
try:
    List = "IN ('"+dbresult[next(iter(dbresult))]+"')"
except:
    print("No data related to room name")
    exit()    

sql = "SELECT DATE_FORMAT(TIMESTAMP, \'%%Y-%%m-%%d %%H:%%i\') AS T, ROUND(AVG(HEART_RATE),1) AS HR, ROUND(AVG(BREATH_RATE),1) AS BR FROM PROCESSED_DATA WHERE MAC %s AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s) AND HEART_RATE IS NOT NULL AND HEART_RATE !=0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE !=0 GROUP BY T ORDER BY `T` DESC;" %(List, timeRange)
print(sql)
cursor.execute(sql)
dbresult = cursor.fetchall() 
if dbresult == None:
    print("No data")
    exit()
cursor.close()
connection.close() 
print(json.dumps(dbresult))