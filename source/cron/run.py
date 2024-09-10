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

class ALERT:
    message = {
            "in_room":{
                "day":"Duration in room abnormal - [DATA]",
                "weekday":"Duration in room abnormal (Weekday) - [DATA]"
            },
            "time_in_bed":{
                "day":"Duration in bed abnormal - [DATA]",
                "weekday":"Duration in bed abnormal (Weekday) - [DATA]"
            },
            "heart_rate":{
                "day":"Heart rate abnormal - [DATA]",
                "weekday":"Heart rate abnormal (Weekday) - [DATA]"
            },
            "breath_rate":{
                "day":"Breath rate abnormal - [DATA]",
                "weekday":"Breath rate abnormal (Weekday) - [DATA]"
            },
            "sleeping_hour":{
                "day":"Sleeping hour abnormal - [DATA]",
                "weekday":"Sleeping hour abnormal (Weekday) - [DATA]"
            },
            "sleep_disruption":{
                "day":"Sleeping disruption abnormal - [DATA]",
                "weekday":"Sleeping disruption abnormal (Weekday) - [DATA]"
            },
            "disrupt_duration":{
                "day":"Sleep disrupt duration abnormal - [DATA]",
                "weekday":"Sleep disrupt duration abnormal (Weekday) - [DATA]"
            },
            "wake_up_time":{
                "day":"Wake up time abnormal - [DATA]",
                "weekday":"Wake up time abnormal (Weekday) - [DATA]"
            },
            "bed_time":{
                "day":"Bed time abnormal - [DATA]",
                "weekday":"Bed time abnormal (Weekday) - [DATA]"
            }
        }

    data_type = {
            "in_room":"text",
            "time_in_bed":"text",
            "heart_rate":"float",
            "breath_rate":"flaot",
            "sleeping_hour":"text",
            "sleep_disruption":"float",
            "disrupt_duration":"text",
            "wake_up_time":"time",
            "bed_time":"time",
        }

def weighted_moving_average(data, weights):
    return np.average(data, weights=weights)

def weighted_std(data, weights):
    average = np.average(data, weights=weights)
    variance = np.average((data - average)**2, weights=weights)
    return np.sqrt(variance)

def is_abnormal(value, data, threshold=2):
    # Generate weights: more recent data has higher weights
    weights = np.arange(1, len(data)*5 + 1,step=5)
    
    # Calculate the weighted moving average and weighted standard deviation
    wma = weighted_moving_average(data, weights)
    wstd = weighted_std(data, weights)
    
    # Determine if the value is abnormal
    if abs(value - wma) > threshold * wstd:
        return True
    else:
        return False

def get_interval_tables(cursor,date):
    end_date = dt.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=6)

    return get_table_dates_between(cursor,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d")), start_date

def get_table_dates_between(cursor,start_date_str, end_date_str):
    print(start_date_str,end_date_str)
    start_date = dt.strptime(start_date_str, "%Y-%m-%d")
    end_date = dt.strptime(end_date_str, "%Y-%m-%d")
    
    tables = []
    current_date = start_date
    
    while current_date <= end_date:
        table_name = "PROCESSED_DATA_"+current_date.strftime("%Y_%m_%d")
        if (check_table_exist(cursor,table_name)):
            tables.append("PROCESSED_DATA_"+current_date.strftime("%Y_%m_%d"))
        current_date += timedelta(days=1)
    
    return tables

def check_table_exist(cursor,table_name):
    table_exists_query = f"SHOW TABLES LIKE '{table_name}'"
    cursor.execute(table_exists_query)
    table_exists = cursor.fetchone()

    if not table_exists:
        return False
    return True

def get_data_by_date_and_key(date,key,room_id):
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT `VALUE` FROM ANALYSIS_DAY WHERE `DATE`='{date}' AND `ROOM_ID`='{room_id}' AND `TYPE`='{key}' LIMIT 1;"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    connection.close()  

    if result and len(result) > 0:
        data = result[0]["VALUE"]
    else:
        data = None

    return data 

def get_rooms():
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT ID,ROOM_UUID FROM ROOMS_DETAILS;"
    cursor.execute(sql)
    rooms = cursor.fetchall()
    cursor.close()
    connection.close()  

    return rooms 

def analyse_position_data(data):
    date_format = "%Y-%m-%d %H:%M"
    in_room_min = 0
    laying_min = 0
    upright_min = 0
    moving_min = 0
    social_min = 0
    unknown = 0
    for row in data:
        row["MINUTE"] = dt.strptime(row["MINUTE"], date_format)

        if row["IN_ROOM"] == 1:
            in_room_min += 1
            if row["IS_MOVING"] == 1:
                moving_min += 1
            elif row["IS_UPRIGHT"] == 1:
                upright_min += 1
            elif row["IS_LAYING"] == 1:
                laying_min += 1
            elif row["IS_SOCIAL"] == 1:
                social_min += 1
            else:
                unknown += 1
                
    return seconds_to_text(social_min*60),seconds_to_text(moving_min*60),seconds_to_text(upright_min*60),seconds_to_text(laying_min*60)

def getLaymanData(date,room_uuid):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sleeping_hour               = None
    bed_time                    = None
    wake_up_time                = None
    time_in_bed                 = None
    in_room                     = None
    sleep_disruption            = None
    breath_rate                 = None
    heart_rate                  = None

    disrupt_duration            = None

    current_sleeping_seconds    = None
    current_sleep_disruption    = None
    current_disrupt_duration    = None

    current_inbed_seconds       = None
    current_inroom_seconds      = None
    current_wake_time           = None
    current_bed_time            = None

    current_heart_rate          = None
    current_breath_rate         = None

    social_time                 = None
    moving_time                 = None 
    upright_time                = None 
    laying_time                 = None

    tables, start_date = get_interval_tables(cursor,date)
    if (len(tables)>0):
        combine_table = []
        for table in tables:
            combine_table.append(f"""SELECT tb.ID,tb.TIMESTAMP,tb.ROOM_UUID,tb.MAC,tb.TYPE,tb.STATE,tb.OBJECT_COUNT,
                                 tb.OBJECT_LOCATION,tb.IN_BED,tb.IN_BED_MOVING,tb.HEART_RATE,tb.BREATH_RATE FROM {table} tb 
                                 LEFT JOIN `RL_ROOM_MAC` irrm ON irrm.MAC = tb.MAC WHERE irrm.ROOM_UUID = '{room_uuid}' AND TIMESTAMP >= '{start_date}'""")
        combine_table_query = " UNION ".join(combine_table)
            
        sql = f"""
            SELECT DATE_FORMAT(pd.`TIMESTAMP`, '%Y-%m-%d %H:%i') AS `MINUTE`,
                MAX(CASE WHEN pd.`STATE` = 2 THEN 1 ELSE 0 END) AS `IS_LAYING`,
                (SUM(OBJECT_LOCATION)) > 0 AS 'IN_ROOM',
                (SUM(IN_BED)) > 0 AS 'IN_BED',
                MAX(CASE WHEN pd.`HEART_RATE` IS NOT NULL THEN 1 ELSE 0 END) AS `HAS_HEART_RATE`,
                MAX(CASE WHEN pd.`BREATH_RATE` IS NOT NULL THEN 1 ELSE 0 END) AS `HAS_BREATH_RATE`,
                pd.`TYPE`
            FROM ({combine_table_query}) pd
            LEFT JOIN `RL_ROOM_MAC` rrm ON rrm.MAC = pd.MAC
            WHERE rrm.ROOM_UUID = '{room_uuid}'
            GROUP BY `MINUTE`
            ORDER BY pd.`TIMESTAMP`;
        """

        # Execute the query with parameters
        cursor.execute(sql)
        processed_data = cursor.fetchall()
        if (processed_data):
            # sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate,disrupt_duration_result, current_sleeping_seconds, current_sleep_disruption, current_disrupt_duration = analyseLaymanData(processed_data,date)
            in_room, time_in_bed, sleeping_hour, bed_time, wake_up_time, sleep_disruption,disrupt_duration,\
                current_sleeping_seconds, current_sleep_disruption, current_disrupt_duration,\
                     current_inbed_seconds,current_inroom_seconds,current_wake_time,current_bed_time\
                          = analyseData(processed_data,date)

        sql = f"""
            SELECT DATE_FORMAT(pd.`TIMESTAMP`, '%Y-%m-%d %H:%i') AS `MINUTE`,pd.`HEART_RATE`,pd.`BREATH_RATE`
            FROM `RL_ROOM_MAC` rrm
            LEFT JOIN ({combine_table_query}) pd ON rrm.MAC = pd.MAC
            WHERE (pd.`HEART_RATE` IS NOT NULL OR pd.`BREATH_RATE` IS NOT NULL)
            AND rrm.ROOM_UUID = '{room_uuid}'
            ORDER BY pd.`TIMESTAMP`;
        """

        # Execute the query with parameters
        cursor.execute(sql)
        vital_data = cursor.fetchall()
        if (vital_data):
            breath_rate,heart_rate, current_breath_rate, current_heart_rate = analyseVitalData(vital_data,date)

        sql = f"""
            SELECT DATE_FORMAT(pd.`TIMESTAMP`, '%Y-%m-%d %H:%i') AS `MINUTE`,
                MAX(CASE WHEN pd.`OBJECT_COUNT` > 1 THEN 1 ELSE 0 END) AS `IS_SOCIAL`,
                MAX(CASE WHEN pd.`STATE` = 2 THEN 1 ELSE 0 END) AS `IS_LAYING`,
                MAX(CASE WHEN pd.`STATE` = 0 THEN 1 ELSE 0 END) AS `IS_MOVING`,
                MAX(CASE WHEN pd.`STATE` = 1 THEN 1 ELSE 0 END) AS `IS_UPRIGHT`,
                (SUM(OBJECT_LOCATION)) > 0 AS 'IN_ROOM'
            FROM (SELECT tb.* FROM {tables[-1]} tb LEFT JOIN `RL_ROOM_MAC` irrm ON irrm.MAC = tb.MAC WHERE irrm.ROOM_UUID = '{room_uuid}' AND TIMESTAMP >= '{date}') pd
            LEFT JOIN `RL_ROOM_MAC` rrm ON rrm.MAC = pd.MAC
            WHERE rrm.ROOM_UUID = '{room_uuid}'
            GROUP BY `MINUTE`
            ORDER BY pd.`TIMESTAMP`;
        """

        # Execute the query with parameters
        cursor.execute(sql)
        position_data = cursor.fetchall()
        if (position_data):
            social_time, moving_time, upright_time, laying_time = analyse_position_data(position_data)
            print("Social time:",social_time)
            print("Moving time:",moving_time)
            print("Upright time:",upright_time)
            print("Laying time:",laying_time)
    
    cursor.close()
    connection.close()
    return sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,\
        breath_rate,heart_rate,disrupt_duration, current_sleeping_seconds, \
            current_sleep_disruption, current_disrupt_duration, \
            current_inbed_seconds,current_inroom_seconds,current_wake_time,current_bed_time, \
            current_heart_rate, current_breath_rate, social_time, moving_time, upright_time, laying_time

def get_week_start_end(date):
    # Find the start (Monday) of the week

    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    start_of_week = date - datetime.timedelta(days=date.weekday())

    # Find the end (Sunday) of the week
    end_of_week = start_of_week + datetime.timedelta(days=6)

    return start_of_week, end_of_week

def insert_data(date,room_id,type,data,mode="week"):
    if data:
        global config
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        if mode == "day":
            query = f"SELECT * FROM ANALYSIS_DAY WHERE `DATE`='{date}' AND `ROOM_ID`='{room_id}' AND `TYPE`='{type}';"
        else:
            query = f"SELECT * FROM ANALYSIS WHERE `EOW`='{date}' AND `ROOM_ID`='{room_id}' AND `TYPE`='{type}';"
        cursor.execute(query)
        existing_data = cursor.fetchone()

        if existing_data is None:

            if mode == "day" and data != '':
                value = data
                insert_query = f"INSERT INTO ANALYSIS_DAY (`DATE`,ROOM_ID,`TYPE`,`VALUE`) VALUES ('{date}', '{room_id}', '{type}', '{value}')"
            else:
                max = data.get("max")
                min = data.get("min")
                average = data.get("average")
                if (max != '' and min != '' and average != ''):
                    insert_query = f"INSERT INTO ANALYSIS (EOW,ROOM_ID,TYPE,MAX,MIN,AVERAGE) VALUES ('{date}', '{room_id}', '{type}', '{max}', '{min}', '{average}')"
                else:
                    insert_query = ''
            cursor.execute(insert_query)
            connection.commit()
            
        else:
            if mode == "day":
                value = data
                update_query = f"UPDATE ANALYSIS_DAY SET `VALUE`='{value}' WHERE `DATE`='{date}' AND `ROOM_ID`='{room_id}' AND `TYPE`='{type}';"
            else:
                max = data.get("max")
                min = data.get("min")
                average = data.get("average")
                update_query = f"UPDATE ANALYSIS SET `MAX`='{max}',`MIN`='{min}',`AVERAGE`='{average}' WHERE `EOW`='{date}' AND `ROOM_ID`='{room_id}' AND `TYPE`='{type}';"
                    
            try:
                cursor.execute(update_query)
                connection.commit()
            except Exception as e:
                print(e)
        cursor.close()
        connection.close()   

def current_layman():
    curr = str(datetime.datetime.now(timezone("Asia/Singapore"))).split(' ')[0]
    print("Running current layman")
    rooms = get_rooms()
    for room in rooms:
        print(curr,room["ID"],room["ROOM_UUID"])
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate,disrupt_duration, \
            current_sleeping_hour, current_sleep_disruption, current_disrupt_duration, \
                 current_inbed_seconds,current_inroom_seconds,current_wake_time,current_bed_time,\
                     current_heart_rate, current_breath_rate, social_time, moving_time, upright_time, laying_time = getLaymanData(curr,room["ROOM_UUID"])
        insert_data(curr,room["ID"],"sleeping_hour",sleeping_hour)
        insert_data(curr,room["ID"],"time_in_bed",time_in_bed)
        insert_data(curr,room["ID"],"bed_time",bed_time)
        insert_data(curr,room["ID"],"wake_up_time",wake_up_time)
        insert_data(curr,room["ID"],"in_room",in_room)
        insert_data(curr,room["ID"],"sleep_disruption",sleep_disruption)
        insert_data(curr,room["ID"],"breath_rate",breath_rate)
        insert_data(curr,room["ID"],"heart_rate",heart_rate)
        insert_data(curr,room["ID"],"disrupt_duration",disrupt_duration)

def previous_week():
    curr = str(datetime.datetime.now(timezone("Asia/Singapore"))).split(' ')[0]
    print("Running previous layman")
    rooms = get_rooms()
    for room in rooms:
        print(curr,room["ID"],room["ROOM_UUID"])
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate,disrupt_duration, \
            current_sleeping_hour, current_sleep_disruption, current_disrupt_duration, \
                 current_inbed_seconds,current_inroom_seconds,current_wake_time,current_bed_time,\
                     current_heart_rate, current_breath_rate, social_time, moving_time, upright_time, laying_time = getLaymanData(curr,room["ROOM_UUID"])
        insert_data(curr,room["ID"],"sleeping_hour",sleeping_hour)
        insert_data(curr,room["ID"],"time_in_bed",time_in_bed)
        insert_data(curr,room["ID"],"bed_time",bed_time)
        insert_data(curr,room["ID"],"wake_up_time",wake_up_time)
        insert_data(curr,room["ID"],"in_room",in_room)
        insert_data(curr,room["ID"],"sleep_disruption",sleep_disruption)
        insert_data(curr,room["ID"],"breath_rate",breath_rate)
        insert_data(curr,room["ID"],"heart_rate",heart_rate)
        insert_data(curr,room["ID"],"disrupt_duration",disrupt_duration)

        alert_configs = get_alert_configs()

        insert_data(curr,room["ID"],"in_room",current_inroom_seconds,mode="day")
        insert_data(curr,room["ID"],"time_in_bed",current_inbed_seconds,mode="day")
        insert_data(curr,room["ID"],"wake_up_time",current_wake_time,mode="day")
        insert_data(curr,room["ID"],"bed_time",current_bed_time,mode="day")
        insert_data(curr,room["ID"],"heart_rate",current_heart_rate,mode="day")
        insert_data(curr,room["ID"],"breath_rate",current_breath_rate,mode="day")

        insert_data(curr,room["ID"],"in_room_social_time",social_time,mode="day")
        insert_data(curr,room["ID"],"in_room_moving_time",moving_time,mode="day")
        insert_data(curr,room["ID"],"in_room_upright_time",upright_time,mode="day")
        insert_data(curr,room["ID"],"in_room_laying_time",laying_time,mode="day")

        if current_sleeping_hour:
            insert_data(curr,room["ID"],"sleeping_hour",current_sleeping_hour,mode="day")
            insert_data(curr,room["ID"],"sleep_disruption",current_sleep_disruption,mode="day")
            insert_data(curr,room["ID"],"disrupt_duration",current_disrupt_duration,mode="day")
        
        for alert_config in alert_configs:
            key = alert_config["DATA_TYPE"]
            mode = "day" if alert_config["MODE"] == 1 else "weekday"
            threshold = alert_config["THRESHOLD"]
            min_dp = alert_config["MIN_DATA_POINT"]
            max_dp = alert_config["MAX_DATA_POINT"]

            curr_key_data = get_data_by_date_and_key(curr,key,room["ID"])

            if (curr_key_data):
                if (key in ALERT.data_type and key in ALERT.message and check_anomaly(curr,room["ID"],key,curr_key_data,ALERT.data_type[key],threshold=threshold,min_dp=min_dp,max_dp=max_dp)):
                    print(curr,ALERT.message[key][mode].replace("[DATA]",str(curr_key_data)))
                    insert_alert(room["ID"],1,1,ALERT.message[key][mode].replace("[DATA]",str(curr_key_data)))
def get_alert_configs():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT `ID`, `DATA_TYPE`,`MODE`,`MIN_DATA_POINT`,`MAX_DATA_POINT`,`THRESHOLD` FROM Gaitmetrics.ALERT_CONFIGS"
    cursor.execute(sql)
    all_data = cursor.fetchall()
    if (all_data):
        return all_data
    else:
        return []

def is_anomaly(series,last_data,threshold):
    df = pd.DataFrame({'value': series})

    z_score_last_point = np.abs((last_data - df['value'].mean()) / df['value'].std())

    # if z_score_last_point > threshold:
    # print(z_score_last_point)

    return z_score_last_point > threshold

def insert_alert(room_id,urgency,type,details):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    insert_query = f"INSERT INTO ALERT (ROOM_ID,URGENCY,`TYPE`,`DETAILS`) VALUES ('{room_id}', '{urgency}', '{type}', '{details}')"
    cursor.execute(insert_query)
    connection.commit()

def check_anomaly(date,room_id,type,data,data_type,threshold=2.5,mode="day",min_dp=15,max_dp=60):
    print("Checking anomaly for",type,"with mode",mode)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    if (mode == "weekday"):
        sql = f"SELECT `VALUE` AS `AVERAGE`, `DATE` FROM `ANALYSIS_DAY` WHERE ROOM_ID={room_id} AND `TYPE`='{type}' AND `DATE` < '{date}' ORDER BY `DATE`;"
    else:
        sql = f"SELECT `VALUE` AS `AVERAGE` FROM `ANALYSIS_DAY` WHERE ROOM_ID={room_id} AND `TYPE`='{type}' AND `DATE` < '{date}' ORDER BY `DATE`;"
    cursor.execute(sql)
    all_data = cursor.fetchall()
    avgs = []
    temp_data = data
    if (data_type == "text"):
        data = text_to_seconds(data)
    elif (data_type == "time"):
        data = text_to_minutes(data)
    else:
        data = float(data)
    for d in all_data:
        average = d.get("AVERAGE")
        if (mode == "weekday"):
            c_date = d.get("DATE")
            if (not same_weekday(date,c_date)):
                continue
        if (data_type == "text"):
            average = text_to_seconds(average)
        elif (data_type == "time"):
            average = text_to_minutes(average)
        else:
            average = float(average)
        
        avgs.append(average)
    flag = False
    if (len(avgs) > min_dp):
        if len(avgs) > max_dp:
            avgs = avgs[-max_dp:]

        if is_abnormal(data,avgs,threshold):
            flag = True
        print("Abnormal" if flag else "Normal")
    else:
        print("Not enough data")
    cursor.close()
    connection.close()
    return flag

def same_weekday(date_str1, date_str2, date_format="%Y-%m-%d"):
    date1 = dt.strptime(str(date_str1), date_format)
    date2 = dt.strptime(str(date_str2), date_format)

    weekday1 = date1.weekday()
    weekday2 = date2.weekday()

    return weekday1 == weekday2

def text_to_seconds(text):

    matches = re.findall(r'(\d+\.\d+|\d+)([hms])', text)

    total_seconds = 0

    hours = 0
    minutes = 0
    seconds = 0

    # Convert each time unit to seconds
    for value, unit in matches:
        if unit == 'h':
            hours += float(value)
            total_seconds += float(value) * 3600
        elif unit == 'm':
            minutes += float(value)
            total_seconds += float(value) * 60
        elif unit == 's':
            seconds += float(value)
            total_seconds += float(value)

    return total_seconds

def is_nap(start_time, end_time):
    # Define daytime hours
    nap_start_limit = datetime.time(6, 0, 0)  # 6:00 AM
    nap_end_limit = datetime.time(20, 0, 0)   # 8:00 PM
    
    # Calculate the duration of the sleep
    duration = end_time - start_time
    
    # Check if the nap is within the specified daytime hours and duration
    if (nap_start_limit <= start_time.time() <= nap_end_limit) and (timedelta(minutes=10) <= duration <= timedelta(hours=3.5)):
        return True
    return False

def is_uninterrupted_night_sleep(end_time_prev, start_time_current, max_wake_duration=1.5, night_start='18:00', night_end='06:00'):
    
    # Calculate wake duration
    wake_duration = (start_time_current - end_time_prev).total_seconds() / 3600
    
    # Check if wake duration exceeds the threshold
    if wake_duration > max_wake_duration:
        return False
    
    # Define night period
    night_start_time = pd.to_datetime(night_start).time()
    night_end_time = pd.to_datetime(night_end).time()
    
    # Check if the sleep interval falls within the night period
    start_time_current_time = start_time_current.time()
    
    if night_start_time <= start_time_current_time or start_time_current_time < night_end_time:
        return True
    else:
        return False

def check_sleeping_intervals(data):
    threshold = 60 * 45
    sleeping_threshold = 60 * 45

    disruption_threshold = 60 * 2.5
    disruption_restore_threshold = 60 * 10

    curr_timeslot = 0

    last_disruption_time = None
    last_row = None
    sleeping = False
    cache = []

    sleep_intervals = []
    disruptions = []
    sleeping_disruptions = []
    disrupt_durations = []
    sleeping_disrupt_durations = []

    analysis = []

    date_format = "%Y-%m-%d %H:%M"
    
    for row in data:
        row["MINUTE"] = dt.strptime(row["MINUTE"], date_format)
        if (len(analysis) <= curr_timeslot):
                analysis.append([])
                disruptions.append(0)
                disrupt_durations.append(0)

        if (row["IS_LAYING"] == 1 and row["HAS_HEART_RATE"] == 1 and row["HAS_BREATH_RATE"] == 1 and row["IN_BED"] == 1 and row["IN_ROOM"] == 1):
            sleeping = True
            if (len(cache)>0):

                if (len(analysis[curr_timeslot])>1):
                    analysis[curr_timeslot][-1] = cache[-1]
                else:
                    analysis[curr_timeslot].append(cache[-1])

                diff = cache[-1]["MINUTE"] - cache[0]["MINUTE"]
                if (diff.total_seconds() > disruption_threshold):
                    last_disruption_time = cache[-1]["MINUTE"]
                cache = []
            else:
                if last_disruption_time is not None:
                    diff = row["MINUTE"] - last_disruption_time
                    if (diff.total_seconds() > disruption_restore_threshold and diff.total_seconds() < sleeping_threshold):
                        last_disruption_time = None
                        disruptions[-1] += 1
                        disrupt_durations[-1] += int(diff.total_seconds())

            analysis[curr_timeslot].append(row)
        else:
            if (sleeping):
                cache.append(row)
            if (last_row):
                diff = row["MINUTE"] - last_row["MINUTE"]

                if ((diff.total_seconds()) > threshold and sleeping):
                    sleeping = False
                    curr_timeslot += 1
                    cache = []

        if (row["IS_LAYING"] == 1 and row["HAS_HEART_RATE"] == 1 and row["HAS_BREATH_RATE"] == 1 and row["IN_BED"] == 1 and row["IN_ROOM"] == 1):
            last_row = row

    if (len(cache)>0):
        disruptions[-1] += 1
        if (len(analysis[curr_timeslot])>1):
            analysis[-1][-1] = cache[-1]
        else:
            analysis[-1].append(cache[-1])
        cache = []

    index = 0
    for interval in analysis:
        if (len(interval)>=2):

            diff = interval[-1]["MINUTE"] - interval[0]["MINUTE"]
            if (diff.total_seconds() > sleeping_threshold and len(interval) > 45):
                # print("From",interval[0]["MINUTE"],"to",interval[-1]["MINUTE"])
                if (index >0):
                    if (len(interval)>0 and len(sleep_intervals)>0 and is_uninterrupted_night_sleep(sleep_intervals[-1][-1]["MINUTE"],interval[0]["MINUTE"])):
                        sleep_intervals[-1] = sleep_intervals[-1] + interval
                        sleeping_disruptions[-1] = sleeping_disruptions[-1] + disruptions[index]
                        sleeping_disrupt_durations[-1] = sleeping_disrupt_durations[-1] + disrupt_durations[index]
                    else:
                        sleep_intervals.append(interval)
                        sleeping_disruptions.append(disruptions[index])
                        sleeping_disrupt_durations.append(disrupt_durations[index])
                else:
                    sleep_intervals.append(interval)
                    sleeping_disruptions.append(disruptions[index])
                    sleeping_disrupt_durations.append(disrupt_durations[index])
        
        index += 1

    for interval in sleep_intervals:
        print("From",interval[0]["MINUTE"],"to",interval[-1]["MINUTE"])

    for row in data:
        for interval in sleep_intervals:
            if (row["MINUTE"] >= interval[0]["MINUTE"] and row["MINUTE"] <= interval[-1]["MINUTE"] and row["IS_LAYING"] == 1 and row["HAS_HEART_RATE"] == 1 and row["HAS_BREATH_RATE"] == 1 and row["IN_BED"] == 1 and row["IN_ROOM"] == 1):
                row["IS_SLEEPING"] = 1
                break
            else:
                row["IS_SLEEPING"] = 0 
    
    return sleep_intervals, sleeping_disruptions, sleeping_disrupt_durations

def analyseData(data,current_date):

    sleeping_intervals, disruptions, disrupt_durations = check_sleeping_intervals(data)
    
    inroom_minutes = {}
    inbed_minutes = {}
    sleeping_minutes = {}

    inroom_seconds = []
    onbed_seconds = []
    sleeping_seconds = []

    start_sleep_time = []
    wake_up_time = []

    current_sleeping_seconds = None
    current_sleep_disruption = None 
    current_disrupt_duration = None
    
    current_inbed_seconds = None
    current_inroom_seconds = None
    current_wake_time = None
    current_bed_time = None

    for row in data:
        date_str = str(row["MINUTE"].date())
        if (row["IN_ROOM"]):
            if (date_str not in inroom_minutes):
                inroom_minutes[date_str] = 1
            else:
                inroom_minutes[date_str] += 1

            if (row["IN_BED"]):
                if (date_str not in inbed_minutes):
                    inbed_minutes[date_str] = 1
                else:
                    inbed_minutes[date_str] += 1
                if (row.get("IS_SLEEPING")):
                    if (date_str not in sleeping_minutes):
                        sleeping_minutes[date_str] = 1
                    else:
                        sleeping_minutes[date_str] += 1

    for date in inroom_minutes:
        print("#########",date,"#########")
        print("In room ",seconds_to_text(inroom_minutes[date]*60))
        inroom_seconds.append(inroom_minutes[date]*60)

        if date == current_date:
            current_inroom_seconds = seconds_to_text(inroom_minutes[date]*60)

        if (date in inbed_minutes):
            onbed_seconds.append(inbed_minutes[date]*60)
            print("On bed ",seconds_to_text(inbed_minutes[date]*60))

            if date == current_date:
                current_inbed_seconds = seconds_to_text(inbed_minutes[date]*60)

        if (date in sleeping_minutes):
            sleeping_seconds.append(sleeping_minutes[date]*60)
            print("Sleeping ",seconds_to_text(sleeping_minutes[date]*60))

            if (date == current_date):
                current_sleeping_seconds = seconds_to_text(sleeping_minutes[date]*60)
                current_sleep_disruption = disruptions[-1]
                current_disrupt_duration = seconds_to_text(disrupt_durations[-1])

        if (date == current_date):
            break    

    for interval in sleeping_intervals:
        if not is_nap(interval[0]["MINUTE"],interval[-1]["MINUTE"]):
            start_sleep_time.append(interval[0]["MINUTE"])

            if (str(interval[0]["MINUTE"].date()) == current_date):
                current_bed_time = to_bedtime(interval[0]["MINUTE"])

            wake_up_time.append(interval[-1]["MINUTE"])

            if (str(interval[-1]["MINUTE"].date()) == current_date):
                if not current_wake_time:
                    current_wake_time = to_waketime(interval[-1]["MINUTE"])

    try:
        sleeping_longest = int(max(sleeping_seconds))
        sleeping_shortest = int(min(sleeping_seconds))
        sleeping_average = int(sum(sleeping_seconds) / len(sleeping_seconds))

        sleeping_hour_result = {
            "average":seconds_to_text(sleeping_average),
            "max":seconds_to_text(sleeping_longest),
            "min":seconds_to_text(sleeping_shortest),
        }
        # print("sleeping",sleeping_hour_result)
    except Exception as e:
        sleeping_hour_result = None

    onbed_seconds = list(filter(filter_non_zero, onbed_seconds))

    try:
        bed_longest = int(max(onbed_seconds))
        bed_shortest = int(min(onbed_seconds))
        bed_average = int(sum(onbed_seconds) / len(onbed_seconds))

        time_in_bed_result = {
            "average":seconds_to_text(bed_average),
            "max":seconds_to_text(bed_longest),
            "min":seconds_to_text(bed_shortest),
        }
        # print("bed",time_in_bed_result)
    except Exception as e:
        time_in_bed_result = None

    inroom_seconds = list(filter(filter_non_zero, inroom_seconds))

    try:
        inroom_longest = int(max(inroom_seconds))
        inroom_shortest = int(min(inroom_seconds))
        inroom_average = int(sum(inroom_seconds) / len(inroom_seconds))

        in_room_result = {
            "average":seconds_to_text(inroom_average),
            "max":seconds_to_text(inroom_longest),
            "min":seconds_to_text(inroom_shortest),
        }
        # print("inroom",in_room_result)
    except Exception as e:
        in_room_result = None

    try:
        pattern = r'^(00:00:|00:01:|00:02:|00:03:|00:04:|00:05:)'
        if re.match(pattern, str(start_sleep_time[0]).split(" ")[1]):
            temp = []
            for i in range(1,len(start_sleep_time)):
                temp.append(start_sleep_time[i])
            
            start_sleep_time = temp
        if (len(start_sleep_time) > 0):
            average_bedtime,earliest_bedtime,latest_bedtime = bedtime_processing(start_sleep_time)
        else:
            average_waketime,earliest_waketime,latest_waketime = '-','-','-'
        bed_time_result = {
            "average":average_bedtime,
            "max":latest_bedtime,
            "min":earliest_bedtime,
        }
    except Exception as e:
        print(start_sleep_time,e)
        bed_time_result = None

    try:
        pattern = r'^(23:55:|23:56:|23:57:|23:58:|23:59:|00:00:)'
        # print(str(wake_up_time[-1]).split(" ")[1])
        if re.match(pattern, str(wake_up_time[-1]).split(" ")[1]):
            # print("removed")
            temp = []
            for i in range(0,len(wake_up_time)-1):
                temp.append(wake_up_time[i])
            
            wake_up_time = temp
            # print(wake_up_time)

        if (len(wake_up_time) > 0):
            average_waketime,earliest_waketime,latest_waketime = waketime_processing(wake_up_time)
        else:
            average_waketime,earliest_waketime,latest_waketime = '-','-','-'
        wake_up_time_result = {
            "average":average_waketime,
            "max":latest_waketime,
            "min":earliest_waketime,
        }
    except Exception as e:
        wake_up_time_result = None

    try:
        if (len(disruptions)==7):
            disruptions[-1] += disruptions[0]
            disruptions = disruptions[1:]
        # print(real_disruptions)
        disruption_most = int(max(disruptions))
        disruption_least = int(min(disruptions))
        disruption_average = sum(disruptions) / len(disruptions)

        current_sleep_disruption = disruptions[-1]

        sleep_disruption_result = {
            "average":round(disruption_average,3),
            "max":disruption_most,
            "min":disruption_least,
        }
    except Exception as e:
        if (len(sleeping_seconds)>0):
            sleep_disruption_result = {
                "average":0,
                "max":0,
                "min":0,
            }
        else:
            sleep_disruption_result = None

    try:
        if (len(disrupt_durations)==7):
            disrupt_durations[-1] += disrupt_durations[0]
            disrupt_durations = disrupt_durations[1:]

        disrupt_duration_longest = int(max(disrupt_durations))
        disrupt_duration_shortest = int(min(disrupt_durations))
        disrupt_duration_average = int(sum(disrupt_durations) / len(disrupt_durations))

        disrupt_duration_result = {
            "average":seconds_to_text(disrupt_duration_average),
            "max":seconds_to_text(disrupt_duration_longest),
            "min":seconds_to_text(disrupt_duration_shortest),
        }
    except Exception as e:
        disrupt_duration_result = None

    return in_room_result, time_in_bed_result, sleeping_hour_result, bed_time_result, \
        wake_up_time_result, sleep_disruption_result, disrupt_duration_result, \
            current_sleeping_seconds, current_sleep_disruption, current_disrupt_duration, \
            current_inbed_seconds,current_inroom_seconds,current_wake_time,current_bed_time

def analyseVitalData(data,current_date):
    current_breath_rate = None
    current_heart_rate = None
    curr_b = []
    curr_r = []
    breath_rate = []
    heart_rate = []

    date_format = "%Y-%m-%d %H:%M"
    
    for row in data:
        row["MINUTE"] = dt.strptime(row["MINUTE"], date_format)
        if (row["BREATH_RATE"] is not None and row["BREATH_RATE"] >= 8):
            breath_rate.append(row["BREATH_RATE"])
            if (str(row["MINUTE"].date()) == current_date):
                curr_b.append(row["BREATH_RATE"])

        if (row["HEART_RATE"] is not None and row["HEART_RATE"] >= 40):
            heart_rate.append(row["HEART_RATE"])
            if (str(row["MINUTE"].date()) == current_date):
                curr_r.append(row["HEART_RATE"])
    
    try:
        breath_rate = remove_outliers_iqr(breath_rate)
        breath_highest = max(breath_rate)
        breath_lowest = min(breath_rate)
        breath_average = sum(breath_rate) / len(breath_rate)

        breath_rate_result = {
            "average":round(breath_average,1),
            "max":int(breath_highest),
            "min":int(breath_lowest),
        }
    except Exception as e:
        breath_rate_result = None

    try:
        heart_rate = remove_outliers_iqr(heart_rate)
        heart_highest = max(heart_rate)
        heart_lowest = min(heart_rate)
        heart_average = sum(heart_rate) / len(heart_rate)
        heart_rate_result = {
            "average":round(heart_average,1),
            "max":int(heart_highest),
            "min":int(heart_lowest),
        }
    except Exception as e:
        heart_rate_result = None

    if curr_b:
        curr_breath_rate = remove_outliers_iqr(curr_b)
        current_breath_rate = sum(curr_b) / len(curr_b)

    if curr_r:
        curr_heart_rate = remove_outliers_iqr(curr_r)
        current_heart_rate = sum(curr_r) / len(curr_r)

    return breath_rate_result,heart_rate_result, current_breath_rate, current_heart_rate

def analyseLaymanData(data,current_date):

    now_datetime = datetime.datetime.now()

    # in seconds
    threshold = 60 * 120
    sleeping_threshold = 60 * 45
    inroom_threshold = 60 * 45
    disruption_threshold = 60 * 2.5
    disruption_restore_threshold = 60 * 10

    current_sleeping_seconds = None
    current_sleep_disruption = None
    current_disrupt_duration = None

    analysis = {"timeslot":[]}
    ianalysis = {"timeslot":[]}
    inroom_analysis = {}
    onbed_analysis = {}
    sleeping_analysis = {}

    onbed_disruption_arr = []

    curr_timeslot = 0
    icurr_timeslot = 0
    curr_day_timeslot = 0
    last_row = None
    ilast_row = None
    sleeping = False
    inroom = False
    cache = []
    inroom_cache = []
    disruptions = []
    disrupt_duration_seconds = []

    breath_rate = []
    heart_rate = []

    disruption_sec_based_on_date = {}

    current_disruption = 0
    current_disrupt_duration_secs = 0
    last_disruption_time = None

    for row in data:

        if (row["TYPE"] == 3):
            if (len(analysis["timeslot"]) <= curr_timeslot):
                disruptions.append(current_disruption)
                disrupt_duration_seconds.append(current_disrupt_duration_secs)
                current_disruption = 0
                current_disrupt_duration_secs = 0
                analysis["timeslot"].append([])
                onbed_disruption_arr.append(0)

            if (row["BREATH_RATE"] is not None and row["BREATH_RATE"] >= 8):
                breath_rate.append(row["BREATH_RATE"])

            if (row["HEART_RATE"] is not None and row["HEART_RATE"] >= 40):
                heart_rate.append(row["HEART_RATE"])


        if (len(ianalysis["timeslot"]) <= icurr_timeslot):
            ianalysis["timeslot"].append([])

        date_str = str(row["TIMESTAMP"].date())

        if (date_str not in inroom_analysis):
            curr_day_timeslot = 0
            inroom_analysis[date_str] = []

        # if (len(inroom_analysis[date_str]) <= curr_day_timeslot):
        #     inroom_analysis[date_str].append([])

        if (row["TYPE"] == 3 and row["BREATH_RATE"] is not None and row["HEART_RATE"] is not None):
            if (date_str not in onbed_analysis):
                onbed_analysis[date_str] = []
            
            if (date_str not in sleeping_analysis):
                sleeping_analysis[date_str] = []

            if (row["STATE"] == 2 and row["IN_BED"] == 1 and row["OBJECT_LOCATION"] == 1):
                sleeping = True
                if (len(cache)>0):
                    diff = cache[-1]["TIMESTAMP"] - cache[0]["TIMESTAMP"]
                    if (diff.total_seconds() > disruption_threshold):
                        # current_disruption += 1
                        last_disruption_time = cache[-1]["TIMESTAMP"]
                    analysis["timeslot"][curr_timeslot] += cache
                    cache = []
                else:
                    if last_disruption_time is not None:
                        diff = row["TIMESTAMP"] - last_disruption_time
                        if (diff.total_seconds() > disruption_restore_threshold and diff.total_seconds() < sleeping_threshold):
                            last_disruption_time = None
                            current_disruption += 1
                            current_disrupt_duration_secs += diff.total_seconds()
                            if (date_str not in disruption_sec_based_on_date):
                                disruption_sec_based_on_date[date_str] = diff.total_seconds()
                            else:
                                disruption_sec_based_on_date[date_str] += diff.total_seconds()
                        #onbed_disruption_arr[-1] =  onbed_disruption_arr[-1] + diff.total_seconds()
                analysis["timeslot"][curr_timeslot].append(row)
            else:
                if (sleeping):
                    cache.append(row)
                if (last_row):
                    diff = row["TIMESTAMP"] - last_row["TIMESTAMP"]

                    if ((diff.total_seconds()) > threshold and sleeping):
                        sleeping = False
                        curr_timeslot += 1
                        cache = []

            if (row["STATE"] == 2 and row["IN_BED"] == 1 and row["OBJECT_LOCATION"] == 1):
                last_row = row

        # if (inroom_last_row):
        #     diff = row["TIMESTAMP"] - inroom_last_row["TIMESTAMP"]

        #     if ((diff.total_seconds()) > inroom_threshold):
        #         curr_day_timeslot += 1
        #         inroom_analysis[date_str].append([])

        # if (len(inroom_analysis[date_str][curr_day_timeslot]) <= 1):
        #     inroom_analysis[date_str][curr_day_timeslot].append(row)
        # else:
        #     inroom_analysis[date_str][curr_day_timeslot][-1] = row
        # inroom_last_row = row
        if (row["OBJECT_LOCATION"] == 1):
            inroom = True
            if (len(inroom_cache)>0):
                diff = inroom_cache[-1]["TIMESTAMP"] - inroom_cache[0]["TIMESTAMP"]
                ianalysis["timeslot"][icurr_timeslot] += cache
                inroom_cache = []
            ianalysis["timeslot"][icurr_timeslot].append(row)
        else:
            if (inroom):
                inroom_cache.append(row)
            if (ilast_row):
                diff = row["TIMESTAMP"] - ilast_row["TIMESTAMP"]

                if ((diff.total_seconds()) > inroom_threshold and inroom):
                    inroom = False
                    icurr_timeslot += 1
                    inroom_cache = []
        
        if (row["OBJECT_LOCATION"] == 1):
            ilast_row = row
        

    result = []
    sleeping_hours = []
    time_in_bed = []
    start_sleep_time = []
    wake_up_time = []
    inroom_seconds = []

    disruptions.append(current_disruption)
    disruptions = disruptions[1:]

    disrupt_duration_seconds.append(current_disrupt_duration_secs)
    disrupt_duration_seconds = disrupt_duration_seconds[1:]

    real_disruptions = []
    real_disrupt_duration = []

    index = 0

    for timeslot in analysis["timeslot"]:
        if (len(timeslot)>1):
            diff = timeslot[-1]["TIMESTAMP"] - timeslot[0]["TIMESTAMP"]
            
            time_in_bed.append(diff.total_seconds())

            start_date_str = str(timeslot[0]["TIMESTAMP"].date())
            end_date_str = str(timeslot[-1]["TIMESTAMP"].date())
            if (start_date_str == end_date_str):
                onbed_analysis[start_date_str].append(diff.total_seconds())
            else:
                start_date = None
                previous_date = None
                onbed_deduct_sec = onbed_disruption_arr[index]

                # print(onbed_deduct_sec)

                for i in range(len(timeslot)):
                    if previous_date == None:
                        previous_date = timeslot[i]

                    if start_date == None:
                        start_date = timeslot[i]

                    date_str = str(timeslot[i]["TIMESTAMP"].date())

                    if (str(previous_date["TIMESTAMP"].date()) != date_str):
                        onbed_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds() - onbed_deduct_sec)
                        onbed_deduct_sec = 0
                        start_date = timeslot[i]

                    previous_date = timeslot[i]

                if (previous_date and start_date):
                    onbed_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds() - onbed_deduct_sec)
                    onbed_deduct_sec = 0


            sleep_percentage = 0
            sleep_count = 0
            for t in timeslot:
                if t["STATE"] == 2 and t["IN_BED"] == 1:
                    sleep_count+=1
            sleep_percentage = sleep_count/len(timeslot)

            if (diff.total_seconds() > sleeping_threshold and sleep_percentage >= 0.2):
                if (len(timeslot) > 1):
                    start_sleep_time.append(timeslot[0]["TIMESTAMP"])
                    if ((now_datetime - timeslot[-1]["TIMESTAMP"]).total_seconds() > (5*60)):
                        wake_up_time.append(timeslot[-1]["TIMESTAMP"])
                    # print("From:",timeslot[0]["TIMESTAMP"],", to:",timeslot[-1]["TIMESTAMP"])
                    sleeping_hours.append(diff.total_seconds())
                    real_disruptions.append(disruptions[index])
                    real_disrupt_duration.append(disrupt_duration_seconds[index])
                    
                    onbed_deduct_sec = onbed_disruption_arr[index]

                    if (start_date_str == end_date_str):
                        sleeping_analysis[start_date_str].append(diff.total_seconds())
                        print("Sleep From "+start_date_str+" to "+end_date_str)
                    else:
                        if (len(timeslot)>0):
                            start_pointer = timeslot[0]
                            current_pointer = timeslot[0]
                            previous_pointer = timeslot[0]

                            onbed_deduct_sec = onbed_disruption_arr[index]
                            for t in range(len(timeslot)):
                                current_pointer = timeslot[t]

                                start_date_str = str(start_pointer["TIMESTAMP"].date())
                                current_date_str = str(current_pointer["TIMESTAMP"].date())
                                if (start_date_str != current_date_str):
                                    # print(onbed_deduct_sec)
                                    sleeping_analysis[start_date_str].append((previous_pointer["TIMESTAMP"] - start_pointer["TIMESTAMP"]).total_seconds() - onbed_deduct_sec)
                                    onbed_deduct_sec = 0
                                    print("Sleep From "+str(start_pointer["TIMESTAMP"])+" to "+str(previous_pointer["TIMESTAMP"]))
                                    start_pointer = timeslot[t]

                                previous_pointer = timeslot[t]
                            
                            sleeping_analysis[start_date_str].append((previous_pointer["TIMESTAMP"] - start_pointer["TIMESTAMP"]).total_seconds() - onbed_deduct_sec)
                            onbed_deduct_sec = 0
                            print("Sleep From "+str(start_pointer["TIMESTAMP"])+" to "+str(previous_pointer["TIMESTAMP"]))
                
                    result.append({
                        "data_length":len(timeslot),
                        "start":timeslot[0],
                        "end":timeslot[-1]
                    })

        index += 1

    for timeslot in ianalysis["timeslot"]:
        if (len(timeslot)>1):
            diff = timeslot[-1]["TIMESTAMP"] - timeslot[0]["TIMESTAMP"]
            start_date_str = str(timeslot[0]["TIMESTAMP"].date())
            end_date_str = str(timeslot[-1]["TIMESTAMP"].date())
            # print("From ",timeslot[0]["TIMESTAMP"]," to ",timeslot[-1]["TIMESTAMP"])
            if (start_date_str == end_date_str):
                inroom_analysis[start_date_str].append(diff.total_seconds())
            else:
                start_date = None
                previous_date = None
                for i in range(len(timeslot)):
                    if previous_date == None:
                        previous_date = timeslot[i]

                    if start_date == None:
                        start_date = timeslot[i]

                    date_str = str(timeslot[i]["TIMESTAMP"].date())

                    if (str(previous_date["TIMESTAMP"].date()) != date_str):
                        inroom_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds())
                        start_date = timeslot[i]

                    previous_date = timeslot[i]

                if (previous_date and start_date):
                    inroom_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds())



    inroom_arr = []
    for date in inroom_analysis:
        inroom_second = 0
        for s in inroom_analysis[date]:
            inroom_second += s
        # print("In room:",date,seconds_to_text(inroom_second))
        inroom_seconds.append(inroom_second)

    onbed_seconds = []

    for date in onbed_analysis:
        onbed_second = 0
        for s in onbed_analysis[date]:
            onbed_second += s
        # print("On bed:",date,seconds_to_text(onbed_second))
        onbed_seconds.append(onbed_second)

    sleeping_seconds = []

    for date in sleeping_analysis:
        sleeping_second = 0
        for s in sleeping_analysis[date]:
            
            sleeping_second += s

        if date in disruption_sec_based_on_date:
            sleeping_second -= disruption_sec_based_on_date[date]

        sleeping_seconds.append(sleeping_second - (random.randint(5, 15) * 60))

        if (current_date == date):
            current_sleeping_seconds = sleeping_second - (random.randint(5, 15) * 60)
            current_sleeping_seconds = seconds_to_text(current_sleeping_seconds)

    sleeping_seconds = list(filter(filter_non_zero, sleeping_seconds))

    print(sleeping_seconds)
    
    try:
        sleeping_longest = int(max(sleeping_seconds))
        sleeping_shortest = int(min(sleeping_seconds))
        sleeping_average = int(sum(sleeping_seconds) / len(sleeping_seconds))

        sleeping_hour_result = {
            "average":seconds_to_text(sleeping_average),
            "max":seconds_to_text(sleeping_longest),
            "min":seconds_to_text(sleeping_shortest),
        }
        # print("sleeping",sleeping_hour_result)
    except Exception as e:
        sleeping_hour_result = None

    onbed_seconds = list(filter(filter_non_zero, onbed_seconds))

    try:
        bed_longest = int(max(onbed_seconds))
        bed_shortest = int(min(onbed_seconds))
        bed_average = int(sum(onbed_seconds) / len(onbed_seconds))

        time_in_bed_result = {
            "average":seconds_to_text(bed_average),
            "max":seconds_to_text(bed_longest),
            "min":seconds_to_text(bed_shortest),
        }
        # print("bed",time_in_bed_result)
    except Exception as e:
        time_in_bed_result = None

    inroom_seconds = list(filter(filter_non_zero, inroom_seconds))

    try:
        inroom_longest = int(max(inroom_seconds))
        inroom_shortest = int(min(inroom_seconds))
        inroom_average = int(sum(inroom_seconds) / len(inroom_seconds))

        in_room_result = {
            "average":seconds_to_text(inroom_average),
            "max":seconds_to_text(inroom_longest),
            "min":seconds_to_text(inroom_shortest),
        }
        # print("inroom",in_room_result)
    except Exception as e:
        in_room_result = None

    try:
        pattern = r'^(00:00:|00:01:|00:02:|00:03:|00:04:|00:05:)'
        if re.match(pattern, str(start_sleep_time[0]).split(" ")[1]):
            temp = []
            for i in range(1,len(start_sleep_time)):
                temp.append(start_sleep_time[i])
            
            start_sleep_time = temp
        if (len(start_sleep_time) > 0):
            average_bedtime,earliest_bedtime,latest_bedtime = bedtime_processing(start_sleep_time)
        else:
            average_waketime,earliest_waketime,latest_waketime = '-','-','-'
        bed_time_result = {
            "average":average_bedtime,
            "max":latest_bedtime,
            "min":earliest_bedtime,
        }
    except Exception as e:
        bed_time_result = None

    try:
        pattern = r'^(23:55:|23:56:|23:57:|23:58:|23:59:|00:00:)'
        # print(str(wake_up_time[-1]).split(" ")[1])
        if re.match(pattern, str(wake_up_time[-1]).split(" ")[1]):
            # print("removed")
            temp = []
            for i in range(0,len(wake_up_time)-1):
                temp.append(wake_up_time[i])
            
            wake_up_time = temp
            # print(wake_up_time)

        if (len(wake_up_time) > 0):
            average_waketime,earliest_waketime,latest_waketime = waketime_processing(wake_up_time)
        else:
            average_waketime,earliest_waketime,latest_waketime = '-','-','-'
        wake_up_time_result = {
            "average":average_waketime,
            "max":latest_waketime,
            "min":earliest_waketime,
        }
    except Exception as e:
        wake_up_time_result = None

    try:
        if (len(real_disruptions)==7):
            real_disruptions[-1] += real_disruptions[0]
            real_disruptions = real_disruptions[1:]
        # print(real_disruptions)
        disruption_most = int(max(real_disruptions))
        disruption_least = int(min(real_disruptions))
        disruption_average = sum(real_disruptions) / len(real_disruptions)

        current_sleep_disruption = real_disruptions[-1]

        sleep_disruption_result = {
            "average":round(disruption_average,3),
            "max":disruption_most,
            "min":disruption_least,
        }
    except Exception as e:
        if (len(sleeping_seconds)>0):
            sleep_disruption_result = {
                "average":0,
                "max":0,
                "min":0,
            }
        else:
            sleep_disruption_result = None
    
    # print("disruption",sleep_disruption_result)

    try:
        breath_rate = remove_outliers_iqr(breath_rate)
        breath_highest = max(breath_rate)
        breath_lowest = min(breath_rate)
        breath_average = sum(breath_rate) / len(breath_rate)

        breath_rate_result = {
            "average":round(breath_average,1),
            "max":int(breath_highest),
            "min":int(breath_lowest),
        }
    except Exception as e:
        breath_rate_result = None

    try:
        heart_rate = remove_outliers_iqr(heart_rate)
        heart_highest = max(heart_rate)
        heart_lowest = min(heart_rate)
        heart_average = sum(heart_rate) / len(heart_rate)
        heart_rate_result = {
            "average":round(heart_average,1),
            "max":int(heart_highest),
            "min":int(heart_lowest),
        }
    except Exception as e:
        heart_rate_result = None

    try:

        if (len(real_disrupt_duration)==7):
            real_disrupt_duration[-1] += real_disrupt_duration[0]
            real_disrupt_duration = real_disrupt_duration[1:]

        disrupt_duration_longest = int(max(real_disrupt_duration))
        disrupt_duration_shortest = int(min(real_disrupt_duration))
        disrupt_duration_average = int(sum(real_disrupt_duration) / len(real_disrupt_duration))

        current_disrupt_duration = seconds_to_text(real_disrupt_duration[-1])

        disrupt_duration_result = {
            "average":seconds_to_text(disrupt_duration_average),
            "max":seconds_to_text(disrupt_duration_longest),
            "min":seconds_to_text(disrupt_duration_shortest),
        }
    except Exception as e:
        disrupt_duration_result = None

    return sleeping_hour_result,time_in_bed_result,bed_time_result,wake_up_time_result,in_room_result,sleep_disruption_result, breath_rate_result,heart_rate_result,disrupt_duration_result, current_sleeping_seconds, current_sleep_disruption, current_disrupt_duration

def remove_outliers_iqr(data):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return [value for value in data if lower_bound <= value <= upper_bound]

def filter_non_zero(number):
    return number > 0

def seconds_to_text(seconds):
    if (seconds == 0):
        return "0m"
    # Calculate hours, minutes, and remaining seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Construct the text representation
    result = ""
    if hours > 0:
        result += f"{hours}h"
    if minutes > 0:
        result += f"{minutes}m"
    if seconds > 0 and result == '':
        result += f"{seconds}s"

    return result

def datetime_to_minutes(dt):
    return dt.hour * 60 + dt.minute

def minutes_to_am_pm_time(minutes):
    if (minutes > 24*60):
        minutes -= 24*60
    hours, minutes = divmod(minutes, 60)
    period = "AM" if hours < 12 else "PM"
    if hours == 0:
        hours = 12  # Adjust 0 to 12 AM
    elif hours > 12:
        hours -= 12  # Convert to 12-hour format
    return f"{hours:02}:{minutes:02} {period}"

def text_to_minutes(text):
    minutes = 0

    try:
        time = text.split(" ")
        time1 = time[0]
        am_pm = time[1]
        if am_pm == "PM":
            minutes += 12*60

        time1 = time1.split(":")
        hour = time1[0]
        minute = time1[1]

        minutes = minutes + (int(hour) * 60) + int(minute)

    except:
        print("Error to convert time")

    return minutes

def to_waketime(time):
    min = datetime_to_minutes(time)
    return minutes_to_am_pm_time(min)

def to_bedtime(time):
    min = datetime_to_minutes(time)
    return minutes_to_am_pm_time(min)

def bedtime_processing(arr):
    # Function to convert datetime to minutes since midnight
    def datetime_to_minutes(dt):
        return dt.hour * 60 + dt.minute
    
    # Function to convert minutes since midnight to 12-hour AM/PM time format
    def minutes_to_am_pm_time(minutes):
        if (minutes > 24*60):
            minutes -= 24*60
        hours, minutes = divmod(minutes, 60)
        period = "AM" if hours < 12 else "PM"
        if hours == 0:
            hours = 12  # Adjust 0 to 12 AM
        elif hours > 12:
            hours -= 12  # Convert to 12-hour format
        return f"{hours:02}:{minutes:02} {period}"

    # Convert bedtime_array to minutes since midnight
    bedtime_minutes = [datetime_to_minutes(dt) for dt in arr]

    bedtime_minutes = sorted(bedtime_minutes)

    # Value to compare against
    threshold = 60 * 6

    # Initialize an array to store popped elements
    popped_elements = []

    # Iterate through the array and remove elements less than the threshold
    i = 0
    while i < len(bedtime_minutes):
        if bedtime_minutes[i] < threshold:
            popped_elements.append(bedtime_minutes.pop(i))
        else:
            i += 1

    bedtime_minutes += popped_elements

    earliest_bedtime = minutes_to_am_pm_time(bedtime_minutes[0])
    latest_bedtime = minutes_to_am_pm_time(bedtime_minutes[-1])

    for i in range(len(bedtime_minutes)):
        if (bedtime_minutes[i] < threshold):
            bedtime_minutes[i] += 24 * 60

    average_bedtime = int(sum(bedtime_minutes) / len(bedtime_minutes))
    average_bedtime = minutes_to_am_pm_time(average_bedtime)

    return average_bedtime,earliest_bedtime,latest_bedtime

def waketime_processing(arr):
    # Function to convert datetime to minutes since midnight
    def datetime_to_minutes(dt):
        return dt.hour * 60 + dt.minute
    
    # Function to convert minutes since midnight to 12-hour AM/PM time format
    def minutes_to_am_pm_time(minutes):
        if (minutes > 24*60):
            minutes -= 24*60
        hours, minutes = divmod(minutes, 60)
        period = "AM" if hours < 12 else "PM"
        if hours == 0:
            hours = 12  # Adjust 0 to 12 AM
        elif hours > 12:
            hours -= 12  # Convert to 12-hour format
        return f"{hours:02}:{minutes:02} {period}"

    # Convert waketime_array to minutes since midnight
    waketime_minutes = [datetime_to_minutes(dt) for dt in arr]

    waketime_minutes = sorted(waketime_minutes)

    # Value to compare against
    threshold = 60 * 12

    # Initialize an array to store popped elements
    popped_elements = []

    # Iterate through the array and remove elements less than the threshold
    i = 0
    while i < len(waketime_minutes):
        if waketime_minutes[i] < threshold:
            popped_elements.append(waketime_minutes.pop(i))
        else:
            i += 1

    waketime_minutes += popped_elements

    earliest_waketime = minutes_to_am_pm_time(waketime_minutes[0])
    latest_waketime = minutes_to_am_pm_time(waketime_minutes[-1])

    for i in range(len(waketime_minutes)):
        if (waketime_minutes[i] < 13*60):
            waketime_minutes[i] += 24 * 60
        # waketime_minutes[i] = minutes_to_am_pm_time(waketime_minutes[i])

    average_waketime = int(sum(waketime_minutes) / len(waketime_minutes))
    average_waketime = minutes_to_am_pm_time(average_waketime)

    return average_waketime,earliest_waketime,latest_waketime

def remove_connection():
    global config
    vernemq_connection = mysql.connector.connect(**vernemq)
    vernemq_cursor = vernemq_connection.cursor(dictionary=True)
    sql = "UPDATE vmq_auth_acl SET connected=0,last_connect_time=NOW() WHERE connected=1 AND TIMESTAMPDIFF(MINUTE, last_connect_time, NOW()) > 5;"
    vernemq_cursor.execute(sql)
    vernemq_connection.commit()
    vernemq_cursor.close()
    vernemq_connection.close()  

domain_url = "https://aswelfarehome.gaitmetrics.org/api"

def get_user_token():
    username= "sam"
    password = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

    data = {
        'LOGIN_NAME': username,
        'PWD': password
    }

    response = requests.post(domain_url+"/login",json=data)

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
        response = requests.post(domain_url + "/getAnalyticData", json=data, headers=headers)
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
        sentMail(",".join(recipients),"Aswelfarehome Devices Disconnected!",body)

sender_email = "www.gaitmetric.com.sg@gmail.com"
sender_password = "wolryshamgswgvzu"
# recipient_email = "recipient@gmail.com"
def sentMail(recipient, subject, body):
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = recipient
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient, html_message.as_string())
    server.quit()

if __name__ == "__main__":
    #previous
    schedule.every().monday.at("23:59", timezone("Asia/Singapore")).do(previous_week)
    schedule.every().tuesday.at("23:59", timezone("Asia/Singapore")).do(previous_week)
    schedule.every().wednesday.at("23:59", timezone("Asia/Singapore")).do(previous_week)
    schedule.every().thursday.at("23:59", timezone("Asia/Singapore")).do(previous_week)
    schedule.every().friday.at("23:59", timezone("Asia/Singapore")).do(previous_week)
    schedule.every().saturday.at("23:59", timezone("Asia/Singapore")).do(previous_week)
    schedule.every().sunday.at("23:59", timezone("Asia/Singapore")).do(previous_week)

    # #current week
    # for i in ["04:00","08:00","10:00","12:00","14:00","16:00","18:00","20:00","22:00"]:
        
    #     schedule.every().monday.at(i, timezone("Asia/Singapore")).do(current_layman)
    #     schedule.every().tuesday.at(i, timezone("Asia/Singapore")).do(current_layman)
    #     schedule.every().wednesday.at(i, timezone("Asia/Singapore")).do(current_layman)
    #     schedule.every().thursday.at(i, timezone("Asia/Singapore")).do(current_layman)
    #     schedule.every().friday.at(i, timezone("Asia/Singapore")).do(current_layman)
    #     schedule.every().saturday.at(i, timezone("Asia/Singapore")).do(current_layman)
    #     schedule.every().sunday.at(i, timezone("Asia/Singapore")).do(current_layman)
        
    schedule.every(5).minutes.do(remove_connection)
    schedule.every().hour.at(":15").do(get_summary_data)
    schedule.every().hour.at(":45").do(check_disconnected_devices)

    while True:
        print(datetime.datetime.now(timezone("Asia/Singapore")))
        schedule.run_pending()
        time.sleep(30)
