import mysql.connector
from user.config import config
from datetime import datetime, timedelta

from collections import defaultdict


config = config()

def addPassword(data):
    result = defaultdict(list)
    if data['LOGIN_NAME'] == '':
        result['ERROR'].append({'Username': 'Username is Empty!'})
    if data['PWD'] == '':
        result['ERROR'].append({'PWD': 'Password is Empty!'})
    if data['CPWD'] == '':
        result['ERROR'].append({'CPWD': 'Confirm Password is Empty!'})
    if data['CPWD'] != data['PWD']:
        result['ERROR'].append({'CPWD': 'Password must be same!'})
    if data['CODE'] == '':
        result['ERROR'].append({'Username': 'Unauthorized User!'})
    sql = "SELECT LOGIN_NAME, CODE, PWD FROM USERS WHERE CODE='%s'"%(data['CODE'])
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    print(dbresult)
    if dbresult[0] != data['LOGIN_NAME']:
        result['ERROR'].append({'Username': 'Username is incorrect!'})
    if dbresult[1] != data['CODE']:
        result['ERROR'].append({'Username': 'Unauthorized User!'})    
    if len(result['ERROR']):
        return result   
    sql = "UPDATE USERS SET PWD='%s', STATUS='%s' WHERE CODE='%s'"%(data['PWD'],1,data["CODE"])
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()
    result['CODE'] = 0
    return result