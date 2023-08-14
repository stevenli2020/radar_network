import mysql.connector
from user.config import config, vernemq
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

config = config()

def getLaymanData(req):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    sql = "SELECT * FROM Gaitmetrics.DEVICES"
    cursor.execute(sql)
    result["DATA"] = [{"MAC": MAC} for (MAC) in cursor]
    
    cursor.close()
    connection.close()
    return result
