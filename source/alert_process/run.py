import paho.mqtt.client as paho
import time
import mysql.connector
import json
from datetime import datetime, timedelta
import pendulum

broker = "143.198.199.16"
port = 1883
sub_topic1 = "/GMT/DEV/+/ALERT"
sub_topic2 = "/GMT/DEV/+/EXTRA_DATA/+/JSON"
pub_topic1 = "/GMT/DEV/ROOM/ROOM_UUID/ALERT"
pub_topic2 = "/GMT/DEV/ROOM/ROOM_UUID/BED_ANALYSIS"
pub_topic3 = "/GMT/DEV/ROOM/ROOM_UUID/HEART_RATE"
client_id = f"1237"
username = "py-client1"
password = "c764eb2b5fa2d259dc667e2b9e195218"

config = {
    "user": "flask",
    "password": "CrbI1q)KUV1CsOj-",
    "host": "db",
    "port": "3306",
    "database": "Gaitmetrics",
    # 'user': 'root',
    # 'password': '14102022',
    # 'host': 'localhost',
    # 'port': '2203',
    # 'database': 'Gaitmetrics'
}

heart_abnormal = {}

sign_of_life = {}

sign_of_life_2 = {}

last_data = {}

occupied = {}

first_occupied_ts = {}


def get_room_uuid_by_mac(mac):
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    print(mac)
    sql = f"SELECT rd.ID,rrm.ROOM_UUID,rd.STATUS FROM RL_ROOM_MAC rrm LEFT JOIN ROOMS_DETAILS rd ON rrm.ROOM_UUID=rd.ROOM_UUID WHERE rrm.MAC='{mac}';"
    cursor.execute(sql)
    rooms = cursor.fetchall()
    cursor.close()
    connection.close()
    return rooms[0]


def insert_alert(room_id, msg):
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
    if result["count"] == 0:
        sql = f"""INSERT INTO ALERT (ROOM_ID,URGENCY,TYPE,DETAILS) VALUES ('{room_id}','{msg["URGENCY"]}','{msg["TYPE"]}','{msg["DETAILS"]}');"""
        cursor.execute(sql)
        connection.commit()
    cursor.close()
    connection.close()


def connect_mqtt() -> paho:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            subscribe(client)
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
        parts = curr_topic.split("/")
        mac_value = parts[3]
        room_detail = get_room_uuid_by_mac(mac_value)
        if parts[-1] == "ALERT":
            insert_alert(room_detail["ID"], msg)
            real_topic = pub_topic1.replace("ROOM_UUID", room_detail["ROOM_UUID"])
            result = client.publish(real_topic, "New alert", qos=1)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{msg}` to topic `{real_topic}`")
            else:
                print(f"Failed to send message to topic {real_topic}")
        elif parts[-1] == "JSON":
            all_zero = True
            sol = False

            all_zero_mode_2 = True
            mode_2 = False

            room_status = room_detail.get("STATUS")
            within_period = check_should_sol(room_detail["ID"])

            if room_status in [1, 2] and within_period:
                if not first_occupied_ts.get(room_detail["ROOM_UUID"]):
                    first_occupied_ts[room_detail["ROOM_UUID"]] = msg["DATA"][0][
                        "timeStamp"
                    ]
            else:
                if first_occupied_ts.get(room_detail["ROOM_UUID"]):
                    del first_occupied_ts[room_detail["ROOM_UUID"]]

            if first_occupied_ts.get(room_detail["ROOM_UUID"]):
                if check_sol_threshold(
                    first_occupied_ts.get(room_detail["ROOM_UUID"]),
                    msg["DATA"][0]["timeStamp"],
                    3 * 60,
                ):
                    occupied[room_detail["ROOM_UUID"]] = True

            if not within_period:
                if occupied.get(room_detail["ROOM_UUID"]):
                    del occupied[room_detail["ROOM_UUID"]]

                if first_occupied_ts.get(room_detail["ROOM_UUID"]):
                    del first_occupied_ts[room_detail["ROOM_UUID"]]

            if last_data.get(room_detail["ROOM_UUID"]):
                if check_sol_threshold(
                    last_data.get(room_detail["ROOM_UUID"]),
                    msg["DATA"][0]["timeStamp"],
                    3 * 60,
                ):
                    del last_data[room_detail["ROOM_UUID"]]

            for item in msg["DATA"]:
                if item.get("signOfLife") != 0:
                    all_zero = False

                    if item.get("signOfLife") == 1:
                        sol = True

                if item.get("pointCloudDetected", 1) != 0:
                    mode_2 = True
                    all_zero_mode_2 = False

            if (
                all_zero_mode_2
                and within_period
                and occupied.get(room_detail["ROOM_UUID"], False)
            ):
                if sign_of_life_2.get(room_detail["ROOM_UUID"]):
                    if check_sol_threshold(
                        sign_of_life_2[room_detail["ROOM_UUID"]],
                        msg["DATA"][0]["timeStamp"],
                        threshold=120,
                    ):
                        alert_msg = {
                            "URGENCY": "3",
                            "TYPE": "1",
                            "DETAILS": "No Sign of Life! - Mode 2",
                        }
                        print("Insert SOL mode 2 alert")
                        insert_alert(room_detail["ID"], alert_msg)
                        if occupied.get(room_detail["ROOM_UUID"]):
                            del occupied[room_detail["ROOM_UUID"]]
                        if sign_of_life_2.get(room_detail["ROOM_UUID"]):
                            del sign_of_life_2[room_detail["ROOM_UUID"]]

                else:
                    sign_of_life_2[room_detail["ROOM_UUID"]] = msg["DATA"][0][
                        "timeStamp"
                    ]

            if mode_2 or not check_should_sol(room_detail["ID"]):
                if sign_of_life_2.get(room_detail["ROOM_UUID"]):
                    del sign_of_life_2[room_detail["ROOM_UUID"]]

            if all_zero:
                if sign_of_life.get(room_detail["ROOM_UUID"]):
                    if check_sol_threshold(
                        sign_of_life[room_detail["ROOM_UUID"]],
                        msg["DATA"][0]["timeStamp"],
                    ):
                        alert_msg = {
                            "URGENCY": "3",
                            "TYPE": "1",
                            "DETAILS": "No Sign of Life! - Mode 1",
                        }
                        print("Insert heart rate alert")
                        insert_alert(room_detail["ID"], alert_msg)
                else:
                    sign_of_life[room_detail["ROOM_UUID"]] = msg["DATA"][0]["timeStamp"]

            if sol:
                if sign_of_life.get(room_detail["ROOM_UUID"]):
                    del sign_of_life[room_detail["ROOM_UUID"]]

            BED_ANALYSIS = {"IN_BED": False}
            any_bed_occupied = any(item.get("bedOccupancy") for item in msg["DATA"])

            if any_bed_occupied:
                BED_ANALYSIS["IN_BED"] = True
                print("At least one bed is occupied.")
                real_topic = pub_topic2.replace("ROOM_UUID", room_detail["ROOM_UUID"])
                result = client.publish(real_topic, json.dumps(BED_ANALYSIS), qos=1)
            else:
                print("No beds are occupied.")

            heart_rates = [
                item.get("heartRate")
                for item in msg["DATA"]
                if item.get("heartRate") is not None
            ]
            if room_detail["ROOM_UUID"] not in heart_abnormal:
                heart_abnormal[room_detail["ROOM_UUID"]] = {"alert": False, "data": []}
            if len(heart_rates) > 0:
                abnormal = False
                print("HEART", heart_rates, room_detail["ROOM_UUID"])
                for rate in heart_rates:
                    if rate >= 110 or rate <= 45:
                        abnormal = True
                        heart_abnormal[room_detail["ROOM_UUID"]]["data"].append(rate)
                        # print(heart_abnormal)

                    real_topic = pub_topic3.replace(
                        "ROOM_UUID", room_detail["ROOM_UUID"]
                    )

                    room_data = {
                        "HEART_RATE": rate,
                        "STATUS": get_room_status(room_detail["ROOM_UUID"]),
                    }

                    client.publish(real_topic, json.dumps(room_data), qos=1)
                    break

                if abnormal:
                    if (
                        len(heart_abnormal[room_detail["ROOM_UUID"]]["data"]) > 3
                        and not heart_abnormal[room_detail["ROOM_UUID"]]["alert"]
                    ):
                        heart_abnormal[room_detail["ROOM_UUID"]]["alert"] = True

                        alert_msg = {
                            "URGENCY": "2",
                            "TYPE": "1",
                            "DETAILS": "Abnormal heart rate detected!",
                        }
                        print("Insert heart rate alert")
                        insert_alert(room_detail["ID"], alert_msg)
                        real_topic = pub_topic1.replace(
                            "ROOM_UUID", room_detail["ROOM_UUID"]
                        )
                        client.publish(real_topic, "New alert", qos=1)
                else:
                    print("reset")
                    heart_abnormal[room_detail["ROOM_UUID"]] = {
                        "alert": False,
                        "data": [],
                    }

            last_data[room_detail["ROOM_UUID"]] = msg["DATA"][0]["timeStamp"]

    client.subscribe(sub_topic1)
    client.subscribe(sub_topic2)
    client.on_message = on_message


def check_sol_threshold(first_ts, curr_ts, threshold=60):
    first_dt = datetime.fromtimestamp(float(first_ts))
    curr_dt = datetime.fromtimestamp(float(curr_ts))

    difference = curr_dt - first_dt

    return difference > timedelta(seconds=threshold)


def run():
    client = connect_mqtt()
    # subscribe(client)
    client.loop_forever()


def get_room_status(room_uuid):
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT STATUS FROM ROOMS_DETAILS WHERE ROOM_UUID='{room_uuid}';"
    cursor.execute(sql)
    records = cursor.fetchall()
    if records and len(records) > 0:
        return int(records[0]["STATUS"])

    return 0


def check_should_sol(room_id):
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = (
        f"SELECT START_TIME, END_TIME FROM ALERT_TIME_RANGE WHERE ROOM_ID='{room_id}';"
    )
    cursor.execute(sql)
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    if records and len(records) > 0:
        start_time = records[0].get("START_TIME")
        end_time = records[0].get("END_TIME")
        if within_time_range(start_time, end_time):
            return True
        return False

    return False


def within_time_range(start_time_str, end_time_str):
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()

    singapore_tz = pendulum.timezone("Asia/Singapore")
    current_time = datetime.now(singapore_tz).time()

    if start_time < end_time:
        is_within_range = start_time <= current_time <= end_time
    else:
        is_within_range = current_time >= start_time or current_time <= end_time

    return is_within_range


if __name__ == "__main__":
    run()
