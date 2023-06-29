import json  
import time
from getdata import * 
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
    result = getVitalData(connection, data)
    return result
    
def getSummaryDataofPosition(data):
    connection = mysql.connector.connect(**config)
    result = getPositionData(connection, data)
    return result    
    
    
def getAnalyticDataofPosture(data):
    connection = mysql.connector.connect(**config)
    result = getPostureData(connection, data)
    return result  
    
# DATA = {'ROOM_UUID':'d32231684bd3470b9b0a86dc0b9df524','TIME':'1 DAY'}
# print(getHistOfVitalData(DATA))  

# DATA = {'DEVICEMAC':'F412FAE26208','TIME':'DAY'}   
# print(getSummaryDataofPosition(DATA)["DATA"][0])  
 
DATA = {'ROOM_UUID':'e06ad8b752764b19ae832aaac1330285','TIME':'DAY'}   
print(getAnalyticDataofPosture(DATA)) 