import os
import paho.mqtt.client as paho
import time
import datetime
import json

broker = '143.198.199.16'
port = 1883
topic = "/GMT/DEV/TEST/JSON"
client_id = f'1236'
username = 'js-client3'
password = 'c764eb2b5fa2d259dc667e2b9e195218'

def generate_random_payload(size):
    return os.urandom(size).hex()

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

def publish(id,client):
  # Example usage:
  size = 1024 * 128  # size in bytes
  payload = generate_random_payload(size)
  print(f"Payload size: {len(payload)} bytes")
  msg = json.dumps({"id":str(id) + "-5","data": payload})
  result = client.publish(topic, msg)
  status = result[0]
  if status == 0:
    print(f"Send `{id}` to topic `{topic}`")
  else:
    print(f"Failed to send message to topic {topic}")

def run():
  client = connect_mqtt()
  client.loop_start()
  for i in range(100):
    publish(i,client)
    if (i%10 == 0):
      time.sleep(5)
  client.loop_stop()

if __name__ == '__main__':
  run()