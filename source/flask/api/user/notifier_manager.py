import mysql.connector
from user.config import config, vernemq, domain_url
from datetime import datetime, timedelta

from collections import defaultdict

config = config()
vernemq_db = vernemq()

def get_notifier():
  result = defaultdict(list)
  connection = mysql.connector.connect(**config)
  cursor = connection.cursor()
  sql = "SELECT EMAIL FROM EMAIL_RECIPIENT;"
  cursor.execute(sql)
  result["DATA"] = [{"EMAIL": EMAIL} for (EMAIL) in cursor]
  cursor.close()
  connection.close()
  return result

def add_notifier(email):
  try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = f"INSERT INTO EMAIL_RECIPIENT (EMAIL) VALUES ('{email}');"
    cursor.execute(sql)
    connection.commit()
    return {
      "RESULT": True
    }
  except Exception as e:
    print(e)
    return {
      "RESULT": False,
      "ERROR": str(e)
    }
  finally:
    if cursor:
      cursor.close()
    if connection:
      connection.close()

def delete_notifier(email):
  try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    delete_query = """
    DELETE FROM EMAIL_RECIPIENT
    WHERE EMAIL = %s
    """
    cursor.execute(delete_query, (email,))
    connection.commit()
    if cursor.rowcount > 0:
      return {
          "RESULT": True,
          "MESSAGE": "Configuration deleted successfully."
      }
    else:
      return {
          "RESULT": False,
          "ERROR": "Configuration key not found."
      }

  except Exception as e:
    print(e)
    return {
        "RESULT": False,
        "ERROR": str(e)  # Return the error for debugging purposes
    }
  finally:
    if cursor:
      cursor.close()
    if connection:
      connection.close()