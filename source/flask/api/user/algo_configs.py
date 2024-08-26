import mysql.connector
from user.config import config, vernemq, domain_url
from datetime import datetime, timedelta

from collections import defaultdict

config = config()
vernemq_db = vernemq()

def get_algo_configs():
  result = defaultdict(list)
  data_dict = {}
  connection = mysql.connector.connect(**config)
  cursor = connection.cursor()
  sql = "SELECT CONFIG_KEY, VALUE FROM ALGO_CONFIGS ORDER BY CREATED_DATE;"
  cursor.execute(sql)
  data = [{"CONFIG_KEY": CONFIG_KEY, "VALUE": VALUE} for (CONFIG_KEY,VALUE) in cursor]
  for row in data:
    data_dict[row["CONFIG_KEY"]] = row["VALUE"]
  result["DATA"] = data_dict
  cursor.close()
  connection.close()
  return result

def add_algo_config(key,value):
  try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = f"INSERT INTO ALGO_CONFIGS (CONFIG_KEY,VALUE) VALUES ('{key}',{value});"
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

def update_algo_configs(data):
  try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    delete_all_query = """
    DELETE FROM ALGO_CONFIGS
    """
    cursor.execute(delete_all_query)

    # Then, insert the new key-value pairs from the data dictionary
    insert_query = """
    INSERT INTO ALGO_CONFIGS (CONFIG_KEY, VALUE)
    VALUES (%s, %s)
    """
    for row in data:
      key = row.get("CONFIG_KEY")
      value = row.get("VALUE")
      cursor.execute(insert_query, (key, value))

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

def delete_algo_config(key):
  try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    delete_query = """
    DELETE FROM ALGO_CONFIGS
    WHERE CONFIG_KEY = %s
    """
    cursor.execute(delete_query, (key,))
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