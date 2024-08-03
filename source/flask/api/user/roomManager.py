import mysql.connector
from user.config import config
from collections import defaultdict
import uuid
import os
import pytz
from tzlocal import get_localzone

config = config()

def searchRoomDetail(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    sql = "SELECT ROOM_NAME, ROOM_UUID FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_NAME LIKE CONCAT('%', %s, '%')"
    cursor.execute(sql, (data['VALUE'],))   
    result["DATA"] = [{"ROOM_NAME": ROOM_NAME, "ROOM_UUID": ROOM_UUID} for (ROOM_NAME, ROOM_UUID) in cursor]
    cursor.close()
    connection.close()
    return result

def getRoomData(req, admin):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    # one device one room
    # sql = "SELECT * FROM ROOMS_DETAILS WHERE MAC='%s'"%(req['MAC'])
    sql = ''
    if admin:
        sql = "SELECT ROOMS_DETAILS.*, LATEST_DEVICES.LAST_DATA_RECEIVED, ROOMS_ON_MAP.x, ROOMS_ON_MAP.y, ROOMS_ON_MAP.w, ROOMS_ON_MAP.h, GROUP_CONCAT(RL_ROOM_MAC.MAC) AS MAC FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID LEFT JOIN (SELECT d.MAC, rrm.ROOM_UUID, max_date.LAST_DATA_RECEIVED FROM Gaitmetrics.DEVICES d LEFT JOIN Gaitmetrics.RL_ROOM_MAC rrm ON rrm.MAC = d.MAC INNER JOIN (SELECT rrm_inner.ROOM_UUID, MAX(d_inner.LAST_DATA_RECEIVED) AS LAST_DATA_RECEIVED FROM Gaitmetrics.DEVICES d_inner LEFT JOIN Gaitmetrics.RL_ROOM_MAC rrm_inner ON rrm_inner.MAC = d_inner.MAC GROUP BY rrm_inner.ROOM_UUID) max_date ON rrm.ROOM_UUID = max_date.ROOM_UUID ORDER BY `rrm`.`ROOM_UUID` ASC) AS LATEST_DEVICES ON RL_ROOM_MAC.MAC = LATEST_DEVICES.MAC LEFT JOIN Gaitmetrics.ROOMS_ON_MAP ON ROOMS_DETAILS.ID=ROOMS_ON_MAP.ID GROUP BY ROOMS_DETAILS.ID"
    else:
        sql = "SELECT ROOMS_DETAILS.*, LATEST_DEVICES.LAST_DATA_RECEIVED, ROOMS_ON_MAP.x, ROOMS_ON_MAP.y, ROOMS_ON_MAP.w, ROOMS_ON_MAP.h, GROUP_CONCAT(RL_ROOM_MAC.MAC) AS MAC FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID LEFT JOIN (SELECT d.MAC, rrm.ROOM_UUID, max_date.LAST_DATA_RECEIVED FROM Gaitmetrics.DEVICES d LEFT JOIN Gaitmetrics.RL_ROOM_MAC rrm ON rrm.MAC = d.MAC INNER JOIN (SELECT rrm_inner.ROOM_UUID, MAX(d_inner.LAST_DATA_RECEIVED) AS LAST_DATA_RECEIVED FROM Gaitmetrics.DEVICES d_inner LEFT JOIN Gaitmetrics.RL_ROOM_MAC rrm_inner ON rrm_inner.MAC = d_inner.MAC GROUP BY rrm_inner.ROOM_UUID) max_date ON rrm.ROOM_UUID = max_date.ROOM_UUID ORDER BY `rrm`.`ROOM_UUID` ASC) AS LATEST_DEVICES ON RL_ROOM_MAC.MAC = LATEST_DEVICES.MAC LEFT JOIN Gaitmetrics.ROOMS_ON_MAP ON ROOMS_DETAILS.ID=ROOMS_ON_MAP.ID RIGHT JOIN Gaitmetrics.RL_USER_ROOM ON ROOMS_DETAILS.ID=RL_USER_ROOM.ROOM_ID WHERE RL_USER_ROOM.USER_ID='%s' GROUP BY ROOMS_DETAILS.ID"%(req['ID'])
    cursor.execute(sql)
    # one device one room
    
    # Get the local timezone
    local_timezone = get_localzone()
    # result["DATA"] = [{"ID": ID, "ROOM_NAME": ROOM_NAME, "MAC": MAC, "ROOM_X":ROOM_X, "ROOM_Y":ROOM_Y, "RADAR_X_LOC": RADAR_X_LOC, "RADAR_Y_LOC":RADAR_Y_LOC, "IMAGE_NAME": IMAGE_NAME} for (ID, ROOM_NAME, MAC, ROOM_X, ROOM_Y, RADAR_X_LOC, RADAR_Y_LOC, IMAGE_NAME) in cursor]
    result["DATA"] = [{"ID": ID, "ROOM_LOC": ROOM_LOC, "ROOM_NAME": ROOM_NAME, "ROOM_UUID":ROOM_UUID, "IMAGE_NAME": IMAGE_NAME, "INFO": INFO, "ROOM_X":ROOM_X, "ROOM_Y":ROOM_Y, "STATUS":STATUS, "OCCUPANCY":OCCUPANCY, "LAST_DATA_TS":LAST_DATA_TS.astimezone(local_timezone).astimezone(pytz.utc) if LAST_DATA_TS else LAST_DATA_TS, "LAST_DATA_RECEIVED": LAST_DATA_RECEIVED.astimezone(local_timezone).astimezone(pytz.utc) if LAST_DATA_RECEIVED else LAST_DATA_RECEIVED, "x":x, "y":y, "w":w, "h":h,"MAC":MAC.split(",") if MAC else []} for (ID, ROOM_LOC, ROOM_NAME, ROOM_UUID, IMAGE_NAME, INFO, ROOM_X, ROOM_Y, STATUS, OCCUPANCY, LAST_DATA_TS, LAST_DATA_RECEIVED,x,y,w,h,MAC) in cursor]
    for room in result["DATA"]:
        cursor.execute(f"""SELECT `ID`,`TIMESTAMP`,`URGENCY`,`TYPE`,`DETAILS`,`NOTIFY` ,`NOTIFY_TIMESTAMP` FROM `ALERT` WHERE `ROOM_ID`={room["ID"]} AND `NOTIFY`=0 GROUP BY `URGENCY` ORDER BY `URGENCY` DESC;""")
        room["ALERTS"] = [{"ID":ID,"TIMESTAMP":TIMESTAMP.astimezone(local_timezone).astimezone(pytz.utc) if TIMESTAMP else TIMESTAMP,"URGENCY": URGENCY, "TYPE": TYPE,"DETAILS":DETAILS,"NOTIFY":NOTIFY,"NOTIFY_TIMESTAMP":NOTIFY_TIMESTAMP.astimezone(local_timezone).astimezone(pytz.utc) if NOTIFY_TIMESTAMP else NOTIFY_TIMESTAMP} for (ID,TIMESTAMP,URGENCY,TYPE,DETAILS,NOTIFY,NOTIFY_TIMESTAMP ) in cursor]
        
    cursor.close()
    connection.close()
    return result

def getSpecificRoomData(req, admin):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    # one device one room
    # sql = "SELECT * FROM ROOMS_DETAILS WHERE MAC='%s'"%(req['MAC'])
    sql = "SELECT ID, ROOM_LOC, ROOM_NAME, ROOM_UUID, IMAGE_NAME, INFO, ROOM_X, ROOM_Y FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s'"%(req['ROOM_UUID'])
    # if 'DETAIL_PAGE' in req:
    #     sql = "SELECT ROOMS_DETAILS.ID, ROOM_LOC, ROOM_NAME, ROOMS_DETAILS.ROOM_UUID, IMAGE_NAME, INFO, ROOM_X, ROOM_Y, DEVICES.MAC, DEVICES.TYPE FROM Gaitmetrics.ROOMS_DETAILS RIGHT JOIN Gaitmetrics.RL_ROOM_MAC ON Gaitmetrics.ROOMS_DETAILS.ROOM_UUID=Gaitmetrics.RL_ROOM_MAC.ROOM_UUID RIGHT JOIN Gaitmetrics.DEVICES ON Gaitmetrics.RL_ROOM_MAC.MAC=Gaitmetrics.DEVICES.MAC WHERE Gaitmetrics.ROOMS_DETAILS.ROOM_UUID='%s'"%(req['ROOM_UUID'])
    # if admin:
    #     sql = "SELECT * FROM ROOMS_DETAILS"
    # else:
    #     sql = ''
    cursor.execute(sql)
    # dbresult = cursor.fetchone()
    # if dbresult:
    #     result["DATA"] = dbresult
    # else:
    #     result["ERROR"] = "Room Not Found"
    result["DATA"] = [{"ID": ID, "ROOM_LOC": ROOM_LOC, "ROOM_NAME": ROOM_NAME, "ROOM_UUID": ROOM_UUID, "IMAGE_NAME": IMAGE_NAME, "INFO": INFO, "ROOM_X":ROOM_X, "ROOM_Y":ROOM_Y} for (ID, ROOM_LOC, ROOM_NAME, ROOM_UUID, IMAGE_NAME, INFO, ROOM_X, ROOM_Y) in cursor]
    cursor.close()
    connection.close()
    return result


def addNewRoomDetail(data):
    result = defaultdict(list)      
    # MAC = data['MAC']
    # print(MAC)
    # print(type(MAC))
    if data['ROOM_NAME'] == '':
        result['ERROR'].append({'ROOM_NAME': 'Room name is Empty!'})
    else:
        if data['ROOM_X'] == '':
            result['ERROR'].append({'ROOM_X': 'Please add value!'})
        if data['ROOM_Y'] == '':
            result['ERROR'].append({'ROOM_Y': 'Please add value!'})
    if data['ROOM_X'] != "" or data['ROOM_Y'] != "":
        if data['ROOM_NAME'] == '':
            result['ERROR'].append({'ROOM_NAME': 'Room name is Empty!'})
    # if data['IMAGE_NAME'] == '':
    #     result['ERROR'].append({'IMAGE_NAME': 'Please upload room image!'})
    if data['ROOM_LOC'] == "":
        result['ERROR'].append({'ROOM_LOC': 'Room location is Empty!'})
    if len(result['ERROR']):
        return result
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    UID = uuid.uuid4().hex
    sql = "SELECT * FROM ROOMS_DETAILS WHERE ROOM_NAME='%s'"%(data['ROOM_NAME'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    if dbresult:
        result['ERROR'].append({'ROOM_NAME': 'Room name is taken'})
        return result
    sql = "SELECT ROOM_UUID FROM ROOMS_DETAILS"
    cursor.execute(sql)
    dbresult = cursor.fetchall()
    if dbresult:
        for x in dbresult:
            if x[0]==UID:
                UID = uuid.uuid4().hex
    cursor.execute("INSERT INTO Gaitmetrics.ROOMS_DETAILS (ROOM_LOC, ROOM_NAME, ROOM_UUID, IMAGE_NAME, INFO, ROOM_X, ROOM_Y) VALUES(%s, %s, %s, %s, %s, %s, %s)", (data['ROOM_LOC'], data['ROOM_NAME'], UID, data['IMAGE_NAME'], data["INFO"], data['ROOM_X'], data['ROOM_Y']))
    connection.commit()
    
    cursor.close()
    connection.close()
    result['DATA'].append({"CODE": 0})
    return result


def updateRoomDetail(data, uploadsLoc):
    result = defaultdict(list)      
    # MAC = data['MAC']
    # print(MAC)
    # print(type(MAC))
    if data['ROOM_NAME'] == '':
        result['ERROR'].append({'ROOM_NAME': 'Room name is Empty!'})
    else:
        if data['ROOM_X'] == '':
            result['ERROR'].append({'ROOM_X': 'Please add value!'})
        if data['ROOM_Y'] == '':
            result['ERROR'].append({'ROOM_Y': 'Please add value!'})
    if data['ROOM_X'] != "" or data['ROOM_Y'] != "":
        if data['ROOM_NAME'] == '':
            result['ERROR'].append({'ROOM_NAME': 'Room name is Empty!'})
    # if data['IMAGE_NAME'] == '':
    #     result['ERROR'].append({'IMAGE_NAME': 'Please upload room image!'})
    if data['ROOM_LOC'] == "":
        result['ERROR'].append({'ROOM_LOC': 'Room location is Empty!'})
    if len(result['ERROR']):
        return result
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "UPDATE Gaitmetrics.ROOMS_DETAILS SET ROOM_LOC='%s', ROOM_NAME='%s', IMAGE_NAME='%s', INFO='%s', ROOM_X='%s', ROOM_Y='%s' WHERE ROOM_UUID='%s'"%(data['ROOM_LOC'], data['ROOM_NAME'], data['IMAGE_NAME'], data['INFO'], data['ROOM_X'], data['ROOM_Y'], data['ROOM_UUID'])
    try:
        if data['IMAGE_NAME'] != data['O_IMAGE_NAME']:
            os.remove(os.path.join(str(uploadsLoc), str(data['O_IMAGE_NAME'])))
    except Exception as e:
        print(e)    
    cursor.execute(sql)
    connection.commit()    
    cursor.close()
    connection.close()
    result['DATA'].append({"CODE": 0})
    return result

def deleteRoomDetail(data, uploadsLoc):
    result = defaultdict(list)      
    # MAC = data['MAC']
    # print(MAC)
    # print(type(MAC))
    if data['ROOM_UUID'] == '':
        result['ERROR'].append({'ROOM_UUID': 'Room uuid is Empty!'})
    if data['IMAGE_NAME'] == '':
        result['ERROR'].append({'IMAGE_NAME': 'Image name is Empty!'})
    if len(result['ERROR']):
        return result
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT * FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s'"%(data['ROOM_UUID'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    if not dbresult:
        result['ERROR'].append({'ROOM_NAME': 'Room name is not found!'})
        return result
    sql = "DELETE FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s'"%(data['ROOM_UUID'])
    os.remove(os.path.join(str(uploadsLoc), str(data['IMAGE_NAME'])))        
    cursor.execute(sql)
    connection.commit()    
    cursor.close()
    connection.close()
    result['DATA'].append({"CODE": 0})
    return result

def getRoomAlertsData(room_uuid,unread = True,set=True):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    option = ' ORDER BY a.`TIMESTAMP` DESC;'
    if (unread):
        option = ' AND a.`NOTIFY`=0 ORDER BY a.`TIMESTAMP` DESC;'
    sql = f"SELECT a.`ID`,a.`TIMESTAMP`,a.`URGENCY`,a.`TYPE`,a.`DETAILS`,a.`NOTIFY` ,a.`NOTIFY_TIMESTAMP` FROM `ALERT` a LEFT JOIN `ROOMS_DETAILS` r ON a.`ROOM_ID`=r.`ID` WHERE r.`ROOM_UUID`='{room_uuid}'" + option
    cursor.execute(sql)   
    local_timezone = get_localzone()
    result["DATA"] = [{"ID": ID, "TIMESTAMP": TIMESTAMP.astimezone(local_timezone).astimezone(pytz.utc) if TIMESTAMP else TIMESTAMP, "URGENCY":URGENCY, "TYPE":TYPE, "DETAILS":DETAILS, "NOTIFY":NOTIFY, "NOTIFY_TIMESTAMP": NOTIFY_TIMESTAMP.astimezone(local_timezone).astimezone(pytz.utc) if NOTIFY_TIMESTAMP else NOTIFY_TIMESTAMP} for (ID, TIMESTAMP,URGENCY,TYPE,DETAILS,NOTIFY,NOTIFY_TIMESTAMP) in cursor]
    
    if set:
        for d in result["DATA"]:
            id = d["ID"]
            notify = d["NOTIFY"]
            if notify == 0:
                sql = f"UPDATE `ALERT` SET `NOTIFY`=1,`NOTIFY_TIMESTAMP`=NOW() WHERE `ID`={id}"
                cursor.execute(sql)  
                connection.commit() 
    cursor.close()
    connection.close()
    return result

def getRoomsAlerts(MAC,unread=True):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    option = ' ORDER BY a.`TIMESTAMP` DESC;'
    if (unread):
        option = ' AND a.`NOTIFY`=0 ORDER BY a.`TIMESTAMP` DESC;'

    sql = f"SELECT a.`ID`,a.`TIMESTAMP`,a.`URGENCY`,a.`TYPE`,a.`DETAILS`,a.`NOTIFY` ,a.`NOTIFY_TIMESTAMP` FROM `ALERT` a LEFT JOIN `ROOMS_DETAILS` r ON a.`ROOM_ID`=r.`ID` LEFT JOIN `RL_ROOM_MAC` rm ON r.`ROOM_UUID`=rm.`ROOM_UUID` WHERE a.URGENCY=3 AND rm.`MAC`='{MAC}'" + option
    cursor.execute(sql)   
    local_timezone = get_localzone()
    result["DATA"] = [{"ID": ID, "TIMESTAMP": TIMESTAMP.astimezone(local_timezone).astimezone(pytz.utc) if TIMESTAMP else TIMESTAMP, "URGENCY":URGENCY, "TYPE":TYPE, "DETAILS":DETAILS, "NOTIFY":NOTIFY, "NOTIFY_TIMESTAMP": NOTIFY_TIMESTAMP.astimezone(local_timezone).astimezone(pytz.utc) if NOTIFY_TIMESTAMP else NOTIFY_TIMESTAMP} for (ID, TIMESTAMP,URGENCY,TYPE,DETAILS,NOTIFY,NOTIFY_TIMESTAMP) in cursor]

    cursor.close()
    connection.close()
    return result

def readRoomAlertsData(alerts):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        alerts = tuple(alerts)
        sql = f"UPDATE `ALERT` SET `NOTIFY`=1,`NOTIFY_TIMESTAMP`=NOW() WHERE `ID` IN {alerts}"
        cursor.execute(sql)  
        connection.commit() 
        cursor.close()
        connection.close()
        return {
            "RESULT": True
        }
    except Exception as e:
        print(e)
        return {
            "RESULT": False
        }
    
def getFilterLocationHistoryData(room_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)

    sql = f"SELECT X_START,X_END,Y_START,Y_END FROM `ROOMS_FILTER_AREA` WHERE `ROOM_ID`='{room_id}'"
    print(sql)
    cursor.execute(sql)   
    result["DATA"] = [{"X_START":X_START, "X_END":X_END, "Y_START":Y_START, "Y_END":Y_END} for (X_START,X_END,Y_START,Y_END) in cursor]
    
    cursor.close()
    connection.close()
    print("Result",result)
    return result

def updateFilterLocationHistoryData(room_id,data):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        result = defaultdict(list)
        print(result)
        sql = f"DELETE FROM `ROOMS_FILTER_AREA` WHERE `ROOM_ID`='{room_id}'"
        cursor.execute(sql)   
        connection.commit() 
        print(sql)
        
        for row in data:
            sql = f"""INSERT INTO `ROOMS_FILTER_AREA` (ROOM_ID,X_START,X_END,Y_START,Y_END) VALUES ('{room_id}','{row["X_START"]}','{row["X_END"]}','{row["Y_START"]}','{row["Y_END"]}');"""
            cursor.execute(sql)   
            connection.commit() 
            print(sql)
        cursor.close()
        connection.close()
        return {
            "RESULT": True
        }
    except Exception as e:
        print(e)
        return {
            "RESULT": False
        }
    
def updateRoomLocationOnMapData(data):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        result = defaultdict(list)
        print(result)
        sql = f"DELETE FROM `ROOMS_ON_MAP`;"
        cursor.execute(sql)   
        connection.commit() 
        print(sql)
        
        for row in data:
            sql = f"""INSERT INTO `ROOMS_ON_MAP` (ID,x,y,w,h) VALUES ({row["ID"]},'{row["x"]}','{row["y"]}','{row["w"]}','{row["h"]}');"""
            cursor.execute(sql)   
            connection.commit() 
            print(sql)
        cursor.close()
        connection.close()
        return {
            "RESULT": True
        }
    except Exception as e:
        print(e)
        return {
            "ERROR":str(e),
            "RESULT": False
        }

def getDeviceConfig(MAC):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)

    sql = f"SELECT CONFIG_SWITCH FROM `DEVICES` WHERE MAC='{MAC}'"
    cursor.execute(sql)
    flag = 0
    for (CONFIG_SWITCH) in cursor.fetchall():
        flag = CONFIG_SWITCH[0]

    if flag:
        result["DATA"] = [{
            "DETAILS":"CONFIG"
            }]
    else:
        result["DATA"] = []
    cursor.close()
    connection.close()
    return result

def setDeviceConfig(MAC,flag):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        result = defaultdict(list)
        print(result)
        sql = f"UPDATE DEVICES SET CONFIG_SWITCH={flag} WHERE MAC='{MAC}';"
        cursor.execute(sql)   
        connection.commit() 
        return {
            "RESULT": True
        }
    except Exception as e:
        print(e)
        return {
            "ERROR":str(e),
            "RESULT": False
        }