from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
from pytz import timezone
import datetime as dtm
import pandas as pd
from datetime import datetime as dt, timedelta
import requests
import mysql.connector
import time
import smtplib
from email.mime.text import MIMEText

import constants
from constants import config

env = "aswelfarehome"


def get_user_token():
    username = "sam"
    password = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

    data = {"LOGIN_NAME": username, "PWD": password}

    response = requests.post(constants.domain_url(env) + "/api/login", json=data)

    # Handling the response
    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        return None


def get_room_summary(user, room_uuid):

    headers = {
        "Content-Type": "application/json",  # Specify the content type if you're sending JSON
        "Authorization": "Bearer "
        + user["access_token"],  # Example of how to include a token for authorization
    }

    data = {"ROOM_UUID": room_uuid, "CUSTOM": 0}

    for i in range(3):
        response = requests.post(
            constants.domain_url(env) + "/api/refreshAnalyticData",
            json=data,
            headers=headers,
        )
        if response.status_code == 200:
            print("Success:", response.json())
            return
        else:
            print("Failed:", response.status_code, response.text)
            time.sleep(30)


def get_summary_data():
    user = get_user_token()
    if user:

        connection = mysql.connector.connect(**config(env))
        cursor = connection.cursor(dictionary=True)
        sql = f"SELECT `ROOM_UUID` FROM ROOMS_DETAILS;"
        cursor.execute(sql)
        result = cursor.fetchall()
        for room in result:
            room_uuid = room["ROOM_UUID"]

            get_room_summary(user, room_uuid)


def check_ui():
    try:
        response = requests.get(constants.domain_url(env))
        status_code = response.status_code
        return status_code == 200 or status_code == 502  # Check if status is OK
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False


def check_api():
    try:
        response = requests.get(constants.domain_url(env) + "/api/test")
        status_code = response.status_code
        return status_code == 200 or status_code == 502  # Check if status is OK
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False


def check_servers():
    recipients = get_notifier()
    ui_status = check_ui()
    api_status = check_api()

    if not ui_status or not api_status:
        body = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
                }
                
                td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
                }
                
                tr:nth-child(even) {
                background-color: #dddddd;
                }
                </style>
            </head>
            <body>
                <p>The servers is down. Please check it out!</p>
            </body>
            </html>
        """
        sentMail(
            recipients, constants.server_name(env) + " Servers Disconnected!", body
        )


def get_notifier():

    connection = mysql.connector.connect(**config(env))
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT `EMAIL` FROM EMAIL_RECIPIENT;"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        data.append(row["EMAIL"])
    return data


def get_current_date():
    print(dtm.datetime.now())
    return str(dtm.datetime.now(timezone("Asia/Singapore"))).split(" ")[0]


def get_interval_tables(cursor, date):
    end_date = dt.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=1)

    return get_table_dates_between(
        cursor, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )


def get_table_dates_between(cursor, start_date_str, end_date_str):
    print(start_date_str, end_date_str)
    start_date = dt.strptime(start_date_str, "%Y-%m-%d")
    end_date = dt.strptime(end_date_str, "%Y-%m-%d")

    tables = []
    current_date = start_date

    while current_date <= end_date:
        table_name = "PROCESSED_DATA_" + current_date.strftime("%Y_%m_%d")
        if check_table_exist(cursor, table_name):
            tables.append("PROCESSED_DATA_" + current_date.strftime("%Y_%m_%d"))
        current_date += timedelta(days=1)

    return tables


def check_table_exist(cursor, table_name):
    table_exists_query = f"SHOW TABLES LIKE '{table_name}'"
    cursor.execute(table_exists_query)
    table_exists = cursor.fetchone()

    if not table_exists:
        return False
    return True


def check_wall_data_count():
    connection = mysql.connector.connect(**config(env))
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT ROOMS_DETAILS.ROOM_NAME, GROUP_CONCAT(DEVICES.MAC) AS MACS FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID LEFT JOIN Gaitmetrics.DEVICES ON RL_ROOM_MAC.MAC=DEVICES.MAC WHERE DEVICES.`TYPE` IN ('1','2') AND ROOMS_DETAILS.ACTIVE=1 GROUP BY ROOMS_DETAILS.ROOM_UUID;"
    cursor.execute(sql)
    dbresult = cursor.fetchall()

    curr = get_current_date()
    tables = get_interval_tables(cursor, curr)

    result = []

    for room in dbresult:
        room_name = room["ROOM_NAME"]
        print(room_name)
        try:
            db = room["MACS"].split(",")
            MAC_LIST = ""
            for MAC in db:
                if MAC_LIST != "":
                    MAC_LIST += ","
                MAC_LIST += f"""'{MAC}'"""
            List = f"IN ({MAC_LIST})"
        except Exception as e:
            print(e)

        dbresult = []

        for table in tables:
            try:
                sql = f"SELECT `TIMESTAMP`, 1 AS `WALL_DATA_COUNT` FROM Gaitmetrics.{table} WHERE MAC {List} AND `TIMESTAMP` >= NOW() - INTERVAL 60 MINUTE;"
                cursor.execute(sql)
                db_data = cursor.fetchall()
                if db_data:
                    dbresult += db_data
            except Exception as e:
                print("No data in", table)

        if not dbresult:
            print("No data")

        df = pd.DataFrame(dbresult, columns=["TIMESTAMP", "WALL_DATA_COUNT"])

        df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

        # Localize timestamps to the local timezone
        df["TIMESTAMP"] = df["TIMESTAMP"].dt.tz_localize("Asia/Singapore")

        # # Subtract 8 hours from each timestamp
        df["TIMESTAMP"] = df["TIMESTAMP"].dt.tz_convert("UTC")

        df.set_index("TIMESTAMP", inplace=True)

        df_resampled = df.resample("1Min").count()

        df_resampled.fillna(0, inplace=True)

        data_obj = {}
        for index, row in df_resampled.iterrows():
            t = int(index.timestamp())
            data_obj[t] = [round(row["WALL_DATA_COUNT"], 1)]

        new_query_data = []
        for t, d in data_obj.items():
            new_query_data.append(int(d[0]))

        if len(new_query_data) > 0:
            average = sum(new_query_data) / len(new_query_data)
            if average < 20:
                result.append({"ROOM_NAME": room_name, "AVERAGE": average})
        # else:
        #     result.append({"ROOM_NAME": room_name, "AVERAGE": "No Data!"})

    cursor.close()
    connection.close()

    table_content = ""

    for row in result:
        room_name = row["ROOM_NAME"]
        average = row["AVERAGE"]

        table_content += f"""
            <tr>
                <td>{room_name}</td>
                <td>{average}</td>
            </tr>
        """

    if len(result) > 0:
        print(result)
        recipients = get_notifier()
        body = (
            """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
                }

                td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
                }

                tr:nth-child(even) {
                background-color: #dddddd;
                }
                </style>
            </head>
            <body>
                <p>There are some active room do not have enough wall data. Please check it out! Below are the details:</p>
                <table>
                <tr>
                    <th>Room Name</th>
                    <th>Device</th>
                </tr>
                """
            + table_content
            + """
                </table>
            </body>
            </html>
        """
        )
        sentMail(
            recipients, constants.server_name(env) + " wall data insufficient!", body
        )


def check_disconnected_devices():
    recipients = get_notifier()

    connection = mysql.connector.connect(**config(env))
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT r.ID,r.ROOM_NAME,d.MAC FROM DEVICES d left join RL_ROOM_MAC rrm on rrm.MAC=d.MAC left join ROOMS_DETAILS r on rrm.ROOM_UUID=r.ROOM_UUID WHERE d.STATUS='DISCONNECTED' AND r.ACTIVE=1 AND d.`TYPE` <> '4';"
    cursor.execute(sql)
    result = cursor.fetchall()
    table_content = ""
    for row in result:
        room_name = row["ROOM_NAME"]
        mac = row["MAC"]

        table_content += f"""
            <tr>
                <td>{room_name}</td>
                <td>{mac}</td>
            </tr>
        """

    if len(result) > 0:
        body = (
            """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
                }
                
                td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
                }
                
                tr:nth-child(even) {
                background-color: #dddddd;
                }
                </style>
            </head>
            <body>
                <p>There are some devices are disconnected in active room. Please check it out! Below are the details:</p>
                <table>
                <tr>
                    <th>Room Name</th>
                    <th>Device</th>
                </tr>
                """
            + table_content
            + """
                </table>
            </body>
            </html>
        """
        )
        sentMail(
            recipients, constants.server_name(env) + " Devices Disconnected!", body
        )


sender_email = "www.gaitmetric.com.sg@gmail.com"
sender_password = "wolryshamgswgvzu"


def sentMail(recipient, subject, body):
    html_message = MIMEText(body, "html")
    html_message["Subject"] = subject
    html_message["From"] = sender_email
    html_message["To"] = ",".join(recipient)
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient, html_message.as_string())
    server.quit()


def notify_email(context):
    subject = f"Airflow alert: {context['task_instance'].task_id} Failed"
    body = f"""
  DAG: {context['task_instance'].dag_id}<br>
  Task: {context['task_instance'].task_id}<br>
  Execution Time: {context['execution_date']}<br>
  Log: <a href="{context['task_instance'].log_url}">Log</a>
  """
    send_email("mvplcw97@gmail.com", subject, body)


with DAG(
    dag_id="preload_dag_aswelfarehome",
    start_date=datetime(2024, 10, 12),
    schedule_interval="@hourly",
    catchup=False,
) as dag:
    get_summary_data_task = PythonOperator(
        task_id="GET_SUMMARY_DATA",
        python_callable=get_summary_data,
        on_failure_callback=notify_email,
    )

    check_devices_task = PythonOperator(
        task_id="CHECK_DEVICES",
        python_callable=check_disconnected_devices,
        on_failure_callback=notify_email,
    )

    check_wall_data_count_task = PythonOperator(
        task_id="CHECK_WALL_DATA",
        python_callable=check_wall_data_count,
        on_failure_callback=notify_email,
    )
