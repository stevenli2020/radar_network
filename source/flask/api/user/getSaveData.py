import math
from unittest import result
import mysql.connector
from user.config import config
from datetime import datetime, timedelta
from user.parseFrame import *
import pytz
import copy
from collections import defaultdict
import numpy as np
import json
import time
import pandas as pd
from tzlocal import get_localzone

config = config()
now = datetime.now()
format_now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
def getSaveRawData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    now = datetime.now()
    if(data['CUSTOM'] == 1):  #check request time include custom time
        ts = data['TIME'].split('-') #split request time into start time and stop time
        sql = "SELECT * FROM RECORD_RAW_DATA WHERE MAC='%s' AND TIME BETWEEN '%s' AND '%s' "%(data['DEVICEMAC'], ts[0], ts[-1]) #sql query
    else:
        t = data['TIME'].split(' ')[0]
        if "MINUTE" in data['TIME']: #check request time in minute                                
            before = now - timedelta(minutes=int(t)) #minus current time t minute           
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f') #change time format              
        elif "HOUR" in data['TIME']: #check reqest time in hour
            before = now - timedelta(hours=int(t)) #minus current time t hour            
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f') #change time format
        sql = "SELECT * FROM RECORD_RAW_DATA WHERE MAC='%s' AND TIME BETWEEN '%s' AND '%s' "%(data['DEVICEMAC'], format_before, format_now) #sql query
    cursor.execute(sql)
    dbresult = cursor.fetchall() # get all retrieve data
    if dbresult:
        my_list = []
        for x in dbresult:
            in_data = str(x[3]).split(',') #split raw data into individual
            # print(in_data)
            byteAD = bytearray()            
            for x in in_data:
                ts, hexD = x.split(':')  #split timestamp and radar raw data
                if "'" in hexD:
                    hexD = hexD.replace("'", "")    
                    byteAD = bytearray.fromhex(hexD) #convert hex string to byte array
                else:
                    byteAD = bytearray.fromhex(hexD) #convert hex string to byte array
                tz = pytz.timezone('Asia/Singapore')
                ts = datetime.fromtimestamp(float(ts), tz) #change time into timestamp format
                if len(hexD) > 104: #check raw data is not empty
                    outputDict = parseStandardFrame(byteAD) #convert byte array data into pointcloud data
                    print(outputDict)
                    decodeData = {}
                    if "numDetectedTracks" in outputDict:
                        decodeData['timestamp'] = str(ts)[:23]
                        decodeData['numDetectedTracks'] = outputDict['numDetectedTracks']
                    # if "numDetectedPoints" in outputDict:
                    #     decodeData['numDetectedPoints'] = outputDict['numDetectedPoints']
                    if "trackData" in outputDict:
                        decodeData['trackData'] = outputDict['trackData'].tolist()
                    if decodeData:
                        dict_copy = copy.deepcopy(decodeData)
                        my_list.append(dict_copy)
            # result["DATA"] = [{"ID": ID, "TIME": TIME, "MAC": MAC, "RAW_DATA": RAW_DATA} for (ID, TIME, MAC, RAW_DATA) in dbresult]
        if my_list:
            result["DATA"] = my_list
        else:
            result['CODE'] = 0
        # print(my_list)
    else:
        result['CODE'] = -1
    # result["DATA"] = [{"ID": ID, "TIME": TIME, "MAC": MAC, "RAW_DATA": RAW_DATA} for (ID, TIME, MAC, RAW_DATA) in cursor]
    cursor.close()
    connection.close()
    return result

def getHistOfVitalData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)    
    sql = "SELECT GROUP_CONCAT(MAC) FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID WHERE ROOMS_DETAILS.ROOM_UUID ='%s'" % (data["ROOM_UUID"])
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    
    try:
        db = dbresult[0].split(',')
        MAC_LIST = ""
        for MAC in db:
            if MAC_LIST != "":
                MAC_LIST += ","
            MAC_LIST += f"""'{MAC}'"""
        List = f"IN ({MAC_LIST})"
    except:
        result["ERROR"].append({'Message': 'No data related to room name!'})
        return result
    if data['CUSTOM'] != 1:
        sql = "SELECT `TIMESTAMP`, `HEART_RATE`, `BREATH_RATE` FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s) AND HEART_RATE IS NOT NULL AND HEART_RATE >0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE >0;" %(List, data['TIME'])
    else: 
        sql = "SELECT `TIMESTAMP`, `HEART_RATE`, `BREATH_RATE` FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP BETWEEN '%s' AND '%s' AND HEART_RATE IS NOT NULL AND HEART_RATE >0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE >0;" %(List, data['TIMESTART'], data['TIMEEND'])

    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    if not dbresult:
        result["ERROR"].append({'Message': 'No data!'})
        return result 
    
    df = pd.DataFrame(dbresult, columns=['TIMESTAMP', 'HEART_RATE', 'BREATH_RATE'])

    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])

    # Get the local timezone
    local_timezone = get_localzone()

    # Localize timestamps to the local timezone
    df['TIMESTAMP'] = df['TIMESTAMP'].dt.tz_localize(local_timezone)

    # # Subtract 8 hours from each timestamp
    df['TIMESTAMP'] = df['TIMESTAMP'].dt.tz_convert('UTC')

    # df['TIMESTAMP'] -= timedelta(hours=8)

    average_heart_rate = round(df['HEART_RATE'].mean(), 1)
    average_breath_rate = round(df['BREATH_RATE'].mean(), 1)

    print(df['HEART_RATE'].min(),df['HEART_RATE'].max())

    df.set_index('TIMESTAMP', inplace=True)

    df_resampled = df.resample('1Min').mean()

    df_resampled.fillna(0, inplace=True)

    data_obj = {}
    for index, row in df_resampled.iterrows():
        t = int(index.timestamp())
        if (not result.get("TIME_START")):
            result["TIME_START"].append(t)
        data_obj[t] = [round(row['HEART_RATE'],1), round(row['BREATH_RATE'],1)]

    new_query_data = []
    for t, d in data_obj.items():
        new_query_data.append(str(d[0]) + ',' + str(d[1]))

    result_data = ';'.join(new_query_data)
    result['DATA'].append(result_data)

    result["AVG"].append([average_heart_rate,average_breath_rate])
    cursor.close()
    connection.close()
    return result

def getHistOfVitalMovingAverageData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)    
    sql = "SELECT GROUP_CONCAT(MAC) FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID WHERE ROOMS_DETAILS.ROOM_UUID ='%s'" % (data["ROOM_UUID"])
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    
    # print(dbresult)
    try:
        db = dbresult[0].split(',')
        List = "IN ('"+db[0]+"','"+db[1]+"')"
    except:
        # print("No data related to room name")
        result["ERROR"].append({'Message': 'No data related to room name!'})
        return result
    if data['CUSTOM'] != 1:
        sql = "SELECT DATE_FORMAT(TIMESTAMP, \'%%Y-%%m-%%d %%H:%%i\') AS T, ROUND(AVG(HEART_RATE),1) AS HR, ROUND(AVG(BREATH_RATE),1) AS BR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s) AND HEART_RATE IS NOT NULL AND HEART_RATE !=0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE !=0 GROUP BY T ORDER BY `T` ASC;" %(List, data['TIME'])
    else: 
        sql = "SELECT DATE_FORMAT(TIMESTAMP, \'%%Y-%%m-%%d %%H:%%i\') AS T, ROUND(AVG(HEART_RATE),1) AS HR, ROUND(AVG(BREATH_RATE),1) AS BR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP BETWEEN '%s' AND '%s' AND HEART_RATE IS NOT NULL AND HEART_RATE !=0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE !=0 GROUP BY T ORDER BY `T` ASC;" %(List, data['TIMESTART'], data['TIMEEND'])
    print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        return result 
    query_data = dbresult
    time_start = 0
    time_end = 0
    time_format = "%Y-%m-%d %H:%M"
    if data['CUSTOM'] != 1:
        time_start = int(time.mktime(time.strptime(query_data[0][0], time_format)))
        time_end   = int(time.mktime(time.strptime(query_data[-1][0], time_format)))
    else:
        time_start = int(time.mktime(time.strptime(data['TIMESTART'], time_format)))
        time_end   = int(time.mktime(time.strptime(data['TIMEEND'], time_format)))
    result["TIME_START"].append(time_start)
    # print(time_start,time_end)
    data_obj = {}
    for T in range(time_start, time_end, 60):
        data_obj[T] = [0,0]
    # print(data_obj)
    for d in query_data:
        t = int(time.mktime(time.strptime(d[0], time_format)))
        data_obj[t] = [d[1],d[2]]
    new_query_data = []
    # new_query_data_str = ""
    for t, d in data_obj.items():
        # new_query_data.append([datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M"), d[0], d[1]])
        # new_query_data_str = new_query_data_str + str(d[0]) + ',' + str(d[1])+';'
        new_query_data.append(str(d[0]) + ',' + str(d[1]))
    result['DATA'].append(';'.join(new_query_data))
    # result['DATA'].append(new_query_data_str)
    if data['CUSTOM'] != 1: 
        sql = "SELECT ROUND(AVG(HEART_RATE), 1) as AHR, ROUND(AVG(BREATH_RATE), 1) as ABR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND HEART_RATE > 0 AND BREATH_RATE > 0 AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s);" %(List, data['TIME'])
    else:
        sql = "SELECT ROUND(AVG(HEART_RATE), 1) as AHR, ROUND(AVG(BREATH_RATE), 1) as ABR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND HEART_RATE > 0 AND BREATH_RATE > 0 AND TIMESTAMP BETWEEN '%s' AND '%s';" %(List, data['TIMESTART'], data['TIMEEND'])
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    result["AVG"].append(dbresult)
    cursor.close()
    connection.close()
    return result

def _getHistOfVitalData(data):
    # SELECT series.TIMESTAMP as TIMESTAMP, COALESCE(dt.HEART_RATE, 0) as HEART_RATE, COALESCE(dt.BREATH_RATE, 0) as BREATH_RATE FROM (SELECT FROM_UNIXTIME(FLOOR((UNIX_TIMESTAMP(TIMESTAMP)) DIV 900)*900) AS TIMESTAMP, AVG(HEART_RATE) as HEART_RATE, AVG(BREATH_RATE) as BREATH_RATE FROM PROCESSED_DATA WHERE HEART_RATE > 0 AND TIMESTAMP BETWEEN NOW() - INTERVAL 1 DAY AND NOW() GROUP BY TIMESTAMP) dt RIGHT JOIN (SELECT date_format(date_add(NOW() - INTERVAL 1 DAY, INTERVAL @num:=@num+900 SECOND), '%Y-%m-%d %H:%i:00') TIMESTAMP FROM PROCESSED_DATA, (select @num:=-900) num LIMIT 97) series ON TIMEDIFF(series.TIMESTAMP,dt.TIMESTAMP) < '00:04:59' AND TIMEDIFF(series.TIMESTAMP,dt.TIMESTAMP) > '-00:00:01' GROUP BY `TIMESTAMP` ORDER BY TIMESTAMP ASC;
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    intervalSecond = 60
    limit = 13
    intervalMinute = "00:04:59"
    sql = ''
    format_date = "'%Y-%m-%d %H:%i:00'"
    if not 'DEVICEMAC' in data:
        result["ERROR"].append({'Message': 'MAC is empty!'})
        return result
    if data['TIME'] == "1 HOUR":
        intervalSecond = 60
        limit = 61
        intervalMinute = '00:00:59'
        format_date = "'%Y-%m-%d %H:%i:00'"
    if data['TIME'] == '1 DAY':
        intervalSecond = 900
        limit = 97
        intervalMinute = '00:14:59'
        format_date = "'%Y-%m-%d %H:%i:00'"
    if data['TIME'] == '1 WEEK':
        intervalSecond = 7200
        limit = 85
        intervalMinute = '01:59:59'
        format_date = "'%Y-%m-%d %H:00:00'"
    if data['TIME'] == '1 MONTH':
        intervalSecond = 43200
        limit = 61
        intervalMinute = "11:59:59"
        format_date = "'%Y-%m-%d %H:00:00'"
    sql = "SELECT series.TIMESTAMP as TIMESTAMP, COALESCE(dt.HEART_RATE, 0) as HEART_RATE, COALESCE(dt.BREATH_RATE, 0) as BREATH_RATE, MAC FROM (SELECT FROM_UNIXTIME(FLOOR((UNIX_TIMESTAMP(TIMESTAMP)) DIV %d)*%d) AS TIMESTAMP, ROUND(AVG(HEART_RATE), 2) as HEART_RATE, ROUND(AVG(BREATH_RATE), 2) as BREATH_RATE, MAC FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND HEART_RATE > 0 AND TIMESTAMP BETWEEN NOW() - INTERVAL %s AND NOW() GROUP BY TIMESTAMP) dt RIGHT JOIN (SELECT date_format(date_add(NOW() - INTERVAL %s, INTERVAL @num:=@num+%d SECOND), %s) TIMESTAMP FROM Gaitmetrics.PROCESSED_DATA, (select @num:=-%d) num LIMIT %d) series ON TIMEDIFF(series.TIMESTAMP,dt.TIMESTAMP) < '%s' AND TIMEDIFF(series.TIMESTAMP,dt.TIMESTAMP) > '-00:00:01' GROUP BY TIMESTAMP ORDER BY TIMESTAMP ASC;"%(intervalSecond, intervalSecond, data['DEVICEMAC'], data['TIME'], data['TIME'], intervalSecond, format_date, intervalSecond, limit, intervalMinute)
    cursor.execute(sql)
    dbresult = cursor.fetchall()    
    # print(dbresult)    
    hr = []
    br = []
    alpha = 0.2
    # result["SQL"].append({"SQL": sql})
    for row in dbresult:
        hr.append(row[1])
        br.append(row[2])

    hr = calculate_ema(hr,alpha)
    br = calculate_ema(br,alpha)

    for index in range(len(dbresult)):
        result["DATA"].append({"TIMESTAMP": dbresult[index][0], "HEART_RATE": hr[index], "BREATH_RATE": br[index]})

    sql = "SELECT ROUND(AVG(HEART_RATE), 2) as HEART_RATE, ROUND(AVG(BREATH_RATE), 2) as BREATH_RATE FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND HEART_RATE > 0 AND TIMESTAMP BETWEEN NOW() - INTERVAL %s AND NOW()"%(data['DEVICEMAC'], data['TIME'])
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    result["AVG"].append(dbresult)
    cursor.close()
    connection.close()
    return result

def calculate_ema(data, alpha):
    ema = [data[0]]  # Initialize EMA with the first data point
    
    for i in range(1, len(data)):
        ema_value = alpha * data[i] + (1 - alpha) * ema[i - 1]
        ema.append(ema_value)
    
    return ema

def getSaveData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    now = datetime.now()
    format_now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    if(data['CUSTOM'] == 1):  #check request time include custom time
        ts = data['TIME'].split('-') #split request time into start time and stop time
        # sql = "SELECT * FROM PROCESSED_DATA WHERE MAC='%s' AND TIMESTAMP BETWEEN '%s' AND '%s' "%(data['DEVICEMAC'], ts[0], ts[-1]) #sql query
        sql = "SELECT TIMESTAMP, HEART_RATE, BREATH_RATE FROM PROCESSED_DATA WHERE MAC='%s' AND TIMESTAMP BETWEEN '%s' AND '%s' AND HEART_RATE IS NOT NULL AND BREATH_RATE IS NOT NULL"%(data['DEVICEMAC'], ts[0], ts[-1]) #sql query
        with open("logs", "a+") as myfile:
            myfile.write("sql: "+str(sql)+"\n before: "+str(ts[0])+"\n now: "+str(ts[1])+"\n")
    else:
        t = data['TIME'].split(' ')[0]
        if "MINUTE" in data['TIME']: #check request time in minute                                
            before = now - timedelta(minutes=int(t)) #minus current time t minute           
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f') #change time format              
        elif "HOUR" in data['TIME']: #check reqest time in hour
            before = now - timedelta(hours=int(t)) #minus current time t hour            
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f') #change time format
        elif "DAY" in data['TIME']: #check reqest time in hour
            before = now - timedelta(days=1) #minus current time t hour            
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f') #change time format
        elif "WEEK" in data['TIME']: #check reqest time in hour
            before = now - timedelta(days=7) #minus current time t hour            
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f') #change time format
        elif "MONTH" in data['TIME']: #check reqest time in hour
            before = now - timedelta(days=30) #minus current time t hour            
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f') #change time format
        # sql = "SELECT * FROM PROCESSED_DATA WHERE MAC='%s' AND TIMESTAMP BETWEEN '%s' AND '%s' "%(data['DEVICEMAC'], format_before, format_now) #sql query
        sql = "SELECT TIMESTAMP, HEART_RATE, BREATH_RATE FROM PROCESSED_DATA WHERE MAC='%s' AND TIMESTAMP BETWEEN '%s' AND '%s' AND HEART_RATE IS NOT NULL AND BREATH_RATE IS NOT NULL"%(data['DEVICEMAC'], format_before, format_now) #sql query
        with open("logs", "a+") as myfile:
            myfile.write("sql: "+str(sql)+"\n before: "+str(format_before)+"\n now: "+str(format_now)+"\n")
    # print(sql)
    cursor.execute(sql)   
    # print(cursor) 
    # result["DATA"] = [{"ID": ID, "TIMESTAMP": TIMESTAMP, "MAC": MAC, "TRACK_DATA": TRACK_DATA, "POSTURE": POSTURE, "OBJECT_LOCATION": OBJECT_LOCATION, "HEART_RATE": HEART_RATE, "HEART_WAVEFORM": HEART_WAVEFORM, "BREATH_RATE": BREATH_RATE, "BREATH_WAVEFORM": BREATH_WAVEFORM} for (ID, TIMESTAMP, MAC, TRACK_DATA, POSTURE, OBJECT_LOCATION, HEART_RATE, HEART_WAVEFORM, BREATH_RATE, BREATH_WAVEFORM) in cursor]
    result["DATA"] = [{"TIMESTAMP": TIMESTAMP,"HEART_RATE": HEART_RATE, "BREATH_RATE": BREATH_RATE} for (TIMESTAMP, HEART_RATE, BREATH_RATE) in cursor]
    cursor.close()
    connection.close()
    return result

def getAnalyticDataofPosture(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)

    IN_ROOM_SECONDS_HOUR = 0
    IN_BED_SECONDS_HOUR = 0
    IN_ROOM_SECONDS_DAY = 0
    IN_BED_SECONDS_DAY = 0   
    IN_ROOM_SECONDS_WEEK = 0
    IN_BED_SECONDS_WEEK = 0
    IN_ROOM_SECONDS_MONTH = 0
    IN_BED_SECONDS_MONTH = 0   
    
    sql = "SELECT GROUP_CONCAT(MAC) FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID WHERE ROOMS_DETAILS.ROOM_UUID = '%s';" % (data['ROOM_UUID'])
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    # print(dbresult)
    try:
        db = dbresult[0].split(',')
        # print(db)
        if len(db) > 1:
            List = "IN ('"+db[0]+"','"+db[1]+"')"
        else:
            List = "IN ('"+db[0]+"')"
    except: 
        # print("No data related to room name")
        result["ERROR"].append({'Message': 'No data related to room name!'})
        return result
    
    TIME_RANGE = ['HOUR','DAY','WEEK','MONTH']
    for T in TIME_RANGE: 
        sql = "SELECT COUNT(CASE WHEN IR>0 THEN 1 END) AS IR_COUNT,COUNT(CASE WHEN IB>0 THEN 1 END) AS IB_COUNT FROM (SELECT DATE_FORMAT(TIMESTAMP, '%%Y-%%m-%%d %%H:%%i') AS T, (SUM(OBJECT_LOCATION))>0 AS IR, (SUM(IN_BED))>0 AS IB FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL 1 %s) AND OBJECT_LOCATION IS NOT NULL GROUP BY T) AS T1" % (List, T)
        cursor.execute(sql)
        dbresult = cursor.fetchall() 
        # print(dbresult)
        IR,IB=dbresult[0]
        if T == 'HOUR':
            IN_ROOM_SECONDS_HOUR = IR*60
            IN_BED_SECONDS_HOUR  = IB*60
            IN_ROOM_PCT_HOUR = round(IR*100/60, 2)
            IN_BED_PCT_HOUR  = round(IB*100/60, 2)
        elif T == "DAY":
            IN_ROOM_SECONDS_DAY = IR*60
            IN_BED_SECONDS_DAY  = IB*60
            IN_ROOM_PCT_DAY = round(IR*100/1440, 2)
            IN_BED_PCT_DAY  = round(IB*100/1440, 2)
        elif T == "WEEK":
            IN_ROOM_SECONDS_WEEK = IR*60
            IN_BED_SECONDS_WEEK  = IB*60
            IN_ROOM_PCT_WEEK = round(IR*100/10080,2)
            IN_BED_PCT_WEEK  = round(IB*100/10080,2)           
        elif T == "MONTH":
            IN_ROOM_SECONDS_MONTH = IR*60
            IN_BED_SECONDS_MONTH  = IB*60
            IN_ROOM_PCT_MONTH = round(IR/432, 2)
            IN_BED_PCT_MONTH  = round(IB/432, 2)  
    result['DATA'].append({"IN_ROOM_SECONDS_HOUR": IN_ROOM_SECONDS_HOUR, "IN_BED_SECONDS_HOUR": IN_BED_SECONDS_HOUR, "IN_ROOM_PCT_HOUR": IN_ROOM_PCT_HOUR, "IN_BED_PCT_HOUR": IN_BED_PCT_HOUR, "IN_ROOM_SECONDS_DAY": IN_ROOM_SECONDS_DAY, "IN_BED_SECONDS_DAY": IN_BED_SECONDS_DAY, "IN_ROOM_PCT_DAY": IN_ROOM_PCT_DAY, "IN_BED_PCT_DAY": IN_BED_PCT_DAY, "IN_ROOM_SECONDS_WEEK": IN_ROOM_SECONDS_WEEK, "IN_BED_SECONDS_WEEK": IN_BED_SECONDS_WEEK, "IN_ROOM_PCT_WEEK": IN_ROOM_PCT_WEEK, "IN_BED_PCT_WEEK": IN_BED_PCT_WEEK, "IN_ROOM_SECONDS_MONTH": IN_ROOM_SECONDS_MONTH, "IN_BED_SECONDS_MONTH": IN_BED_SECONDS_MONTH, "IN_ROOM_PCT_MONTH": IN_ROOM_PCT_MONTH, "IN_BED_PCT_MONTH": IN_BED_PCT_MONTH})
    cursor.close()
    connection.close()
    return result

def queryHistoryAnalytic(timeRange, posture, List):
    result = {}
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND %s = 1;" %(List, timeRange, posture)
    # print(sql)
    # exit()
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    if not dbresult:
        print("No data")
        result = {'Message': 'No data!'}
    result = int(dbresult[0]*2)
    cursor.close()
    connection.close()
    return result

def _getAnalyticDataofPosture(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    sql = "SELECT * FROM SUMMARY_ANALYTIC WHERE MAC='%s'"%(data['DEVICEMAC'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()    
    result["DATA"].append({'totalCountInOutRoom': dbresult[1]})
    result["DATA"].append({'countInRoom': dbresult[2]})
    result["DATA"].append({'countInBed': dbresult[3]})

    cursor.close()
    connection.close()
    return result

def getSummaryDataofPosition(data):
    # start_time = time.time()
    N = 10 # N is the dividing factor, e.g. 10 means every meter will be divided to 10 data points
    sigma = 3
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    result["_DBG"] = []
    if not 'DEVICEMAC' in data:
        result["ERROR"].append({'Message': 'MAC is empty!'})
        return result
    t = data['TIME']
    timeRange = "10 DAY"
    if t == "HOUR":
        timeRange = "1 HOUR"
    elif t == "DAY":
        timeRange = "1 DAY"
    elif t == "WEEK":
        timeRange = "1 WEEK"
    elif t == "MONTH":
        timeRange = "1 MONTH" 
    # macString = "IN ('"+db[0]+"','"+db[1]+"')"
    sql = "SELECT ROOM_X*%d AS X_RANGE,ROOM_Y*%d AS Y_RANGE,ID FROM ROOMS_DETAILS RIGHT JOIN RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID WHERE RL_ROOM_MAC.MAC='%s';" %(N, N, data['DEVICEMAC'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()    
    X_RANGE = int(dbresult[0])
    Y_RANGE = int(dbresult[1])
    ROOM_ID = int(dbresult[2])  

    sql = "SELECT X_START, X_END, Y_START, Y_END FROM ROOMS_FILTER_AREA WHERE ROOM_ID='%s';"%(ROOM_ID)
    cursor.execute(sql)
    areas = cursor.fetchall()    
    filtering = ""
    for area in areas:
        X_START = area[0]
        X_END = area[1]
        Y_START = area[2]
        Y_END = area[3]
        if (filtering == ""):
            filtering = f" AND ((PX < {X_START} OR PX > {X_END}) AND (PY < {Y_START} OR PY > {Y_END})"
        else:
            filtering += f" AND (PX < {X_START} OR PX > {X_END}) AND (PY < {Y_START} OR PY > {Y_END})"

    if (filtering != ""):
            filtering += ")"  

    if t == "CUSTOM":
        sql = "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y,ROUND(MIN(PX),1),ROUND(MIN(PY),1) FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` BETWEEN '%s' AND '%s' AND `PX` IS NOT NULL AND PY IS NOT NULL%s;" %(data['DEVICEMAC'], data['TIMESTART'], data['TIMEEND'],filtering)
    else:
        sql = "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y,ROUND(MIN(PX),1),ROUND(MIN(PY),1) FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND PY IS NOT NULL%s;" %(data['DEVICEMAC'], timeRange,filtering)
    print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    # print(dbresult)
    if dbresult[0] == None and dbresult[1] == None:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        # print(result)
        return result
    X_SIZE = int(dbresult[0]*N)
    Y_SIZE = int(dbresult[1]*N)
    X_MIN =  int(dbresult[2]*N)
    Y_MIN =  int(dbresult[3]*N)

    HMAP = np.zeros((X_RANGE*3, Y_RANGE*3))
    if t == "CUSTOM":
        sql = "SELECT CONCAT(ROUND(PX*%d),',',ROUND(PY*%d)) AS XY,COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` BETWEEN '%s' AND '%s' AND `PX` IS NOT NULL AND `PY` IS NOT NULL%s GROUP BY XY ORDER BY XY ASC;" %(N, N, data['DEVICEMAC'], data['TIMESTART'], data['TIMEEND'],filtering)
    else:
        sql = "SELECT CONCAT(ROUND(PX*%d),',',ROUND(PY*%d)) AS XY,COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND `PY` IS NOT NULL%s GROUP BY XY ORDER BY XY ASC;" %(N, N, data['DEVICEMAC'], timeRange,filtering)
    print(sql)
    print(filtering)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    cursor.close()
    connection.close() 
    # print("second sql time: %s s"%(time.time()-start_time))
    # print(dbresult)
    # result["_DBG"]=dbresult
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'DATA': 'No Data!'})
        return result
    for row in dbresult:
        # print(row)
        X,Y = row[0].split(",")   
        CNT = int(row[1])
        
        # print(int(X), int(Y), X_SHIFT+int(X), Y_SHIFT+int(Y), CNT)
        try:
            # result["_DBG"].append([X,Y,CNT])
            HMAP[X_RANGE+int(X)][Y_RANGE+int(Y)] += CNT
        except Exception as e:
            continue
    # print(HMAP)
    # Apply Gaussian blur with a specified sigma value
    NEW_HMAP = gaussian_blur(HMAP, sigma)
    DATA = []
    MAX = np.amax(NEW_HMAP)
    for X in range(0, X_RANGE):
        for Y in range(0, Y_RANGE):
            try:
                VALUE = round(NEW_HMAP[X+X_RANGE,Y+Y_RANGE],2)
            except:
                VALUE = 0
            # result["_DBG"].append(VALUE)
            if VALUE > 0.03 * MAX:
                DATA.append([round(X, 1),round(Y, 1), VALUE])
    DATA.append([X_RANGE, Y_RANGE, 0]) 
    DATA.append([0, 0, 0]) 
    result["DATA"].append(DATA)
    result["MAX"].append(MAX)
    
    return result




def gaussian_blur(array, sigma):
    size = int(2 * np.ceil(3 * sigma) + 1)  # Determine the kernel size based on sigma
    # print("before kernel loop: %s s"%(time.time()-start_time))
    kernel = np.fromfunction(lambda x, y: (1 / (2 * np.pi * sigma ** 2)) * np.exp(
        -((x - size // 2) ** 2 + (y - size // 2) ** 2) / (2 * sigma ** 2)), (size, size))
    kernel = kernel / np.sum(kernel)  # Normalize the kernel

    blurred_array = np.zeros_like(array, dtype=float)
    # print("before padded loop: %s s"%(time.time()-start_time))
    # Pad the array to handle border pixels
    padded_array = np.pad(array, ((size // 2, size // 2), (size // 2, size // 2)), mode='constant')
    # print("before Gaussian filter loop: %s s"%(time.time()-start_time))
    # Apply the Gaussian filter
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            window = padded_array[i:i + size, j:j + size]
            blurred_array[i, j] = np.sum(window * kernel)
    # print("after Gaussian filter loop: %s s"%(time.time()-start_time))
    return blurred_array
