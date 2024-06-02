import mysql.connector
from user.config import config
from collections import defaultdict
import uuid
import os
import pytz
from tzlocal import get_localzone

config = config()

def get_data_types():
  try:
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT `ID`, `DATA_KEY`, `DATA_LABEL` FROM Gaitmetrics.UTILS_DATA_TYPE"
    cursor.execute(sql)
    result["DATA"] = [{"ID": ID, "value": DATA_KEY, "label": DATA_LABEL} for (ID, DATA_KEY, DATA_LABEL) in cursor]
    cursor.close()
    connection.close()
    return result
  except:
    return None
  
def get_alert_configurations():
  try:
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT `ID`, `DATA_TYPE`,`MODE`,`MIN_DATA_POINT`,`MAX_DATA_POINT`,`THRESHOLD` FROM Gaitmetrics.ALERT_CONFIGS"
    cursor.execute(sql)
    result["DATA"] = [{"ID": ID, "DATA_TYPE": DATA_TYPE, "MODE": MODE, "MIN_DATA_POINT":MIN_DATA_POINT, "MAX_DATA_POINT":MAX_DATA_POINT, "THRESHOLD":THRESHOLD} for (ID, DATA_TYPE,MODE,MIN_DATA_POINT,MAX_DATA_POINT,THRESHOLD) in cursor]
    cursor.close()
    connection.close()
    return result
  except:
    return None
  
def set_alert_configurations(data):
  try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    sql = f"DELETE FROM `ALERT_CONFIGS`;"
    cursor.execute(sql)   
    connection.commit() 
    
    for row in data:
      sql = f"""INSERT INTO `ALERT_CONFIGS` (`DATA_TYPE`,`MODE`,`MIN_DATA_POINT`,`MAX_DATA_POINT`,`THRESHOLD`) VALUES ('{row["DATA_TYPE"]}','{row["MODE"]}','{row["MIN_DATA_POINT"]}','{row["MAX_DATA_POINT"]}','{row["THRESHOLD"]}');"""
      cursor.execute(sql)   
      connection.commit() 
    cursor.close()
    connection.close()
    return {
      "RESULT": True
    }
  except Exception as e:
    print(e)
    return {
      "ERROR":str(e),
      "RESULT": False
    }