from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
import requests
import mysql.connector
import time
import smtplib
from email.mime.text import MIMEText

import constants
from constants import config

env = "nec"


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
    dag_id="preload_dag_nec",
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

