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
client_id = f'1236'
username = 'js-client3'
password = 'c764eb2b5fa2d259dc667e2b9e195218'

def trigger_alert(data):
  connection = mysql.connector.connect(**config)
  cursor = connection.cursor(dictionary=True)
  result = defaultdict(list)
  sql = "SELECT MAC FROM Gaitmetrics.RL_ROOM_MAC WHERE ROOM_UUID=%s"
  cursor.execute(sql, (data['ROOM_UUID'],))   
  MACS = cursor.fetchall()
  if (len(MACS)>0):
    result = {"DATA": 'Alert sent!'}
    mac = MACS[0].get("MAC")
    curr_topic = f"/GMT/DEV/{mac}/ALERT"
    curr_alert = {
      "TIMESTAMP":time.time(),
      "URGENCY":data['URGENCY'],
      "TYPE":data['TYPE'],
      "DETAILS":data['DETAILS']
    }
    send_mqtt(curr_alert,curr_topic)
  else:
    result = {"ERROR": 'No device'}
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

def publish(client,msg,topic):
  msg = json.dumps(msg)
  result = client.publish(topic, msg, qos=1)
  # result: [0, 1]
  status = result[0]
  if status == 0:
      print(f"Send `{msg}` to topic `{topic}`")
  else:
      print(f"Failed to send message to topic {topic}")

def send_mqtt(msg,topic):
  client = connect_mqtt()
  client.loop_start()
  publish(client,msg,topic)
  client.loop_stop()