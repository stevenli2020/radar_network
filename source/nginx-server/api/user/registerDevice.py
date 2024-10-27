import mysql.connector
from user.config import config, vernemq
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
import pytz
from tzlocal import get_localzone

config = config()
vernemq_db = vernemq()
MQTT_GRP = "GMT"


def getRLMacRoomData(req):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    sql = (
        "SELECT RL_ROOM_MAC.MAC, DEVICES.TYPE, DEVICES.DEPLOY_X, DEVICES.DEPLOY_Y FROM Gaitmetrics.RL_ROOM_MAC JOIN Gaitmetrics.DEVICES ON Gaitmetrics.DEVICES.MAC=Gaitmetrics.RL_ROOM_MAC.MAC WHERE Gaitmetrics.RL_ROOM_MAC.ROOM_UUID='%s'"
        % (req["ROOM_UUID"])
    )
    cursor.execute(sql)
    result["DATA"] = [
        {"MAC": MAC, "TYPE": TYPE, "DEPLOY_X": DEPLOY_X, "DEPLOY_Y": DEPLOY_Y}
        for (MAC, TYPE, DEPLOY_X, DEPLOY_Y) in cursor
    ]

    cursor.close()
    connection.close()
    return result


def getregisterDeviceLists(req, admin):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    local_timezone = get_localzone()
    if admin:
        sql = "SELECT DEVICES.Id, DEVICES.MAC, NAME, TYPE, DEVICES.STATUS, DEPLOY_X, DEPLOY_Y, DEPLOY_Z, ROT_X, ROT_Y, ROT_Z, LAST_DATA_RECEIVED, DESCRIPTION, ROOMS_DETAILS.ROOM_NAME, DEVICES.CONFIG_SWITCH FROM Gaitmetrics.DEVICES LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON Gaitmetrics.DEVICES.MAC=Gaitmetrics.RL_ROOM_MAC.MAC LEFT JOIN Gaitmetrics.ROOMS_DETAILS ON Gaitmetrics.RL_ROOM_MAC.ROOM_UUID=Gaitmetrics.ROOMS_DETAILS.ROOM_UUID GROUP BY DEVICES.Id ORDER BY DEVICES.STATUS,ROOMS_DETAILS.ROOM_NAME"
        cursor.execute(sql)
        result["DATA"] = [
            {
                "Id": Id,
                "MAC": MAC,
                "NAME": NAME,
                "TYPE": TYPE,
                "STATUS": STATUS,
                "DEPLOY_X": DEPLOY_X,
                "DEPLOY_Y": DEPLOY_Y,
                "DEPLOY_Z": DEPLOY_Z,
                "ROT_X": ROT_X,
                "ROT_Y": ROT_Y,
                "ROT_Z": ROT_Z,
                "LAST DATA": (
                    LAST_DATA_RECEIVED.astimezone(local_timezone).astimezone(pytz.utc)
                    if LAST_DATA_RECEIVED
                    else LAST_DATA_RECEIVED
                ),
                "DESCRIPTION": DESCRIPTION,
                "ROOM_NAME": ROOM_NAME,
                "CONFIG_SWITCH": CONFIG_SWITCH,
            }
            for (
                Id,
                MAC,
                NAME,
                TYPE,
                STATUS,
                DEPLOY_X,
                DEPLOY_Y,
                DEPLOY_Z,
                ROT_X,
                ROT_Y,
                ROT_Z,
                LAST_DATA_RECEIVED,
                DESCRIPTION,
                ROOM_NAME,
                CONFIG_SWITCH,
            ) in cursor
        ]
    else:
        sql = "SELECT * FROM RL_USER_MAC WHERE USER_ID='%s'" % (req["ID"])
        cursor.execute(sql)
        result["DATA"] = [{"USER_ID": USER_ID, "MAC": MAC} for (USER_ID, MAC) in cursor]
    cursor.close()
    connection.close()
    return result


def getregisterDevice(req):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    if not "MAC" in req:
        sql = (
            "SELECT DEVICES.Id, DEVICES.MAC, NAME, TYPE, DEVICES.STATUS, DEPLOY_X, DEPLOY_Y, DEPLOY_Z, ROT_X, ROT_Y, ROT_Z, LAST_MODIFIED_TIME, DESCRIPTION, ROOMS_DETAILS.ROOM_NAME, ROOMS_DETAILS.ROOM_UUID FROM Gaitmetrics.DEVICES LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON Gaitmetrics.DEVICES.MAC=Gaitmetrics.RL_ROOM_MAC.MAC LEFT JOIN Gaitmetrics.ROOMS_DETAILS ON Gaitmetrics.RL_ROOM_MAC.ROOM_UUID=Gaitmetrics.ROOMS_DETAILS.ROOM_UUID WHERE DEVICES.Id='%s'"
            % (req["Id"])
        )
        cursor.execute(sql)
        result["DATA"] = [
            {
                "Id": Id,
                "MAC": MAC,
                "NAME": NAME,
                "TYPE": TYPE,
                "STATUS": STATUS,
                "DEPLOY_X": DEPLOY_X,
                "DEPLOY_Y": DEPLOY_Y,
                "DEPLOY_Z": DEPLOY_Z,
                "ROT_X": ROT_X,
                "ROT_Y": ROT_Y,
                "ROT_Z": ROT_Z,
                "LAST MODIFIED TIME": LAST_MODIFIED_TIME,
                "DESCRIPTION": DESCRIPTION,
                "ROOM_NAME": ROOM_NAME,
                "ROOM_UUID": ROOM_UUID,
            }
            for (
                Id,
                MAC,
                NAME,
                TYPE,
                STATUS,
                DEPLOY_X,
                DEPLOY_Y,
                DEPLOY_Z,
                ROT_X,
                ROT_Y,
                ROT_Z,
                LAST_MODIFIED_TIME,
                DESCRIPTION,
                ROOM_NAME,
                ROOM_UUID,
            ) in cursor
        ]
    else:
        sql = (
            "SELECT DEVICES.Id, DEVICES.MAC, NAME, LAST_MODIFIED_TIME, DESCRIPTION, STATUS, TIMESTAMP FROM DEVICES JOIN DEVICE_STATUS ON DEVICES.MAC=DEVICE_STATUS.MAC WHERE DEVICES.MAC='%s'"
            % (req["MAC"])
        )
        cursor.execute(sql)
        result["DATA"] = [
            {
                "Id": Id,
                "MAC": MAC,
                "NAME": NAME,
                "LAST_MODIFIED_TIME": LAST_MODIFIED_TIME,
                "DESCRIPTION": DESCRIPTION,
                "STATUS": STATUS,
                "TIMESTAMP": TIMESTAMP,
            }
            for (
                Id,
                MAC,
                NAME,
                LAST_MODIFIED_TIME,
                DESCRIPTION,
                STATUS,
                TIMESTAMP,
            ) in cursor
        ]
    cursor.close()
    connection.close()
    return result


def registerNewDevice(req):
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    if req["MAC"] == "":
        result["ERROR"].append({"MAC": "MAC Address is Empty!"})
    if req["NAME"] == "":
        result["ERROR"].append({"NAME": "Device Name is Empty!"})
    elif "'" in req["NAME"]:
        result["ERROR"].append({"NAME": "' is not allowed"})
    if req["DEPLOY_X"] == "":
        result["ERROR"].append({"DEPLOY_X": "Device position(X) is Empty!"})
    if req["DEPLOY_Y"] == "":
        result["ERROR"].append({"DEPLOY_Y": "Device position(Y) is Empty!"})
    if req["DEPLOY_Z"] == "":
        result["ERROR"].append({"DEPLOY_Z": "Device position(Z) is Empty!"})
    if req["ROT_X"] == "":
        result["ERROR"].append({"ROT_X": "Device rotation(X) is Empty!"})
    if req["ROT_Y"] == "":
        result["ERROR"].append({"ROT_Y": "Device rotation(Y) is Empty!"})
    if req["ROT_Z"] == "":
        result["ERROR"].append({"ROT_Z": "Device rotation(Z) is Empty!"})
    if req["DEPLOY_LOC"] == "":
        result["ERROR"].append({"DEPLOY_LOC": "Device location is Empty!"})
    if req["DEVICE_TYPE"] == "":
        result["ERROR"].append({"DEVICE_TYPE": "Device type is Empty!"})
    if len(result["ERROR"]):
        return result
    sql = "SELECT * FROM Gaitmetrics.DEVICES WHERE MAC='%s'" % (req["MAC"])
    cursor.execute(sql)
    dbresult = cursor.fetchall()
    if dbresult:
        result["ERROR"].append({"MAC": "MAC Address already registered!"})
        return result
    sql = "SELECT * FROM Gaitmetrics.DEVICES WHERE NAME='%s'" % (req["NAME"])
    cursor.execute(sql)
    dbresult = cursor.fetchall()
    if dbresult:
        result["ERROR"].append({"NAME": "Name is taken!"})
    else:
        sql = "SELECT * FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s'" % (
            req["DEPLOY_LOC"]
        )
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        if not dbresult:
            result["ERROR"].append({"DEPLOY_LOC": "Device Location not found!"})
            return result
        cursor.execute(
            "INSERT INTO Gaitmetrics.RL_ROOM_MAC (ROOM_UUID, MAC) VALUES (%s, %s)",
            (dbresult[3], req["MAC"]),
        )
        connection.commit()
        cursor.execute(
            "INSERT INTO Gaitmetrics.DEVICES (MAC, NAME, TYPE, STATUS, DEPLOY_X, DEPLOY_Y, DEPLOY_Z, ROT_X, ROT_Y, ROT_Z, DESCRIPTION) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                req["MAC"],
                req["NAME"],
                req["DEVICE_TYPE"],
                "DISCONNECTED",
                req["DEPLOY_X"],
                req["DEPLOY_Y"],
                req["DEPLOY_Z"],
                req["ROT_X"],
                req["ROT_Y"],
                req["ROT_Z"],
                req["DESCRIPTION"],
            ),
        )
        connection.commit()
        result["DATA"].append(
            {"MESSAGE": "Device " + req["MAC"] + " registered succefully"}
        )
    # Add_Vernemq_db(req['MAC'])
    cursor.close()
    connection.close()

    return result


def updateDeviceDetail(req):
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    if req["MAC"] == "":
        result["ERROR"].append({"MAC": "MAC Address is Empty!"})
    if req["NAME"] == "":
        result["ERROR"].append({"NAME": "Device Name is Empty!"})
    elif "'" in req["NAME"]:
        result["ERROR"].append({"NAME": "' is not allowed"})
    if req["DEPLOY_X"] == "":
        result["ERROR"].append({"DEPLOY_X": "Device position(X) is Empty!"})
    if req["DEPLOY_Y"] == "":
        result["ERROR"].append({"DEPLOY_Y": "Device position(Y) is Empty!"})
    if req["DEPLOY_Z"] == "":
        result["ERROR"].append({"DEPLOY_Z": "Device position(Z) is Empty!"})
    if req["ROT_X"] == "":
        result["ERROR"].append({"ROT_X": "Device rotation(X) is Empty!"})
    if req["ROT_Y"] == "":
        result["ERROR"].append({"ROT_Y": "Device rotation(Y) is Empty!"})
    if req["ROT_Z"] == "":
        result["ERROR"].append({"ROT_Z": "Device rotation(Z) is Empty!"})
    if req["DEPLOY_LOC"] == "":
        result["ERROR"].append({"DEPLOY_LOC": "Device Location is Empty!"})
    if len(result["ERROR"]):
        return result
    sql = "SELECT * FROM Gaitmetrics.DEVICES WHERE MAC='%s'" % (req["MAC"])
    cursor.execute(sql)
    dbresult1 = cursor.fetchone()
    if not dbresult1:
        result["ERROR"].append({"MAC": "Mac address not found!"})
        return result
    sql = "SELECT * FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s'" % (
        req["DEPLOY_LOC"]
    )
    cursor.execute(sql)
    dbresult1 = cursor.fetchone()
    print(dbresult1)
    if not dbresult1:
        result["ERROR"].append({"DEPLOY_LOC": "Device Location not found!"})
        return result
    sql = "SELECT * FROM Gaitmetrics.RL_ROOM_MAC WHERE ROOM_UUID='%s' AND MAC='%s'" % (
        req["DEPLOY_O_LOC"],
        req["MAC"],
    )
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    print(dbresult)
    if dbresult:
        sql = (
            "UPDATE Gaitmetrics.RL_ROOM_MAC SET ROOM_UUID='%s', MAC='%s' WHERE RL_ID='%s'"
            % (req["DEPLOY_LOC"], req["MAC"], dbresult[0])
        )
        cursor.execute(sql)
    else:
        cursor.execute(
            "INSERT INTO Gaitmetrics.RL_ROOM_MAC (ROOM_UUID, MAC) VALUES (%s, %s)",
            (req["DEPLOY_LOC"], req["MAC"]),
        )
    sql = (
        "UPDATE Gaitmetrics.DEVICES SET MAC='%s', NAME='%s', TYPE='%s', DEPLOY_X='%s', DEPLOY_Y='%s', DEPLOY_Z='%s', ROT_X='%s', ROT_Y='%s', ROT_Z='%s', DESCRIPTION='%s' WHERE Id='%s'"
        % (
            req["MAC"],
            req["NAME"],
            req["DEVICE_TYPE"],
            req["DEPLOY_X"],
            req["DEPLOY_Y"],
            req["DEPLOY_Z"],
            req["ROT_X"],
            req["ROT_Y"],
            req["ROT_Z"],
            req["DESCRIPTION"],
            req["Id"],
        )
    )
    print(sql)
    cursor.execute(sql)
    result["DATA"] = [{"MESSAGE": "Device " + req["MAC"] + " updated succefully"}]
    connection.commit()
    cursor.close()
    connection.close()
    # Add_Vernemq_db(req['MAC'])
    return result


def deleteDeviceDetail(req):
    id = req["Id"]
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    sql = "DELETE FROM Gaitmetrics.RL_ROOM_MAC WHERE MAC='%s'" % (req["MAC"])
    cursor.execute(sql)
    connection.commit()
    sql = "DELETE FROM Gaitmetrics.DEVICES WHERE Id='%s'" % (id)
    cursor.execute(sql)
    connection.commit()

    cursor.close()
    connection.close()
    vernemq_db_connection = mysql.connector.connect(**vernemq_db)
    vernemq_db_cursor = vernemq_db_connection.cursor()
    sql = "DELETE FROM vernemq_db.vmq_auth_acl WHERE client_id='%s'" % (req["MAC"])
    vernemq_db_cursor.execute(sql)
    vernemq_db_connection.commit()
    vernemq_db_cursor.close()
    vernemq_db_connection.close()
    result["CODE"] = 0
    return result


def Add_Vernemq_db(mac):
    vernemq_db_connection = mysql.connector.connect(**vernemq_db)
    vernemq_db_cursor = vernemq_db_connection.cursor()
    sql = "SELECT * FROM vernemq_db.vmq_auth_acl WHERE client_id='%s'" % (mac)
    vernemq_db_cursor.execute(sql)
    dbresult = vernemq_db_cursor.fetchall()
    if dbresult:
        vernemq_db_cursor.execute(
            "UPDATE `vmq_auth_acl` SET `client_id`='"
            + mac
            + "',`username`='_"
            + mac
            + "',`password`=MD5(SHA1('radar1"
            + MQTT_GRP
            + "_"
            + mac
            + mac
            + '\')),`publish_acl`=\'[{"pattern":"/'
            + MQTT_GRP
            + "/DEV/"
            + mac
            + '/#"}]\',`subscribe_acl`=\'[{"pattern":"/'
            + MQTT_GRP
            + "/DEV/"
            + mac
            + "/#\"}]' WHERE `client_id`='"
            + mac
            + "';"
        )
        print(" - Updated entry in vmq_auth_acl")
    else:
        vernemq_db_cursor.execute(
            "INSERT INTO `vmq_auth_acl`(`client_id`,`username`,`password`,`publish_acl`,`subscribe_acl`) VALUES ('"
            + mac
            + "','_"
            + mac
            + "',MD5(SHA1('radar1"
            + MQTT_GRP
            + "_"
            + mac
            + mac
            + '\')),\'[{"pattern":"/'
            + MQTT_GRP
            + "/DEV/"
            + mac
            + '/#"}]\',\'[{"pattern":"/'
            + MQTT_GRP
            + "/DEV/"
            + mac
            + "/#\"}]');"
        )
        print(" - Added entry to vmq_auth_acl")
    vernemq_db_connection.commit()
    vernemq_db_cursor.close()
    vernemq_db_connection.close()


# def getDeviceStatusData(req, admin):
#     connection = mysql.connector.connect(**config)
#     cursor = connection.cursor()
#     result = defaultdict(list)
#     if not admin:
#         sql = "SELECT MAC FROM RL_USER_MAC WHERE USER_ID='%s'"%(req['ID'])
#         cursor.execute(sql)
#         dbresult = cursor.fetchone()
#         if dbresult:
#             li = list(dbresult[0])
#             with open("logs", "a+") as myfile:
#                 myfile.write("dbresult: "+str(dbresult)+", mac: "+str(li[0])+"\n")
#             print(dbresult[0])
#         else:
#             result['CODE'] = -1
#     cursor.close()
#     connection.close()
#     return result


def insertDeviceCredential(req):
    try:
        result = defaultdict(list)
        # if req.get('mountpoint') == None:
        #     result['ERROR'].append({'mountpoint': 'mountpoint is not provided!'})

        # if req.get('client_id') == None:
        #     result['ERROR'].append({'client_id': 'client_id is not provided!'})
        # elif req.get('client_id') == '':
        #     result['ERROR'].append({'client_id': 'client_id is empty!'})

        if req.get("username") == None:
            result["ERROR"].append({"username": "username is not provided!"})
        elif req.get("username") == "":
            result["ERROR"].append({"username": "username is empty!"})

        if req.get("password") == None:
            result["ERROR"].append({"password": "password is not provided!"})
        elif req.get("password") == "":
            result["ERROR"].append({"password": "password is empty!"})

        # if req.get('publish_acl') == None:
        #     result['ERROR'].append({'publish_acl': 'publish_acl is not provided!'})
        # elif req.get('publish_acl') == '':
        #     result['ERROR'].append({'publish_acl': 'publish_acl is empty!'})

        # if req.get('subscribe_acl') == None:
        #     result['ERROR'].append({'subscribe_acl': 'subscribe_acl is not provided!'})
        # elif req.get('subscribe_acl') == '':
        #     result['ERROR'].append({'subscribe_acl': 'subscribe_acl is empty!'})

        if len(result["ERROR"]):
            return result

        mountpoint = ""  # req['mountpoint']
        mac = req["username"]
        client_id = mac  # req['client_id']
        username = "_" + mac
        password = req["password"]
        publish_acl = '[{"pattern":"/GMT/DEV/' + mac + '/#"}]'  # req['publish_acl']
        subscribe_acl = '[{"pattern":"/GMT/DEV/' + mac + '/#"}]'  # req['subscribe_acl']
        connection = mysql.connector.connect(**vernemq_db)
        cursor = connection.cursor()
        result = {}
        sql = (
            "INSERT INTO vmq_auth_acl (mountpoint,client_id,username,password,publish_acl,subscribe_acl) VALUES ('%s','%s','%s',md5('%s'),'%s','%s')"
            % (mountpoint, client_id, username, password, publish_acl, subscribe_acl)
        )

        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()
        return {"DATA": ["Device credential inserted!"]}
    except Exception as e:
        print(e)
        return {"ERROR": ["Failed to insert device credential!"]}
