import json
import time
import mysql.connector
from datetime import datetime

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}

devicesTbl={}

def on_message(client, obj, msg):
    global devicesTbl,config
    print(msg.topic)
    
    # print(msg.payload.decode('utf-8'))
    TOPIC = msg.topic.split("/")
    if TOPIC[-1] == "UPDATE_DEV_CONF":
        print("Received device setting update request for: " + msg.payload.decode("utf-8"))
        DEV = msg.payload.decode("utf-8").upper()
        if DEV in devicesTbl:
            print(DEV)
            del devicesTbl[DEV]
        return
    elif TOPIC[-2]=="REQ":
        REQ = TOPIC[-1]
        if REQ == "UPDATE_CONFIG":
            MAC = TOPIC[3]
            PAYLOAD = msg.payload.decode('utf-8')
            print("Received device request for: " + REQ +"\r\n"+PAYLOAD)
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor(dictionary=True)      
            sql="UPDATE `DEVICES` SET `HWINFO`='"+PAYLOAD+"' WHERE MAC='"+MAC+"';"
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            connection.close() 
            ACK_TOPIC = msg.topic.replace(REQ, "ACK")
            client.publish(ACK_TOPIC,"", qos=1)
        return
    elif TOPIC[-1]=="STATUS":
        MAC = TOPIC[3]
        PAYLOAD = msg.payload.decode('utf-8')
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)      
        sql="UPDATE `DEVICES` SET `STATUS`='"+PAYLOAD+"' WHERE MAC='"+MAC+"';"
        print(sql)
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()         
        return
    PAYLOAD = json.loads(msg.payload.decode('utf-8'))
    MAC = TOPIC[3]
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)  
    table_name = get_table_name(connection,cursor)
    check_table_exist(connection,cursor,table_name)
    sql="UPDATE `DEVICES` SET `LAST_DATA_RECEIVED`=NOW(),`STATUS`='CONNECTED' WHERE MAC='"+MAC+"';"
    cursor.execute(sql)      
    # print(sql)
    ROOM_UUID = None
    if MAC not in devicesTbl:
        print("New device ["+MAC+"]")
        devicesTbl[MAC]={}
        sql="SELECT * FROM ROOMS_DETAILS RIGHT JOIN RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID WHERE MAC='"+MAC+"';"
        cursor.execute(sql)
        dbresult = cursor.fetchone() 
        if dbresult == None:
            print("Device not registered")
            cursor.close()
            connection.close()            
            return     
        devicesTbl[MAC]=dbresult
        print(devicesTbl)
    ROOM_UUID = devicesTbl[MAC]['ROOM_UUID']
    print("Update device info for "+ MAC)
    DATA = PAYLOAD["DATA"]
    TYPE = PAYLOAD["TYPE"]
    OBJECT_COUNT = 0
    OBJECT_LOCATION = 0
    if TYPE == "WALL":
        Type = "1"
    elif TYPE == "CEIL":
        Type = "2"
    elif TYPE == "VITAL":
        Type = "3"
    else:
        Type = "0"
    ROOM_STATUS = 0
    OBJECT_COUNT = 0        
    for D in DATA:
        STATE = 4
        TIME = D['timeStamp']
        OBJECT_LOCATION = 0
        ROOM_STATUS = 0
        OBJECT_COUNT = 0
        if abs(time.time() - TIME) > 3600: 
            TIME = time.time()
        if Type == "1" or Type == "2":
            if D['state'] == None:
                STATE = 4
                if (D['numSubjects'] == None or D['numSubjects'] == 0):
                    ROOM_STATUS = 0
                else:
                    ROOM_STATUS = None
            elif D['state'] == "Moving":
                STATE = 0
                ROOM_STATUS = 1
            elif D['state'] == "Upright":
                STATE = 1
                ROOM_STATUS = 1
            elif D['state'] == "Laying":
                STATE = 2
                ROOM_STATUS = 2
            elif D['state'] == "Fall":
                STATE = 3
                ROOM_STATUS = 255
            OBJECT_COUNT = 0 if D['numSubjects'] == None else D['numSubjects']
            OBJECT_LOCATION = 0 if D['roomOccupancy'] == None else int(D['roomOccupancy'])
            PX = "NULL" if D['posX']==None else str(round(D['posX'],3))
            PY = "NULL" if D['posY']==None else str(round(D['posY'],3))
            PZ = "NULL" if D['posZ']==None else str(round(D['posZ'],3))
            VX = "NULL" if D['velX']==None else str(round(D['velX'],3))
            VY = "NULL" if D['velY']==None else str(round(D['velX'],3))
            VZ = "NULL" if D['velZ']==None else str(round(D['velX'],3))
            AX = "NULL" if D['accX']==None else str(round(D['accX'],3))
            AY = "NULL" if D['accY']==None else str(round(D['accX'],3))
            AZ = "NULL" if D['accZ']==None else str(round(D['accX'],3))
            SIGN_OF_LIFE = "NULL" if D.get('signOfLife') == None else str(D.get('signOfLife'))
            # print(STATE,OBJECT_COUNT,OBJECT_LOCATION)
            sql = f"INSERT INTO `{table_name}`(`TIMESTAMP`, `ROOM_UUID`, `MAC`, `TYPE`, `STATE`, `OBJECT_COUNT`, `OBJECT_LOCATION`, `PX`, `PY`, `PZ`, `VX`, `VY`, `VZ`, `AX`, `AY`, `AZ`, `SIGN_OF_LIFE`) VALUES (FROM_UNIXTIME(%s),'%s','%s',%s,%d,%d,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"%(TIME,ROOM_UUID,MAC,Type,STATE,OBJECT_COUNT,OBJECT_LOCATION,PX,PY,PZ,VX,VY,VZ,AX,AY,AZ,SIGN_OF_LIFE)
            if OBJECT_COUNT > 0 and STATE ==4:
                ROOM_STATUS = 1
        elif Type == "3":
            # print(D)
            IN_BED = 0 if D['bedOccupancy']==None else D['bedOccupancy']
            IN_BED_MOVING = "NULL" if D.get('inBedMoving')==None else str(D.get('inBedMoving'))
            SIGN_OF_LIFE = "NULL" if D.get('signOfLife') == None else str(D.get('signOfLife'))
            if D['bedOccupancy']:
                STATE = 2
                OBJECT_LOCATION = 1
                ROOM_STATUS = 2
            HEART_RATE = "NULL" if D['heartRate']==None else str(round(D['heartRate'],1))
            BREATH_RATE = "NULL" if D['breathRate']==None else str(round(D['breathRate'],1))
            sql = f"INSERT INTO `{table_name}`(`TIMESTAMP`, `ROOM_UUID`, `MAC`, `TYPE`, `STATE`, `OBJECT_LOCATION`, `IN_BED`, `HEART_RATE`, `BREATH_RATE`, `IN_BED_MOVING`, `SIGN_OF_LIFE`) VALUES (FROM_UNIXTIME(%s),'%s','%s',%s,%d,%d,%d,%s,%s,%s,%s)"%(TIME,ROOM_UUID,MAC,Type,STATE,OBJECT_LOCATION,IN_BED,HEART_RATE,BREATH_RATE,IN_BED_MOVING,SIGN_OF_LIFE)
        # print(sql)
        cursor.execute(sql)  
    
    if (ROOM_STATUS is not None):
        sql="UPDATE `ROOMS_DETAILS` SET `STATUS`="+str(ROOM_STATUS)+",`OCCUPANCY`="+str(OBJECT_COUNT)+",`LAST_DATA_TS`=NOW() WHERE ROOM_UUID='"+devicesTbl[MAC]['ROOM_UUID']+"';"
    else:
        sql="UPDATE `ROOMS_DETAILS` SET `OCCUPANCY`="+str(OBJECT_COUNT)+",`LAST_DATA_TS`=NOW() WHERE ROOM_UUID='"+devicesTbl[MAC]['ROOM_UUID']+"';"
    cursor.execute(sql)
    print(sql)
        
    connection.commit()
    cursor.close()
    connection.close()   

    client.publish(msg.topic.replace("/DATA/","/EXTRA_DATA/"),json.dumps(PAYLOAD), qos=1)

def get_table_name(connection,cursor):
    cursor.execute("SELECT DATE_FORMAT(CURRENT_DATE(), '%Y_%m_%d') AS format_date")
    formatted_date = cursor.fetchall()[0]["format_date"]
    table_name = f'PROCESSED_DATA_{formatted_date}'
    return table_name

def check_table_exist(connection,cursor,table_name):
    table_exists_query = f"SHOW TABLES LIKE '{table_name}'"
    cursor.execute(table_exists_query)
    table_exists = cursor.fetchone()

    # If table does not exist, create it
    if not table_exists:
        print("Creating table....")
        create_table_query = f"""
        CREATE TABLE {table_name} (
          `ID` int(11) NOT NULL AUTO_INCREMENT,
          `TIMESTAMP` timestamp NOT NULL DEFAULT current_timestamp(),
          `ROOM_UUID` varchar(50) DEFAULT NULL,
          `MAC` varchar(12) NOT NULL,
          `TYPE` tinyint(4) DEFAULT 0 COMMENT '0: undefined; 1: wall; 2: ceil; 3: vital ',
          `STATE` tinyint(4) DEFAULT NULL COMMENT '0: Moving, 1: Upright, 2: Laying, 3: Fall, 4: None, 5: Social',
          `OBJECT_COUNT` tinyint(4) NOT NULL DEFAULT 0,
          `OBJECT_LOCATION` tinyint(4) DEFAULT NULL COMMENT '0: out room, 1: in room',
          `IN_BED` tinyint(1) NOT NULL DEFAULT 0,
          `IN_BED_MOVING` tinyint(1) DEFAULT NULL,
          `SIGN_OF_LIFE` tinyint(1) DEFAULT NULL,
          `HEART_RATE` float DEFAULT NULL,
          `BREATH_RATE` float DEFAULT NULL,
          `PX` float DEFAULT NULL,
          `PY` float DEFAULT NULL,
          `PZ` float DEFAULT NULL,
          `VX` float DEFAULT NULL,
          `VY` float DEFAULT NULL,
          `VZ` float DEFAULT NULL,
          `AX` float DEFAULT NULL,
          `AY` float DEFAULT NULL,
          `AZ` float DEFAULT NULL,
          PRIMARY KEY (`ID`),
          KEY `TIMESTAMP` (`TIMESTAMP`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs;
        """.format(table_name=table_name)
        cursor.execute(create_table_query)
        connection.commit()