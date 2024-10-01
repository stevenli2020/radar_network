import schedule
import datetime
from datetime import datetime as dt,timedelta
import time
import mysql.connector
from pytz import timezone
import re
import random
import pandas as pd
import numpy as np
import requests
import smtplib
from email.mime.text import MIMEText

import constants

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}

vernemq = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'vernemq_db'
}

def get_user_token():
    username= "sam"
    password = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

    data = {
        'LOGIN_NAME': username,
        'PWD': password
    }

    response = requests.post(constants.DOMAIN_URL+"/api/login",json=data)

    # Handling the response
    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        return None
    
def get_room_summary(user,room_uuid):
    
    headers = {
        'Content-Type': 'application/json',  # Specify the content type if you're sending JSON
        'Authorization': 'Bearer ' + user['access_token']  # Example of how to include a token for authorization
    }
    
    data = {
        "ROOM_UUID": room_uuid,
        "CUSTOM": 0
    }

    for i in range(3):
        response = requests.post(constants.DOMAIN_URL + "/api/refreshAnalyticData", json=data, headers=headers)
        if response.status_code == 200:
            print("Success:", response.json())
            return
        else:
            print("Failed:", response.status_code, response.text)
            time.sleep(30)

def get_summary_data():
    user = get_user_token()
    if user:
        
        global config
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        sql = f"SELECT `ROOM_UUID` FROM ROOMS_DETAILS;"
        cursor.execute(sql)
        result = cursor.fetchall()
        for room in result:
            room_uuid = room["ROOM_UUID"]

            get_room_summary(user,room_uuid)

def check_ui():
    try:
        response = requests.get(constants.DOMAIN_URL)
        status_code = response.status_code
        return status_code == 200 or status_code == 502  # Check if status is OK
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False

def check_api():
    try:
        response = requests.get(constants.DOMAIN_URL + "/api/test")
        status_code = response.status_code
        return status_code == 200 or status_code == 502  # Check if status is OK
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False

def check_servers():
    recipients = get_notifier()
    ui_status = check_ui()
    api_status = check_api()

    if (not ui_status or not api_status):
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
        sentMail(recipients,"Aswelfarehome Servers Disconnected!",body)

def get_notifier():
    global config
    connection = mysql.connector.connect(**config)
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
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT r.ID,r.ROOM_NAME,d.MAC FROM DEVICES d left join RL_ROOM_MAC rrm on rrm.MAC=d.MAC left join ROOMS_DETAILS r on rrm.ROOM_UUID=r.ROOM_UUID WHERE d.STATUS='DISCONNECTED' AND r.ACTIVE=1;"
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

    if (len(result) > 0):
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
                <p>There are some devices are disconnected in active room. Please check it out! Below are the details:</p>
                <table>
                <tr>
                    <th>Room Name</th>
                    <th>Device</th>
                </tr>
                """ + table_content + """
                </table>
            </body>
            </html>
        """
        sentMail(recipients,"Aswelfarehome Devices Disconnected!",body)

sender_email = "www.gaitmetric.com.sg@gmail.com"
sender_password = "wolryshamgswgvzu"
# recipient_email = "recipient@gmail.com"
def sentMail(recipient, subject, body):
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = ",".join(recipient)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient, html_message.as_string())
    server.quit()

if __name__ == "__main__":
    schedule.every().hour.at(":15").do(get_summary_data)
    schedule.every().hour.at(":45").do(check_disconnected_devices)
    schedule.every(10).minutes.do(check_servers)

    while True:
        print(datetime.datetime.now(timezone("Asia/Singapore")))
        schedule.run_pending()
        time.sleep(30)