import mysql.connector
from user.config import config, vernemq, domain_url
from datetime import datetime, timedelta

from collections import defaultdict

config = config()
vernemq_db = vernemq()


def get_all_component_enablement():
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT ID, PAGE, COMPONENT, USER, ADMIN FROM COMPONENT_ENABLEMENT;"
    cursor.execute(sql)
    result["DATA"] = [
        {"ID": ID, "PAGE": PAGE, "COMPONENT": COMPONENT, "USER": USER, "ADMIN": ADMIN}
        for (ID, PAGE, COMPONENT, USER, ADMIN) in cursor
    ]
    cursor.close()
    connection.close()
    return result


def get_component_enablement(page, current_user):
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT PAGE, COMPONENT, USER, ADMIN FROM COMPONENT_ENABLEMENT WHERE PAGE = '{page}';"
    cursor.execute(sql)
    result = cursor.fetchall()
    components = {}
    for row in result:
        component = row.get("COMPONENT")
        user = row.get("USER")
        admin = row.get("ADMIN")
        if current_user.get("TYPE") == 0:
            components[component] = user == 1
        elif current_user.get("TYPE") == 1:
            components[component] = admin == 1
        else:
            components[component] = True
    cursor.close()
    connection.close()
    return components


def edit_component_enablement(data):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        delete_all_query = """
    DELETE FROM COMPONENT_ENABLEMENT
    """
        cursor.execute(delete_all_query)

        # Then, insert the new key-value pairs from the data dictionary
        insert_query = """
    INSERT INTO COMPONENT_ENABLEMENT (ID, PAGE, COMPONENT, USER, ADMIN)
    VALUES (%s, %s, %s, %s, %s)
    """
        for row in data:
            print(row)
            id = row.get("ID")
            page = row.get("PAGE")
            component = row.get("COMPONENT")
            user = row.get("USER")
            admin = row.get("ADMIN")
            cursor.execute(insert_query, (id, page, component, user, admin))

        connection.commit()
        return {"RESULT": True}
    except Exception as e:
        print(e)
        return {"RESULT": False, "ERROR": str(e)}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
