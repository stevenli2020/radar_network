from datetime import datetime as dt,timedelta
import schedule
import datetime
import random
import mysql.connector
from pytz import timezone
import re
import pandas as pd
import numpy as np

from run import getLaymanData, get_alert_configs, get_rooms, insert_data, seconds_to_text, check_anomaly, insert_alert, get_data_by_date_and_key, ALERT


def get_dates_between(start_date_str, end_date_str):
    start_date = dt.strptime(start_date_str, "%Y-%m-%d")
    end_date = dt.strptime(end_date_str, "%Y-%m-%d")
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return dates

start_date = "2024-09-30"
end_date = "2024-10-05"

dates_between = get_dates_between(start_date, end_date)

for curr in dates_between:
    # print("Running current layman")
    rooms = get_rooms()
    for room in rooms:
        if (room["ID"] not in [5]):
            continue
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
        
        # for alert_config in alert_configs:
        #     key = alert_config["DATA_TYPE"]
        #     mode = "day" if alert_config["MODE"] == 1 else "weekday"
        #     threshold = alert_config["THRESHOLD"]
        #     min_dp = alert_config["MIN_DATA_POINT"]
        #     max_dp = alert_config["MAX_DATA_POINT"]

        #     curr_key_data = get_data_by_date_and_key(curr,key,room["ID"])

        #     if (curr_key_data):
        #         if (key in ALERT.data_type and key in ALERT.message and check_anomaly(curr,room["ID"],key,curr_key_data,ALERT.data_type[key],threshold=threshold,min_dp=min_dp,max_dp=max_dp)):
        #             print(curr,ALERT.message[key][mode].replace("[DATA]",str(curr_key_data)))
        #             insert_alert(room["ID"],1,1,ALERT.message[key][mode].replace("[DATA]",str(curr_key_data)))