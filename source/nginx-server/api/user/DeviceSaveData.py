import mysql.connector
from user.config import config
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone

config = config()

def getDeviceListsOfStatus():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    local_timezone = get_localzone()
    sql = "SELECT DEVICE_STATUS.MAC, STATUS, TIMESTAMP, NAME FROM DEVICE_STATUS JOIN DEVICES ON DEVICE_STATUS.MAC=DEVICES.MAC"
    cursor.execute(sql)
    result["DATA"] = [{"MAC": MAC, "STATUS": STATUS, "TIMESTAMP": TIMESTAMP.astimezone(local_timezone).astimezone(pytz.utc) if TIMESTAMP else TIMESTAMP, "NAME": NAME} for (MAC, STATUS, TIMESTAMP, NAME) in cursor]
    cursor.close()
    connection.close()
    return result

def getDeviceListsOfSaveRawData():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    sql = "SELECT * FROM RL_DEVICE_SAVE"
    cursor.execute(sql)
    result["DATA"] = [{"Id": Id, "MAC": MAC, "Start": Start, "Expired": Expired} for (Id, MAC, Start, Expired) in cursor]
    cursor.close()
    connection.close()
    return result

def getSaveDeviceDetail(req):
    id = req['Id']
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    sql = "SELECT * FROM RL_DEVICE_SAVE WHERE Id='%s'"%(id)
    cursor.execute(sql)
    print(cursor)
    result["DATA"] = [{"Id": Id, "MAC": MAC, "Start": Start, "Expired": Expired} for (Id, MAC, Start, Expired) in cursor]
    cursor.close()
    connection.close()
    return result

def updateSaveDeviceDataTime(req):
    id = req['Id']
    mac = req['MAC']
    time = req['TIME']
    time = time.split('-')
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    sql = "UPDATE RL_DEVICE_SAVE SET Start='%s', Expired='%s', MAC='%s' WHERE Id='%s'"%(time[0],time[1],mac,id)
    cursor.execute(sql)
    connection.commit()
    result["CODE"] = 0
    cursor.close()
    connection.close()
    return result

def deleteSaveDeviceDataTime(req):
    id = req['Id']
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    sql = "DELETE FROM RL_DEVICE_SAVE WHERE Id='%s'"%(id)
    cursor.execute(sql)
    connection.commit()
    result["CODE"] = 0
    cursor.close()
    connection.close()
    return result

