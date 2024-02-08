import mysql.connector
from user.config import config
from datetime import datetime, timedelta

from collections import defaultdict
from user.email.gmail import sentMail
from user.email.gmailTemplate import emailTemplate
import re
import hashlib

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

# SELECT ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS, CODE, LAST_UPDATE, CREATED, MAC FROM USERS JOIN RL_USER_MAC ON USERS.ID=RL_USER_MAC.USER_ID;

config = config()

def requestAllUsers():
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT USERS.ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, USERS.STATUS, CODE, LAST_UPDATE, CREATED, GROUP_CONCAT(ROOMS_DETAILS.ROOM_NAME) AS ROOM_NAME FROM Gaitmetrics.USERS LEFT JOIN Gaitmetrics.RL_USER_ROOM ON USERS.ID=RL_USER_ROOM.USER_ID LEFT JOIN Gaitmetrics.ROOMS_DETAILS ON RL_USER_ROOM.ROOM_ID=ROOMS_DETAILS.ID GROUP BY USERS.ID"
    cursor.execute(sql)
    result["DATA"] = [{"ID": ID, "LOGIN_NAME": LOGIN_NAME, "FULL_NAME": FULL_NAME, "EMAIL": EMAIL, "PHONE": PHONE, "TYPE": TYPE, "STATUS": STATUS, "CODE": CODE, "LAST_UPDATE": LAST_UPDATE, "CREATED": CREATED, "ROOM_NAME": ROOM_NAME} for (ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS,CODE, LAST_UPDATE, CREATED, ROOM_NAME) in cursor]
    cursor.close()
    connection.close()
    return result

def requestSpecificUser(data):
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    Id = data['USER_ID']
    sql = "SELECT USERS.ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, USERS.STATUS, CODE, LAST_UPDATE, CREATED, GROUP_CONCAT(ROOMS_DETAILS.ROOM_NAME) AS ROOM_NAME FROM Gaitmetrics.USERS LEFT JOIN Gaitmetrics.RL_USER_ROOM ON USERS.ID=RL_USER_ROOM.USER_ID LEFT JOIN Gaitmetrics.ROOMS_DETAILS ON RL_USER_ROOM.ROOM_ID=ROOMS_DETAILS.ID WHERE USERS.ID='%s' GROUP BY USERS.ID"%(Id)
    cursor.execute(sql)
    result["DATA"] = [{"ID": ID, "LOGIN_NAME": LOGIN_NAME, "FULL_NAME": FULL_NAME, "EMAIL": EMAIL, "PHONE": PHONE, "TYPE": TYPE, "STATUS": STATUS, "CODE": CODE, "LAST_UPDATE": LAST_UPDATE, "CREATED": CREATED, "ROOM_NAME": ROOM_NAME} for (ID, LOGIN_NAME, FULL_NAME, EMAIL, PHONE, TYPE, STATUS,CODE, LAST_UPDATE, CREATED, ROOM_NAME) in cursor]
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
    body = emailTemplate(data['LOGIN_NAME'], "http://143.198.199.16:5000/api/updatePassword?"+str(data['LOGIN_NAME'])+"&"+str(code)+"&add", "add")
    sentMail(data['EMAIL'], 'Account Created Successfully', body)
    if data['USER_TYPE'] == '0':
        sql = "SELECT * FROM Gaitmetrics.USERS WHERE LOGIN_NAME='%s'"%(data['LOGIN_NAME'])
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        # print(dbresult)
        if dbresult:
            id = dbresult[0]
            RoomList = str(data['ROOM']).split(',')
            # print(RoomList)
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
    sql = "SELECT * FROM Gaitmetrics.USERS WHERE ID='%s'"%(data['USER_ID'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    print(dbresult)
    if dbresult:
        if dbresult[1] != data['LOGIN_NAME']:
            sql = "SELECT * FROM Gaitmetrics.USERS WHERE LOGIN_NAME='%s'"%(data['LOGIN_NAME'])
            cursor.execute(sql)
            userresult = cursor.fetchone()
            if userresult:
                result['ERROR'].append({'Username': 'Username is taken'})
                return result     
        if dbresult[3] != data['EMAIL']:
            sql = "SELECT * FROM Gaitmetrics.USERS WHERE EMAIL='%s'"%(data['EMAIL'])
            cursor.execute(sql)
            emailresult = cursor.fetchone()
            if emailresult:
                result['ERROR'].append({'Email': 'Email is taken'})
                return result   
    sql = "UPDATE Gaitmetrics.USERS SET LOGIN_NAME='%s', FULL_NAME='%s', EMAIL='%s',PHONE='%s', TYPE='%s' WHERE ID='%s'"%(data['LOGIN_NAME'], data['FULL_NAME'], data['EMAIL'], data['PHONE'], data['USER_TYPE'], data['USER_ID'])
    cursor.execute(sql)
    connection.commit()
    sql = "DELETE FROM Gaitmetrics.RL_USER_ROOM WHERE USER_ID='%s'"%(data['USER_ID'])
    cursor.execute(sql)
    connection.commit()
    RoomList = str(data['ROOM']).split(',')
    for Room in RoomList:
        if (not Room):
            continue
        RoomName = Room.replace("'", "")
        RoomName = RoomName.replace("]", "")
        RoomName = RoomName.replace("[", "")
        # RoomName = RoomName.replace(" ", "")
        
        if RoomName[0] == " ":
            RoomName = RoomName[1:]
        if RoomName[-1] == " ":
            RoomName = RoomName[:-1]
        # print(RoomName)
        sql = "SELECT * FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_NAME='%s'"%(RoomName)
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        # print(dbresult)
        if dbresult:
            cursor.execute("INSERT INTO Gaitmetrics.RL_USER_ROOM (USER_ID, ROOM_ID) VALUES(%s, %s)", (data['USER_ID'], dbresult[0]))
            connection.commit()
    cursor.close()
    connection.close()
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
    result['DATA'].append({"CODE": 0})
    return result

