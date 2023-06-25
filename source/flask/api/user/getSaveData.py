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
    sql = "SELECT DATE_FORMAT(TIMESTAMP, \'%%Y-%%m-%%d %%H:%%i\') AS T, ROUND(AVG(HEART_RATE),1) AS HR, ROUND(AVG(BREATH_RATE),1) AS BR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s) AND HEART_RATE IS NOT NULL AND HEART_RATE !=0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE !=0 GROUP BY T ORDER BY `T` ASC;" %(List, data['TIME'])
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        return result 
    result['DATA'].append(dbresult)
    sql = "SELECT ROUND(AVG(HEART_RATE), 1) as AHR, ROUND(AVG(BREATH_RATE), 1) as ABR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND HEART_RATE > 0 AND BREATH_RATE > 0 AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s);" %(List, data['TIME'])
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
    
    # result["SQL"].append({"SQL": sql})
    for row in dbresult:
        result["DATA"].append({"TIMESTAMP": row[0], "HEART_RATE": row[1], "BREATH_RATE": row[2]})
    sql = "SELECT ROUND(AVG(HEART_RATE), 2) as HEART_RATE, ROUND(AVG(BREATH_RATE), 2) as BREATH_RATE FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND HEART_RATE > 0 AND TIMESTAMP BETWEEN NOW() - INTERVAL %s AND NOW()"%(data['DEVICEMAC'], data['TIME'])
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    result["AVG"].append(dbresult)
    cursor.close()
    connection.close()
    return result

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
    # N,U=data['TIME'].split(" ")
    # NUM = int(N)
    TOTAL_SECONDS_HOUR = 3600
    TOTAL_SECONDS_DAY = 86400
    TOTAL_SECONDS_WEEK = 604800
    TOTAL_SECONDS_MONTH = 2592000
    # if U.upper() == "DAY":
    #     TOTAL_SECONDS = NUM * 86400
    # elif U.upper() == "HOUR":
    #     TOTAL_SECONDS = NUM * 3600
    # elif U.upper() == "WEEK":
    #     TOTAL_SECONDS = NUM * 604800
    # elif U.upper() == "MONTH":
    #     TOTAL_SECONDS = NUM * 2592000
    # else:
    #     print("Time range error, exit")
    #     result["ERROR"].append({'Message': 'Time range error!'})
    #     return result
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
    # sql = "SELECT COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND OBJECT_LOCATION = 1;" %(List, data['TIME'])
    # # print(sql)
    # # exit()
    # cursor.execute(sql)
    # dbresult = cursor.fetchone() 
    # if not dbresult:
    #     print("No data")
    #     result["ERROR"].append({'Message': 'No data!'})
    #     return result
    # IN_ROOM_SECONDS = int(dbresult[0]*2)
    # sql = "SELECT COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND IN_BED = 1;" %(List, data['TIME'])
    # # print(sql)
    # cursor.execute(sql)
    # dbresult = cursor.fetchone() 
    # if not dbresult:
    #     print("No data")
    #     result["ERROR"].append({'Message': 'No data!'})
    #     return result
    #     # exit()
    # IN_BED_SECONDS = int(dbresult[0]*2)
    IN_ROOM_SECONDS_HOUR = queryHistoryAnalytic("1 HOUR", "OBJECT_LOCATION", List)
    IN_BED_SECONDS_HOUR = queryHistoryAnalytic("1 HOUR", "IN_BED", List)
    IN_ROOM_SECONDS_DAY = queryHistoryAnalytic("1 DAY", "OBJECT_LOCATION", List)
    IN_BED_SECONDS_DAY = queryHistoryAnalytic("1 DAY", "IN_BED", List)
    IN_ROOM_SECONDS_WEEK = queryHistoryAnalytic("1 WEEK", "OBJECT_LOCATION", List)
    IN_BED_SECONDS_WEEK = queryHistoryAnalytic("1 WEEK", "IN_BED", List)
    IN_ROOM_SECONDS_MONTH = queryHistoryAnalytic("1 MONTH", "OBJECT_LOCATION", List)
    IN_BED_SECONDS_MONTH = queryHistoryAnalytic("1 MONTH", "IN_BED", List)
    print(IN_ROOM_SECONDS_HOUR, IN_BED_SECONDS_HOUR)
    result['DATA'].append({"IN_ROOM_SECONDS_HOUR": IN_ROOM_SECONDS_HOUR, "IN_BED_SECONDS_HOUR": IN_BED_SECONDS_HOUR, "IN_ROOM_PCT_HOUR": round(IN_ROOM_SECONDS_HOUR*100/TOTAL_SECONDS_HOUR,2), "IN_BED_PCT_HOUR": round(IN_BED_SECONDS_HOUR*100/TOTAL_SECONDS_HOUR,2), "IN_ROOM_SECONDS_DAY": IN_ROOM_SECONDS_DAY, "IN_BED_SECONDS_DAY": IN_BED_SECONDS_DAY, "IN_ROOM_PCT_DAY": round(IN_ROOM_SECONDS_DAY*100/TOTAL_SECONDS_DAY,2), "IN_BED_PCT_DAY": round(IN_BED_SECONDS_DAY*100/TOTAL_SECONDS_DAY,2), "IN_ROOM_SECONDS_WEEK": IN_ROOM_SECONDS_WEEK, "IN_BED_SECONDS_WEEK": IN_BED_SECONDS_WEEK, "IN_ROOM_PCT_WEEK": round(IN_ROOM_SECONDS_WEEK*100/TOTAL_SECONDS_WEEK,2), "IN_BED_PCT_WEEK": round(IN_BED_SECONDS_WEEK*100/TOTAL_SECONDS_WEEK,2), "IN_ROOM_SECONDS_MONTH": IN_ROOM_SECONDS_MONTH, "IN_BED_SECONDS_MONTH": IN_BED_SECONDS_MONTH, "IN_ROOM_PCT_MONTH": round(IN_ROOM_SECONDS_MONTH*100/TOTAL_SECONDS_MONTH,2), "IN_BED_PCT_MONTH": round(IN_BED_SECONDS_MONTH*100/TOTAL_SECONDS_MONTH,2)})

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
    else:
        timeRange = "1 MONTH"
    sql = "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND PY IS NOT NULL;" %(data['DEVICEMAC'], timeRange)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    # print(dbresult)
    # print("first sql time: %s s"%(time.time()-start_time))
    if dbresult[0] == None and dbresult[1] == None:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        # print(result)
        return result
    X_SHIFT = int(dbresult[0]*N)
    X_SIZE = int(dbresult[0]*N)*4
    Y_SHIFT = int(dbresult[1]*N)
    Y_SIZE = int(dbresult[1]*N)*4

    HMAP = np.zeros((X_SIZE, Y_SIZE))
    HMAP2 = np.zeros((X_SHIFT, X_SHIFT))
        

    sql = "SELECT CONCAT(ROUND(PX*%d),',',ROUND(PY*%d)) AS XY,COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND `PY` IS NOT NULL GROUP BY XY ORDER BY XY ASC;" %(N, N, data['DEVICEMAC'], timeRange)
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    cursor.close()
    connection.close() 
    # print("second sql time: %s s"%(time.time()-start_time))
    print(dbresult)
    
    sample = []
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'DATA': 'No Data!'})
        return result
    for row in dbresult:
        # print(row)
        X,Y = row[0].split(",")   
        CNT = int(row[1])
        # print(int(X), int(Y), X_SHIFT+int(X), Y_SHIFT+int(Y), CNT)
        sample.append([int(X), int(Y), int(row[1])])
        try:
            HMAP[X_SHIFT+int(X)][Y_SHIFT+int(Y)] += CNT
        except:
            continue
    result["SAMPLE"].append(sample)
    # print(HMAP)
    # Apply Gaussian blur with a specified sigma value

    NEW_HMAP = gaussian_blur(HMAP, sigma)
    # print("after gaussian time: %s s"%(time.time()-start_time))
    # print("\nOriginal HMAP:")
    # print(HMAP)
    # print("\nBlurred HMAP:")
    # print(NEW_HMAP)
    # print("MAX VALUE: %f" %(np.max(NEW_HMAP)))

    # print("\nShifted HMAP:")
    HMAP2 = NEW_HMAP[X_SHIFT:X_SHIFT*2,Y_SHIFT:Y_SHIFT*2]
    # print(HMAP2)

    DATA = []
    # print("\nUnpack data:")
    # print("before loop: %s s"%(time.time()-start_time))
    for X in range(0, X_SHIFT-1):
        for Y in range(0, Y_SHIFT-1):
            DATA.append([round(X, 1),round(Y, 1), round(HMAP2[X,Y],2)])
    # print("after loop: %s s"%(time.time()-start_time))
    print("\nfinal output: " +str(DATA)+"\n")           
    result["DATA"].append(DATA)
    result["DEBUG"].append([X_SHIFT-1, Y_SHIFT-1])
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
