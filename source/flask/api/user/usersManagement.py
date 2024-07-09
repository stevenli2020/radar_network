import mysql.connector
from user.config import config, vernemq, domain_url
from datetime import datetime, timedelta

from collections import defaultdict
from user.email.gmail import sentMail
from user.email.gmailTemplate import emailTemplate
import re
import hashlib
import pytz
from tzlocal import get_localzone

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

# SELECT ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS, CODE, LAST_UPDATE, CREATED, MAC FROM USERS JOIN RL_USER_MAC ON USERS.ID=RL_USER_MAC.USER_ID;

config = config()
vernemq_db = vernemq()

def requestAllUsers():
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    local_timezone = get_localzone()
    sql = "SELECT USERS.ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, USERS.STATUS, CODE, LAST_UPDATE, CREATED, GROUP_CONCAT(ROOMS_DETAILS.ROOM_NAME) AS ROOM_NAME FROM Gaitmetrics.USERS LEFT JOIN Gaitmetrics.RL_USER_ROOM ON USERS.ID=RL_USER_ROOM.USER_ID LEFT JOIN Gaitmetrics.ROOMS_DETAILS ON RL_USER_ROOM.ROOM_ID=ROOMS_DETAILS.ID GROUP BY USERS.ID"
    cursor.execute(sql)
    result["DATA"] = [{"ID": ID, "LOGIN_NAME": LOGIN_NAME, "FULL_NAME": FULL_NAME, "EMAIL": EMAIL, "PHONE": PHONE, "TYPE": TYPE, "STATUS": STATUS, "CODE": CODE, "LAST_UPDATE": LAST_UPDATE.astimezone(local_timezone).astimezone(pytz.utc) if LAST_UPDATE else LAST_UPDATE, "CREATED": CREATED.astimezone(local_timezone).astimezone(pytz.utc) if CREATED else CREATED, "ROOM_NAME": ROOM_NAME} for (ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS,CODE, LAST_UPDATE, CREATED, ROOM_NAME) in cursor]
    cursor.close()
    connection.close()
    return result

def requestSpecificUser(data):
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    Id = data['USER_ID']
    local_timezone = get_localzone()
    sql = "SELECT USERS.ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, USERS.STATUS, CODE, LAST_UPDATE, CREATED, GROUP_CONCAT(ROOMS_DETAILS.ROOM_NAME) AS ROOM_NAME FROM Gaitmetrics.USERS LEFT JOIN Gaitmetrics.RL_USER_ROOM ON USERS.ID=RL_USER_ROOM.USER_ID LEFT JOIN Gaitmetrics.ROOMS_DETAILS ON RL_USER_ROOM.ROOM_ID=ROOMS_DETAILS.ID WHERE USERS.ID='%s' GROUP BY USERS.ID"%(Id)
    cursor.execute(sql)
    result["DATA"] = [{"ID": ID, "LOGIN_NAME": LOGIN_NAME, "FULL_NAME": FULL_NAME, "EMAIL": EMAIL, "PHONE": PHONE, "TYPE": TYPE, "STATUS": STATUS, "CODE": CODE, "LAST_UPDATE": LAST_UPDATE.astimezone(local_timezone).astimezone(pytz.utc) if LAST_UPDATE else LAST_UPDATE, "CREATED": CREATED.astimezone(local_timezone).astimezone(pytz.utc) if CREATED else CREATED, "ROOM_NAME": ROOM_NAME} for (ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS,CODE, LAST_UPDATE, CREATED, ROOM_NAME) in cursor]
    # sql = "SELECT ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS, CODE, LAST_UPDATE, CREATED FROM USERS WHERE ID='%s'"%(data['USER_ID'])
    # cursor.execute(sql)
    # result["DATA"] = [{"ID": ID, "LOGIN_NAME": LOGIN_NAME, "FULL_NAME": FULL_NAME, "EMAIL": EMAIL, "PHONE": PHONE, "TYPE": TYPE, "STATUS": STATUS, "CODE": CODE, "LAST_UPDATE": LAST_UPDATE, "CREATED": CREATED} for (ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS,CODE, LAST_UPDATE, CREATED) in cursor]
    # sql = "SELECT MAC FROM RL_USER_MAC WHERE USER_ID='%s'"%(Id)
    # cursor.execute(sql)
    # dbresult = cursor.fetchone()
    # if dbresult:
    #     result['DATA'][0]['MAC'] = dbresult[0]
    cursor.close()
    connection.close()
    return result

def addNewUser(data):    
    result = defaultdict(list)      
    # MAC = data['MAC']
    # print(MAC)
    # print(type(MAC))
    if data['LOGIN_NAME'] == '':
        result['ERROR'].append({'Username': 'Username is Empty!'})
    if data['FULL_NAME'] == '':
        result['ERROR'].append({'Fullname': 'Fullname is Empty!'})
    if data['EMAIL'] == '':
        result['ERROR'].append({'Email': 'Email is Empty!'})
    else:
        if not re.fullmatch(regex, data['EMAIL']):
            result['ERROR'].append({'Email': 'Email address is incorrect!'})
    if data['USER_TYPE'] == '-1' or data['USER_TYPE'] == '':
        result['ERROR'].append({'Type': "Please select user type"})
    if len(result['ERROR']):
        return result
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT * FROM Gaitmetrics.USERS WHERE LOGIN_NAME='%s'"%(data['LOGIN_NAME'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    if dbresult:
        result['ERROR'].append({'Username': 'Username is taken'})
        return result
    sql = "SELECT * FROM Gaitmetrics.USERS WHERE EMAIL='%s'"%(data['EMAIL'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    if dbresult:
        result['ERROR'].append({'Email': 'Email is taken'})
        return result
    bencode = str.encode(data['LOGIN_NAME'] + data['EMAIL'])
    code = hashlib.sha256(bencode).hexdigest()
    now = datetime.now()
    cursor.execute("INSERT INTO Gaitmetrics.USERS (LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS, CODE, CREATED) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (data['LOGIN_NAME'], data['FULL_NAME'], data['EMAIL'], data['PHONE'], data['USER_TYPE'], 0, code, now))
    connection.commit()
    body = emailTemplate(data['LOGIN_NAME'], domain_url() + "/resetPassword?user="+str(data['LOGIN_NAME'])+"&code="+str(code)+"&mode=add", "add")
    sentMail(data['EMAIL'], 'Account Created Successfully', body)
    if str(data['USER_TYPE']) == '0':
        sql = "SELECT * FROM Gaitmetrics.USERS WHERE LOGIN_NAME='%s'"%(data['LOGIN_NAME'])
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        # print(dbresult)
        if dbresult:
            id = dbresult[0]
            if (data['ROOM']):
                RoomList = str(data['ROOM']).split(',')
                for Room in RoomList:
                    RoomName = Room.replace("'", "")
                    RoomName = RoomName.replace("]", "")
                    RoomName = RoomName.replace("[", "")
                    # RoomName = RoomName.replace(" ", "")
                    
                    if RoomName[0] == " ":
                        RoomName = RoomName[1:]
                    if RoomName[-1] == " ":
                        RoomName = RoomName[:-1]
                    print(RoomName)
                    sql = "SELECT * FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_NAME='%s'"%(RoomName)
                    cursor.execute(sql)
                    dbresult = cursor.fetchone()
                    print(dbresult)
                    if dbresult:
                        cursor.execute("INSERT INTO Gaitmetrics.RL_USER_ROOM (USER_ID, ROOM_ID) VALUES(%s, %s)", (id, dbresult[0]))
                        connection.commit()
                # for x in MAC:
                #     cursor.execute("INSERT INTO RL_USER_MAC (USER_ID, MAC) VALUES(%s, %s)", (id, x))
                #     connection.commit()
    
    vernemq_db_connection = mysql.connector.connect(**vernemq_db)
    vernemq_db_cursor = vernemq_db_connection.cursor()
    acl_data = []
    for i in range(1, 51):
        client_id = data['LOGIN_NAME'] + str(i)
        acl_data.append(("", client_id, data['LOGIN_NAME'], "c764eb2b5fa2d259dc667e2b9e195218", '[{"pattern":"/GMT/#"}]', '[{"pattern":"/GMT/#"}]'))

    # Inserting multiple rows into vmq_auth_acl
    sql = "INSERT INTO vmq_auth_acl (mountpoint, client_id, username, password, publish_acl, subscribe_acl) VALUES (%s, %s, %s, md5(%s), %s, %s)"
    vernemq_db_cursor.executemany(sql, acl_data)
    vernemq_db_connection.commit()
    vernemq_db_cursor.close()
    vernemq_db_connection.close()
    cursor.close()
    connection.close()
    result['DATA'].append({"CODE": 0})
    return result

def updateUserDetails(data):    
    result = defaultdict(list)      
         
    if data['LOGIN_NAME'] == '':
        result['ERROR'].append({'Username': 'Username is Empty!'})
    if data['FULL_NAME'] == '':
        result['ERROR'].append({'Fullname': 'Fullname is Empty!'})
    if data['EMAIL'] == '':
        result['ERROR'].append({'Email': 'Email is Empty!'})
    else:
        if not re.fullmatch(regex, data['EMAIL']):
            result['ERROR'].append({'Email': 'Email address is incorrect!'})
    if data['USER_TYPE'] == '-1' or data['USER_TYPE'] == '':
        result['ERROR'].append({'Type': "Please select user type"})
    if len(result['ERROR']):
        return result
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    vernemq_db_connection = mysql.connector.connect(**vernemq_db)
    vernemq_db_cursor = vernemq_db_connection.cursor()

    sql = "SELECT * FROM Gaitmetrics.USERS WHERE ID=%s"
    cursor.execute(sql, (data['USER_ID'],))
    dbresult = cursor.fetchone()
    if not dbresult:
        result['ERROR'].append({'User_ID': 'User ID not found!'})
        return result

    if dbresult[1] != data['LOGIN_NAME']:
        sql = "SELECT * FROM Gaitmetrics.USERS WHERE LOGIN_NAME=%s"
        cursor.execute(sql, (data['LOGIN_NAME'],))
        userresult = cursor.fetchone()
        if userresult:
            result['ERROR'].append({'Username': 'Username is taken'})
            return result

        # Delete existing ACL entries for the old username
        sql = "DELETE FROM vmq_auth_acl WHERE username=%s"
        vernemq_db_cursor.execute(sql, (dbresult[1],))
        vernemq_db_connection.commit()

        # Insert new ACL entries for the new username
        acl_data = []
        for i in range(1, 51):
            client_id = data['LOGIN_NAME'] + str(i)
            acl_data.append(("", client_id, data['LOGIN_NAME'], "c764eb2b5fa2d259dc667e2b9e195218", '[{"pattern":"/GMT/#"}]', '[{"pattern":"/GMT/#"}]'))

        sql = "INSERT INTO vmq_auth_acl (mountpoint, client_id, username, password, publish_acl, subscribe_acl) VALUES (%s, %s, %s, md5(%s), %s, %s)"
        vernemq_db_cursor.executemany(sql, acl_data)
        vernemq_db_connection.commit()

    if dbresult[3] != data['EMAIL']:
        sql = "SELECT * FROM Gaitmetrics.USERS WHERE EMAIL=%s"
        cursor.execute(sql, (data['EMAIL'],))
        emailresult = cursor.fetchone()
        if emailresult:
            result['ERROR'].append({'Email': 'Email is taken'})
            return result   

    sql = "UPDATE Gaitmetrics.USERS SET LOGIN_NAME=%s, FULL_NAME=%s, EMAIL=%s,PHONE=%s, TYPE=%s WHERE ID=%s"
    cursor.execute(sql, (data['LOGIN_NAME'], data['FULL_NAME'], data['EMAIL'], data['PHONE'], data['USER_TYPE'], data['USER_ID']))
    connection.commit()

    sql = "DELETE FROM Gaitmetrics.RL_USER_ROOM WHERE USER_ID=%s"
    cursor.execute(sql, (data['USER_ID'],))
    connection.commit()
    RoomList = str(data['ROOM']).split(',')
    for Room in RoomList:
        if not Room:
            continue
        RoomName = Room.replace("'", "").strip()
        sql = "SELECT * FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_NAME=%s"
        cursor.execute(sql, (RoomName,))
        dbresult = cursor.fetchone()
        if dbresult:
            sql = "INSERT INTO Gaitmetrics.RL_USER_ROOM (USER_ID, ROOM_ID) VALUES(%s, %s)"
            cursor.execute(sql, (data['USER_ID'], dbresult[0]))
            connection.commit()

    cursor.close()
    connection.close()
    vernemq_db_cursor.close()
    vernemq_db_connection.close()

    result['DATA'].append({"CODE": 0})
    return result
    
def deleteUserDetails(data):    
    result = defaultdict(list)      
         
    if data['USER_ID'] == '':
        result['ERROR'].append({'Username': 'User not found!'})
        return result
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT * FROM Gaitmetrics.USERS WHERE ID='%s'"%(data['USER_ID'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    print(dbresult)
    if not dbresult:
        result['ERROR'].append({'Username': 'User not found!'})
        return result   
    sql = "DELETE FROM Gaitmetrics.USERS WHERE ID='%s'"%(data['USER_ID'])
    cursor.execute(sql)
    connection.commit()
    sql = "DELETE FROM Gaitmetrics.RL_USER_ROOM WHERE USER_ID='%s'"%(data['USER_ID'])
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()

    vernemq_db_connection = mysql.connector.connect(**vernemq_db)
    vernemq_db_cursor = vernemq_db_connection.cursor()
    sql = "DELETE FROM vmq_auth_acl WHERE username='%s'" % (dbresult[1])  # Assuming dbresult[1] contains the username
    vernemq_db_cursor.execute(sql)
    vernemq_db_connection.commit()
    vernemq_db_cursor.close()
    vernemq_db_connection.close()

    result['DATA'].append({"CODE": 0})
    return result

def getMQTTClientID(username):
    client_id = None
    try:
        vernemq_db_connection = mysql.connector.connect(**vernemq_db)
        vernemq_db_cursor = vernemq_db_connection.cursor(dictionary=True)
        sql = "SELECT client_id FROM vmq_auth_acl WHERE username='%s' AND connected=0 ORDER BY last_connect_time LIMIT 1" % (username)  # Assuming dbresult[1] contains the username
        vernemq_db_cursor.execute(sql)
        result = vernemq_db_cursor.fetchall()
        if (len(result) == 0):
            sql = "SELECT client_id FROM vmq_auth_acl WHERE username='%s' AND connected=1 ORDER BY last_connect_time LIMIT 1" % (username)  # Assuming dbresult[1] contains the username
            vernemq_db_cursor.execute(sql)
            result = vernemq_db_cursor.fetchall()
        vernemq_db_cursor.close()
        vernemq_db_connection.close()
        client_id = result[0].get("client_id")
    except Exception as error:
        print("An exception occurred:", error)
        client_id = None

    return client_id

def setClientConnection(client_id):
    status = True
    try:
        vernemq_db_connection = mysql.connector.connect(**vernemq_db)
        vernemq_db_cursor = vernemq_db_connection.cursor()
        sql = "UPDATE vmq_auth_acl SET connected=1,last_connect_time=NOW() WHERE client_id='%s'" % (client_id)  # Assuming dbresult[1] contains the username
        vernemq_db_cursor.execute(sql)
        vernemq_db_connection.commit()
        vernemq_db_cursor.close()
        vernemq_db_connection.close()
    except:
        status = False

    return status