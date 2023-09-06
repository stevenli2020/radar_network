import mysql.connector
from user.config import config
from collections import defaultdict
import uuid
import os

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
        sql = "SELECT ROOMS_DETAILS.*, DEVICES.LAST_DATA_RECEIVED FROM Gaitmetrics.ROOMS_DETAILS JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID JOIN Gaitmetrics.DEVICES ON RL_ROOM_MAC.MAC=DEVICES.MAC GROUP BY ROOMS_DETAILS.ID"
    else:
        sql = "SELECT ROOMS_DETAILS.*, DEVICES.LAST_DATA_RECEIVED FROM Gaitmetrics.ROOMS_DETAILS JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID JOIN Gaitmetrics.DEVICES ON RL_ROOM_MAC.MAC=DEVICES.MAC RIGHT JOIN Gaitmetrics.RL_USER_ROOM ON ROOMS_DETAILS.ID=RL_USER_ROOM.ROOM_ID WHERE RL_USER_ROOM.USER_ID='%s' GROUP BY ROOMS_DETAILS.ID"%(req['ID'])
    cursor.execute(sql)
    # one device one room
    # result["DATA"] = [{"ID": ID, "ROOM_NAME": ROOM_NAME, "MAC": MAC, "ROOM_X":ROOM_X, "ROOM_Y":ROOM_Y, "RADAR_X_LOC": RADAR_X_LOC, "RADAR_Y_LOC":RADAR_Y_LOC, "IMAGE_NAME": IMAGE_NAME} for (ID, ROOM_NAME, MAC, ROOM_X, ROOM_Y, RADAR_X_LOC, RADAR_Y_LOC, IMAGE_NAME) in cursor]
    result["DATA"] = [{"ID": ID, "ROOM_LOC": ROOM_LOC, "ROOM_NAME": ROOM_NAME, "ROOM_UUID":ROOM_UUID, "IMAGE_NAME": IMAGE_NAME, "INFO": INFO, "ROOM_X":ROOM_X, "ROOM_Y":ROOM_Y, "STATUS":STATUS, "OCCUPANCY":OCCUPANCY, "LAST_DATA_TS":LAST_DATA_TS, "LAST_DATA_RECEIVED": LAST_DATA_RECEIVED} for (ID, ROOM_LOC, ROOM_NAME, ROOM_UUID, IMAGE_NAME, INFO, ROOM_X, ROOM_Y, STATUS, OCCUPANCY, LAST_DATA_TS, LAST_DATA_RECEIVED) in cursor]
    for room in result["DATA"]:
        cursor.execute(f"""SELECT `URGENCY`, COUNT(*) AS `COUNT` FROM `ALERT` WHERE `ROOM_ID`={room["ID"]} AND `NOTIFY`=0 GROUP BY `URGENCY` ORDER BY `URGENCY` DESC;""")
        room["ALERTS"] = [{"URGENCY": URGENCY, "COUNT": COUNT} for (URGENCY,COUNT ) in cursor]
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
    if data['IMAGE_NAME'] != data['O_IMAGE_NAME']:
        os.remove(os.path.join(str(uploadsLoc), str(data['O_IMAGE_NAME'])))        
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

def getRoomAlertsData(room_uuid,unread = True):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    option = ';'
    if (unread):
        option = ' AND a.`NOTIFY`=0;'
    sql = f"SELECT a.`ID`,a.`TIMESTAMP`,a.`URGENCY`,a.`TYPE`,a.`DETAILS`,a.`NOTIFY` ,a.`NOTIFY_TIMESTAMP` FROM `ALERT` a LEFT JOIN `ROOMS_DETAILS` r ON a.`ROOM_ID`=r.`ID` WHERE r.`ROOM_UUID`='{room_uuid}'" + option
    cursor.execute(sql)   
    result["DATA"] = [{"ID": ID, "TIMESTAMP": TIMESTAMP, "URGENCY":URGENCY, "TYPE":TYPE, "DETAILS":DETAILS, "NOTIFY":NOTIFY, "NOTIFY_TIMESTAMP": NOTIFY_TIMESTAMP} for (ID, TIMESTAMP,URGENCY,TYPE,DETAILS,NOTIFY,NOTIFY_TIMESTAMP) in cursor]
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