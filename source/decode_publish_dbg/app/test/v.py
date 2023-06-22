import json
import time
import mysql.connector
from collections import defaultdict

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}

def getHistOfVitalData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)    
    sql = "SELECT GROUP_CONCAT(MAC) FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID WHERE ROOMS_DETAILS.ROOM_UUID ='%s'" % (data["ROOM_UUID"])
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    # print(dbresult)   
    try:
        db = dbresult[0].split(',')
        List = "IN ('"+db[0]+"','"+db[1]+"')"
    except:
        # print("No data related to room name")
        result["ERROR"].append({'Message': 'No data related to room name!'})
        return result
    sql = "SELECT DATE_FORMAT(TIMESTAMP, \'%%Y-%%m-%%d %%H:%%i\') AS T, ROUND(AVG(HEART_RATE),1) AS HR, ROUND(AVG(BREATH_RATE),1) AS BR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s) AND HEART_RATE IS NOT NULL AND HEART_RATE !=0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE !=0 GROUP BY T ORDER BY `T` ASC;" %(List, data['TIME'])
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        return result
    result['DATA'].append(dbresult)
    # sql = "SELECT ROUND(AVG(HEART_RATE), 2) as HEART_RATE, ROUND(AVG(BREATH_RATE), 2) as BREATH_RATE FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND HEART_RATE > 0 AND TIMESTAMP BETWEEN NOW() - INTERVAL %s AND NOW()"%(data['DEVICEMAC'], data['TIME'])
    # cursor.execute(sql)
    # dbresult = cursor.fetchone() 
    # result["AVG"].append(dbresult)
    cursor.close()
    connection.close()
    return result
    
DATA = {'ROOM_UUID':'d32231684bd3470b9b0a86dc0b9df524','TIME':'1 DAY'}
print(getHistOfVitalData(DATA))  