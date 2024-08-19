import paho.mqtt.client as paho
import sys
import time
import json

broker = '143.198.199.16'
port = 1883
topic = "/TEST"
client_id = f'1235'
username = 'js-client2'
password = 'c764eb2b5fa2d259dc667e2b9e195218'

# client_id="0002"
# username="decode-publish"  
# password="/-K3tuBhod3-FIzv"

def connect_mqtt() -> paho:
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print("Connected to MQTT Broker!")
    else:
      print("Failed to connect, return code %d\n", rc)

  client = paho.Client(client_id)
  client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client

def subscribe(client: paho):
  def on_message(client, userdata, msg):
    curr_topic = msg.topic
    msg = msg.payload.decode()
    msg = json.loads(msg)
    print(f"Received `{msg.get('id')}` from `{curr_topic}` topic")
  client.subscribe("/GMT/DEV/+/JSON")
  client.on_message = on_message

def run():
  client = connect_mqtt()
  subscribe(client)
  client.loop_forever()

if __name__ == '__main__':
    run()