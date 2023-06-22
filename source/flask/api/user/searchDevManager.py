import mysql.connector
from user.config import config
from datetime import datetime, timedelta
from user.parseFrame import *
import pytz
import copy
from collections import defaultdict

config = config()


def searchDevDetail(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    sql = "SELECT MAC, NAME FROM DEVICES WHERE NAME LIKE CONCAT('%', %s, '%')"
    cursor.execute(sql, (data['VALUE'],))   
    result["DATA"] = [{"MAC": MAC, "NAME": NAME} for (MAC, NAME) in cursor]
    cursor.close()
    connection.close()
    return result



