import mysql.connector
from user.config import config


config = config()

def createTable(dbName):
    connection = mysql.connector.connect(**config)
    # cursor = connection.cursor("CREATE TABLE IF NOT EXISTS %s (ID int NOT Null AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) CURRENT_TIMESTAMP(6), X json, Y json, Z json)",(dbName))
    # connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS "+dbName+" (ID INT AUTO_INCREMENT PRIMARY KEY, TIMESTAMP timestamp(6) DEFAULT CURRENT_TIMESTAMP(6), X json, Y json, Z json)")
    connection.commit()
    cursor.close()
    connection.close()