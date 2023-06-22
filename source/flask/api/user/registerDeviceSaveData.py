import mysql.connector
from user.config import config
from datetime import datetime, timedelta

config = config()


def registerDeviceSaveRaw(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    now = datetime.now()
    if data['DEVICEMAC'] and data['TIME'] != 'please select':
        if(data['CUSTOM'] == 0):  
            sql = "SELECT * FROM RL_DEVICE_SAVE WHERE MAC='%s'"%(data['DEVICEMAC'])
            ti = now
            if 'day' in data["TIME"]:
                ti = now + timedelta(days=1)
            elif 'week' in data["TIME"]:
                ti = now + timedelta(weeks=1)
            else:
                ti = now + timedelta(weeks=4)
            cursor.execute(sql)
            dbresult = cursor.fetchall()
            if dbresult:
                for x in dbresult:
                    print(x, x[3]<now)
                    if x[3] < now:
                        cursor.execute("INSERT INTO RL_DEVICE_SAVE (MAC, Expired) VALUES (%s, %s)", (data['DEVICEMAC'], ti))
                        connection.commit()
                        result["DATA"] = [{"MESSAGE": "Device "+data['DEVICEMAC']+" registered succefully"}]
                    elif x[3] > now:
                        result["ERROR"] = [{"MAC": data['DEVICEMAC']+" already saving data from "+str(x[2])+" to "+str(x[3])}]
            else:
                cursor.execute("INSERT INTO RL_DEVICE_SAVE (MAC, Expired) VALUES (%s, %s)", (data['DEVICEMAC'], ti))
                result["DATA"] = [{"MESSAGE": "Device "+data['DEVICEMAC']+" registered succefully"}]
                connection.commit()
        else:
            sql = "SELECT * FROM RL_DEVICE_SAVE WHERE MAC='%s'"%(data['DEVICEMAC'])
            ts = data['TIME'].split('-')
            cursor.execute(sql)
            dbresult = cursor.fetchall()
            if dbresult:
                for x in dbresult:                    
                    if x[3] < now:
                        cursor.execute("INSERT INTO RL_DEVICE_SAVE (MAC, Start, Expired) VALUES (%s, %s, %s)", (data['DEVICEMAC'], ts[0], ts[1]))
                        connection.commit()
                        result["DATA"] = [{"MESSAGE": "Device "+data['DEVICEMAC']+" registered succefully"}]
                    elif x[3] > now:
                        result["ERROR"] = [{"MAC": data['DEVICEMAC']+" already saving data from "+str(x[2])+" to "+str(x[3])}]
            else:
                cursor.execute("INSERT INTO RL_DEVICE_SAVE (MAC, Start, Expired) VALUES (%s, %s, %s)", (data['DEVICEMAC'], ts[0], ts[1]))
                result["DATA"] = [{"MESSAGE": "Device "+data['DEVICEMAC']+" registered succefully"}]
                connection.commit()
    elif data['TIME'] == "please select":
        result['ERROR'] = [{"CODE": 0, "TIME": "Please select Time"}]
    else:
        result['ERROR'] = [{"CODE": 0, "MAC": "MAC is Empty"}]
    cursor.close()
    connection.close()
    return result