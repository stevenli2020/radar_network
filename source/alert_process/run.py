import paho.mqtt.client as paho
import time
import mysql.connector
import json

broker = '143.198.199.16'
port = 1883
sub_topic = "/GMT/DEV/+/ALERT"
pub_topic = "/GMT/DEV/ROOM/ROOM_UUID/ALERT"
client_id = f'1237'
username = 'py-client1'
password = 'c764eb2b5fa2d259dc667e2b9e195218'

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
    # 'user': 'root',
    # 'password': '14102022',
    # 'host': 'localhost',
    # 'port': '2203',
    # 'database': 'Gaitmetrics'
}

def get_room_uuid_by_mac(mac):
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    print(mac)
    sql = f"SELECT rd.ID,rrm.ROOM_UUID FROM RL_ROOM_MAC rrm LEFT JOIN ROOMS_DETAILS rd ON rrm.ROOM_UUID=rd.ROOM_UUID WHERE rrm.MAC='{mac}';"
    cursor.execute(sql)
    rooms = cursor.fetchall()
    cursor.close()
    connection.close()  
    return rooms[0]

def insert_alert(room_id,msg):
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = f"""INSERT INTO ALERT (ROOM_ID,URGENCY,TYPE,DETAILS) VALUES ('{room_id}','{msg["URGENCY"]}','{msg["TYPE"]}','{msg["DETAILS"]}');"""
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()  

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
        print(f"Received `{msg}` from `{curr_topic}` topic")
        parts = curr_topic.split('/')
        mac_value = parts[3]
        room_detail = get_room_uuid_by_mac(mac_value)
        insert_alert(room_detail["ID"],msg)
        real_topic = pub_topic.replace("ROOM_UUID",room_detail["ROOM_UUID"])
        result = client.publish(real_topic, "New alert")
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{real_topic}`")
        else:
            print(f"Failed to send message to topic {real_topic}")

    client.subscribe(sub_topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()