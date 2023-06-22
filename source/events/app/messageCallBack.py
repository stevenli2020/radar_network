import json
import time
import mysql.connector

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
            client.publish(ACK_TOPIC,"")
        return
    elif TOPIC[-1]=="STATUS":
        MAC = TOPIC[3]
        PAYLOAD = msg.payload.decode('utf-8')
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)      
        sql="UPDATE `DEVICES` SET `STATUS`='"+PAYLOAD+"' WHERE MAC='"+MAC+"';"
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()         
        return
    PAYLOAD = json.loads(msg.payload.decode('utf-8'))
    MAC = TOPIC[3]
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)       
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
                ROOM_STATUS = 0
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
            # print(STATE,OBJECT_COUNT,OBJECT_LOCATION)
            sql = "INSERT INTO `PROCESSED_DATA`(`TIMESTAMP`, `MAC`, `TYPE`, `STATE`, `OBJECT_COUNT`, `OBJECT_LOCATION`, `PX`, `PY`, `PZ`, `VX`, `VY`, `VZ`, `AX`, `AY`, `AZ`) VALUES (FROM_UNIXTIME(%s),'%s',%s,%d,%d,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s)"%(TIME,MAC,Type,STATE,OBJECT_COUNT,OBJECT_LOCATION,PX,PY,PZ,VX,VY,VZ,AX,AY,AZ)
            if OBJECT_COUNT > 0 and STATE ==4:
                ROOM_STATUS = 1
        elif Type == "3":
            # print(D)
            IN_BED = 0 if D['bedOccupancy']==None else D['bedOccupancy']
            if D['bedOccupancy']:
                STATE = 2
                OBJECT_LOCATION = 1
                ROOM_STATUS = 2
            HEART_RATE = "NULL" if D['heartRate']==None else str(round(D['heartRate'],1))
            BREATH_RATE = "NULL" if D['breathRate']==None else str(round(D['breathRate'],1))
            sql = "INSERT INTO `PROCESSED_DATA`(`TIMESTAMP`, `MAC`, `TYPE`, `STATE`, `OBJECT_LOCATION`, `IN_BED`, `HEART_RATE`, `BREATH_RATE`) VALUES (FROM_UNIXTIME(%s),'%s',%s,%d,%d,%d,%s,%s)"%(TIME,MAC,Type,STATE,OBJECT_LOCATION,IN_BED,HEART_RATE,BREATH_RATE)
        # print(sql)
        cursor.execute(sql)  
        sql="UPDATE `ROOMS_DETAILS` SET `STATUS`="+str(ROOM_STATUS)+",`OCCUPANCY`="+str(OBJECT_COUNT)+",`LAST_DATA_TS`=NOW() WHERE ROOM_UUID='"+devicesTbl[MAC]['ROOM_UUID']+"';"
        cursor.execute(sql)
        sql="UPDATE `DEVICES` SET `LAST_DATA_RECEIVED`=NOW() WHERE MAC='"+MAC+"';"
        cursor.execute(sql)       
    connection.commit()
    cursor.close()
    connection.close()   