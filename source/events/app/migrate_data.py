import json
import time
import mysql.connector
from datetime import datetime

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}

def main():
  connection = mysql.connector.connect(**config)
  cursor = connection.cursor(dictionary=True)      

  dates = get_dates(connection,cursor)
  for date in dates:
    table_name = get_table_name(date)
    status = check_table_exist(connection,cursor,table_name)
    if not status:
      insert_new_table(connection,cursor,table_name,date)

  cursor.close()
  connection.close()   

def get_dates(connection,cursor):
  sql = "SELECT DISTINCT DATE_FORMAT(TIMESTAMP, '%Y_%m_%d') AS formatted_date FROM PROCESSED_DATA WHERE TIMESTAMP >= '2024-01-01';"
  cursor.execute(sql)
  data = cursor.fetchall()
  if data and len(data):
    dates = []
    for i in data:
      dates.append(i["formatted_date"])
    return dates
  return []

def insert_new_table(connection,cursor,table_name,date):
  sql = f"INSERT INTO {table_name} (SELECT NULL,`TIMESTAMP`,`MAC`,`TYPE`,`STATE`,OBJECT_COUNT,OBJECT_LOCATION,IN_BED,IN_BED_MOVING,HEART_RATE,BREATH_RATE,PX,PY,PZ,VX,VY,VZ,AX,AY,AZ FROM PROCESSED_DATA WHERE DATE_FORMAT(TIMESTAMP, '%Y_%m_%d') = '{date}');"
  cursor.execute(sql)
  connection.commit()
  # INSERT INTO PROCESSED_DATA_2024_05_08 (SELECT NULL,`TIMESTAMP`,`MAC`,`TYPE`,`STATE`,OBJECT_COUNT,OBJECT_LOCATION,IN_BED,IN_BED_MOVING,HEART_RATE,BREATH_RATE,PX,PY,PZ,VX,VY,VZ,AX,AY,AZ FROM PROCESSED_DATA_2024_05_07 WHERE DATE_FORMAT(TIMESTAMP, '%Y_%m_%d') = '2024_05_08');
  # DELETE FROM `PROCESSED_DATA_2024_05_07` WHERE DATE_FORMAT(TIMESTAMP, '%Y_%m_%d')='2024_05_08';

def get_table_name(date):
  table_name = f'PROCESSED_DATA_{date}'
  return table_name

def check_table_exist(connection,cursor,table_name):
  table_exists_query = f"SHOW TABLES LIKE '{table_name}'"
  cursor.execute(table_exists_query)
  table_exists = cursor.fetchone()

  # If table does not exist, create it
  if not table_exists:
    print("Creating table....")
    create_table_query = f"""
    CREATE TABLE {table_name} (
      `ID` int(11) NOT NULL AUTO_INCREMENT,
      `TIMESTAMP` timestamp NOT NULL DEFAULT current_timestamp(),
      `MAC` varchar(12) NOT NULL,
      `TYPE` tinyint(4) DEFAULT 0 COMMENT '0: undefined; 1: wall; 2: ceil; 3: vital ',
      `STATE` tinyint(4) DEFAULT NULL COMMENT '0: Moving, 1: Upright, 2: Laying, 3: Fall, 4: None, 5: Social',
      `OBJECT_COUNT` tinyint(4) NOT NULL DEFAULT 0,
      `OBJECT_LOCATION` tinyint(4) DEFAULT NULL COMMENT '0: out room, 1: in room',
      `IN_BED` tinyint(1) NOT NULL DEFAULT 0,
      `IN_BED_MOVING` tinyint(1) DEFAULT NULL,
      `HEART_RATE` float DEFAULT NULL,
      `BREATH_RATE` float DEFAULT NULL,
      `PX` float DEFAULT NULL,
      `PY` float DEFAULT NULL,
      `PZ` float DEFAULT NULL,
      `VX` float DEFAULT NULL,
      `VY` float DEFAULT NULL,
      `VZ` float DEFAULT NULL,
      `AX` float DEFAULT NULL,
      `AY` float DEFAULT NULL,
      `AZ` float DEFAULT NULL,
      PRIMARY KEY (`ID`),
      KEY `TIMESTAMP` (`TIMESTAMP`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs;
    """.format(table_name=table_name)
    cursor.execute(create_table_query)
    connection.commit()
    return False
  return True

main()
