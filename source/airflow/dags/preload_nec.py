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
