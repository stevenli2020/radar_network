import mysql.connector
from user.config import config
from datetime import datetime, timedelta

from collections import defaultdict


config = config()


def auth(data):
    sql = (
        "SELECT * FROM USERS WHERE `LOGIN_NAME`='%s' AND `ID`='%s' AND `CODE`='%s' AND `TYPE`='%s'"
        % (data.get("Username"), data.get("ID"), data.get("CODE"), data.get("TYPE"))
    )
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute(sql)
    dbresult = cursor.fetchall()
    login = False
    admin = False
    if len(dbresult) == 0:
        login = False
        admin = False
    cursor.close()
    connection.close()
    if data.get("TYPE") == 0:
        login = True
        admin = False
    elif data.get("TYPE") in [1, 2]:
        login = True
        admin = True
    return login, admin


def is_superadmin(data):
    if data.get("TYPE") == 2:
        return True
    return False


def signIn(data):
    result = defaultdict(list)
    if data["LOGIN_NAME"] == "":
        result["ERROR"].append({"Username": "Username is Empty!"})
    if data["PWD"] == "":
        result["ERROR"].append({"PWD": "Password is Empty!"})

    sql = "SELECT ID, LOGIN_NAME, PWD, CODE, TYPE FROM USERS WHERE LOGIN_NAME='%s'" % (
        data["LOGIN_NAME"]
    )
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    if not dbresult:
        result["ERROR"].append({"Username": "Username is incorrect!"})
        return result
    if dbresult[2] != data["PWD"]:
        result["ERROR"].append({"PWD": "Password is incorrect!"})
    if len(result["ERROR"]):
        return result
    sql = "UPDATE USERS SET STATUS='%s' WHERE LOGIN_NAME='%s'" % (2, data["LOGIN_NAME"])
    cursor.execute(sql)
    connection.commit()
    result["DATA"].append(
        {
            "ID": dbresult[0],
            "Username": dbresult[1],
            "CODE": dbresult[3],
            "TYPE": dbresult[4],
        }
    )
    cursor.close()
    connection.close()
    return result


def signOut(data):
    result = defaultdict(list)
    if data["ID"] == "":
        result["ERROR"].append({"ID": "ID is Empty!"})
    if data["CODE"] == "":
        result["ERROR"].append({"CODE": "Code is Empty!"})

    sql = "SELECT * FROM USERS WHERE ID='%s' AND CODE='%s'" % (data["ID"], data["CODE"])
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    if not dbresult:
        result["ERROR"].append({"User": "User not found!"})
        return result
    if len(result["ERROR"]):
        return result
    sql = "UPDATE USERS SET STATUS='%s' WHERE ID='%s'" % (3, data["ID"])
    cursor.execute(sql)
    connection.commit()
    result["DATA"].append({"CODE": 0})
    cursor.close()
    connection.close()
    return result
