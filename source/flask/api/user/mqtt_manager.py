import mysql.connector
from user.config import config, server_ip
from collections import defaultdict
import uuid
import os
import pytz
from tzlocal import get_localzone
import paho.mqtt.client as paho
import time
import datetime
import json

config = config()
broker = server_ip()
port = 1883
alert_topic = "/GMT/DEV/[MAC]/ALERT"
client_id = f"1236"
username = "js-client3"
password = "c764eb2b5fa2d259dc667e2b9e195218"


def trigger_alert(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    sql = "SELECT ID FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID=%s"
    cursor.execute(sql, (data["ROOM_UUID"],))
    ROOMS = cursor.fetchall()
    if len(ROOMS) > 0:
        result = {"DATA": "Alert sent!"}
        room_uuid = data["ROOM_UUID"]
        room_id = ROOMS[0].get("ID")
        urgency = data["URGENCY"]
        atype = data["TYPE"]
        details = data["DETAILS"]

        check_sql = f"""
        SELECT COUNT(*) AS count
        FROM ALERT
        WHERE ROOM_ID = '{room_id}'
        AND URGENCY = '{urgency}'
        AND TYPE = '{atype}'
        AND DETAILS = '{details}'
        AND TIMESTAMP >= NOW() - INTERVAL 15 SECOND
    """

        cursor.execute(check_sql)
        result = cursor.fetchone()

        # If there are no matching entries within the last 15 seconds, proceed with insertion
        if result["count"] == 0:
            sql = f"""INSERT INTO ALERT (ROOM_ID,URGENCY,TYPE,DETAILS) VALUES ('{room_id}','{urgency}','{atype}','{details}');"""
            cursor.execute(sql)
            connection.commit()

            pub_topic1 = "/GMT/DEV/ROOM/ROOM_UUID/ALERT"
            real_topic = pub_topic1.replace("ROOM_UUID", room_uuid)
            send_mqtt(1, real_topic)
    else:
        result = {"ERROR": "No device"}

    cursor.close()
    connection.close()
    return result


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = paho.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg, topic):
    msg = json.dumps(msg)
    result = client.publish(topic, msg, qos=1)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def send_mqtt(msg, topic):
    client = connect_mqtt()
    client.loop_start()
    publish(client, msg, topic)
    client.loop_stop()
