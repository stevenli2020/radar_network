import paho.mqtt.client as paho
import time
import mysql.connector
import json

broker = '143.198.199.16'
port = 1883
sub_topic1 = "/GMT/DEV/+/ALERT"
sub_topic2 = "/GMT/DEV/+/DATA/+/JSON"
pub_topic1 = "/GMT/DEV/ROOM/ROOM_UUID/ALERT"
pub_topic2 = "/GMT/DEV/ROOM/ROOM_UUID/BED_ANALYSIS"
pub_topic3 = "/GMT/DEV/ROOM/ROOM_UUID/HEART_RATE"
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

heart_abnormal = {

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

    check_sql = f"""
        SELECT COUNT(*) AS count
        FROM ALERT
        WHERE ROOM_ID = '{room_id}'
        AND URGENCY = '{msg["URGENCY"]}'
        AND TYPE = '{msg["TYPE"]}'
        AND DETAILS = '{msg["DETAILS"]}'
        AND TIMESTAMP >= NOW() - INTERVAL 15 SECOND
    """

    cursor.execute(check_sql)
    result = cursor.fetchone()

    # If there are no matching entries within the last 15 seconds, proceed with insertion
    if result['count'] == 0:
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
        if (parts[-1] == "ALERT"):
            insert_alert(room_detail["ID"],msg)
            real_topic = pub_topic1.replace("ROOM_UUID",room_detail["ROOM_UUID"])
            result = client.publish(real_topic, "New alert")
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{msg}` to topic `{real_topic}`")
            else:
                print(f"Failed to send message to topic {real_topic}")
        elif (parts[-1] == "JSON"):

            BED_ANALYSIS = {
                "IN_BED":False
            }
            any_bed_occupied = any(item.get('bedOccupancy') for item in msg['DATA'])

            if any_bed_occupied:
                BED_ANALYSIS["IN_BED"] = True
                print("At least one bed is occupied.")
                real_topic = pub_topic2.replace("ROOM_UUID",room_detail["ROOM_UUID"])
                result = client.publish(real_topic, json.dumps(BED_ANALYSIS))
            else:
                print("No beds are occupied.")

            heart_rates = [item.get('heartRate') for item in msg['DATA'] if item.get('heartRate') is not None]
            if (room_detail["ROOM_UUID"] not in heart_abnormal):
                heart_abnormal[room_detail["ROOM_UUID"]] = {
                    "alert": False,
                    "data":[]
                }
            if (len(heart_rates) > 0):
                abnormal = False
                print("HEART",heart_rates, room_detail["ROOM_UUID"] )
                for rate in heart_rates:
                    if (rate >= 110 or rate <= 45):
                        abnormal = True
                        heart_abnormal[room_detail["ROOM_UUID"]]["data"].append(rate)
                        # print(heart_abnormal)

                    real_topic = pub_topic3.replace("ROOM_UUID",room_detail["ROOM_UUID"])
                    client.publish(real_topic, rate)
                    break

                if (abnormal):
                    if (len(heart_abnormal[room_detail["ROOM_UUID"]]["data"]) > 3 and not heart_abnormal[room_detail["ROOM_UUID"]]["alert"]):
                        heart_abnormal[room_detail["ROOM_UUID"]]["alert"] = True

                        alert_msg = {
                            "URGENCY":"2",
                            "TYPE":"1",
                            "DETAILS":"Abnormal heart rate detected!"
                        }
                        print("Insert heart rate alert")
                        insert_alert(room_detail["ID"],alert_msg)
                        real_topic = pub_topic1.replace("ROOM_UUID",room_detail["ROOM_UUID"])
                        client.publish(real_topic, "New alert")
                else:
                    print("reset")
                    heart_abnormal[room_detail["ROOM_UUID"]] = {
                        "alert": False,
                        "data":[]
                    }


    client.subscribe(sub_topic1)
    client.subscribe(sub_topic2)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()