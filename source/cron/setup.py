from datetime import datetime as dt,timedelta
import schedule
import datetime
import random
import mysql.connector
from pytz import timezone
import re
import pandas as pd
import numpy as np

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

def get_interval_tables(cursor,date):
    end_date = dt.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=7)

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

def getLaymanData(date,room_uuid):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sleeping_hour = None
    bed_time = None
    wake_up_time = None
    time_in_bed = None
    in_room = None
    sleep_disruption = None
    breath_rate = None
    heart_rate = None

    disrupt_duration = None

    current_sleeping_seconds = None
    current_sleep_disruption = None
    current_disrupt_duration = None

    tables, start_date = get_interval_tables(cursor,date)
    if (len(tables)>0):
        combine_table = []
        for table in tables:
            combine_table.append(f"SELECT tb.* FROM {table} tb LEFT JOIN `RL_ROOM_MAC` irrm ON irrm.MAC = tb.MAC WHERE irrm.ROOM_UUID = '{room_uuid}' AND TIMESTAMP >= '{start_date}'")
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
            in_room, time_in_bed, sleeping_hour, bed_time, wake_up_time, sleep_disruption,disrupt_duration,current_sleeping_seconds, current_sleep_disruption, current_disrupt_duration = analyseData(processed_data,date)

        sql = f"""
            SELECT pd.`HEART_RATE`,pd.`BREATH_RATE`
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
            breath_rate,heart_rate = analyseVitalData(vital_data)
        
        cursor.close()
        connection.close()
    return sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate,disrupt_duration, current_sleeping_seconds, current_sleep_disruption, current_disrupt_duration

def get_week_start_end(date):
    # Find the start (Monday) of the week

    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    start_of_week = date - datetime.timedelta(days=date.weekday())

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
    # print("Running current layman")
    rooms = get_rooms()
    for room in rooms:
        # print(curr,room["ID"],room["ROOM_UUID"])
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate,disrupt_duration, current_sleeping_hour, current_sleep_disruption, current_disrupt_duration = getLaymanData(curr,room["ROOM_UUID"])
        insert_data(curr,room["ID"],"sleeping_hour",sleeping_hour)
        insert_data(curr,room["ID"],"time_in_bed",time_in_bed)
        insert_data(curr,room["ID"],"bed_time",bed_time)
        insert_data(curr,room["ID"],"wake_up_time",wake_up_time)
        insert_data(curr,room["ID"],"in_room",in_room)
        insert_data(curr,room["ID"],"sleep_disruption",sleep_disruption)
        insert_data(curr,room["ID"],"breath_rate",breath_rate)
        insert_data(curr,room["ID"],"heart_rate",heart_rate)

def previous_week():
    curr = str(datetime.datetime.now(timezone("Asia/Singapore"))).split(' ')[0]
    print("Running previous layman")
    rooms = get_rooms()
    for room in rooms:
        # print(curr,room["ID"],room["ROOM_UUID"])
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate,disrupt_duration, current_sleeping_hour, current_sleep_disruption, current_disrupt_duration = getLaymanData(curr,room["ROOM_UUID"])
        insert_data(curr,room["ID"],"sleeping_hour",sleeping_hour)
        insert_data(curr,room["ID"],"time_in_bed",time_in_bed)
        insert_data(curr,room["ID"],"bed_time",bed_time)
        insert_data(curr,room["ID"],"wake_up_time",wake_up_time)
        insert_data(curr,room["ID"],"in_room",in_room)
        insert_data(curr,room["ID"],"sleep_disruption",sleep_disruption)
        insert_data(curr,room["ID"],"breath_rate",breath_rate)
        insert_data(curr,room["ID"],"heart_rate",heart_rate)

def check_sleeping_intervals(data):
    threshold = 60 * 90
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
                print("From",interval[0]["MINUTE"],"to",interval[-1]["MINUTE"])
                sleep_intervals.append(interval)
                sleeping_disruptions.append(disruptions[index])
                sleeping_disrupt_durations.append(disrupt_durations[index])
        
        index += 1

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
        if (date in inbed_minutes):
            onbed_seconds.append(inbed_minutes[date]*60)
            print("On bed ",seconds_to_text(inbed_minutes[date]*60))
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
        start_sleep_time.append(interval[0]["MINUTE"])
        wake_up_time.append(interval[-1]["MINUTE"])

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

        print(disruptions)

        sleep_disruption_result = {
            "average":round(disruption_average,3),
            "max":disruption_most,
            "min":disruption_least,
        }

        print(sleep_disruption_result)
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

        print(disrupt_durations,min(disrupt_durations))
        print(disrupt_duration_result)

    except Exception as e:
        disrupt_duration_result = None

    return in_room_result, time_in_bed_result, sleeping_hour_result, bed_time_result, wake_up_time_result, sleep_disruption_result, disrupt_duration_result, current_sleeping_seconds, current_sleep_disruption, current_disrupt_duration

def analyseVitalData(data):
    breath_rate = []
    heart_rate = []
    for row in data:
        if (row["BREATH_RATE"] is not None and row["BREATH_RATE"] >= 8):
            breath_rate.append(row["BREATH_RATE"])

        if (row["HEART_RATE"] is not None and row["HEART_RATE"] >= 40):
            heart_rate.append(row["HEART_RATE"])
    
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

    return breath_rate_result,heart_rate_result

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
                    print("From:",timeslot[0]["TIMESTAMP"],", to:",timeslot[-1]["TIMESTAMP"])
                    sleeping_hours.append(diff.total_seconds())
                    real_disruptions.append(disruptions[index])
                    real_disrupt_duration.append(disrupt_duration_seconds[index])
                    
                    onbed_deduct_sec = onbed_disruption_arr[index]

                    if (start_date_str == end_date_str):
                        sleeping_analysis[start_date_str].append(diff.total_seconds())
                        # print("Sleep From "+start_date_str+" to "+end_date_str)
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
                            # print("Sleep From "+str(start_pointer["TIMESTAMP"])+" to "+str(previous_pointer["TIMESTAMP"]))
                
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

start_date = "2024-05-22"
end_date = "2024-05-25"

def get_dates_between(start_date_str, end_date_str):
    start_date = dt.strptime(start_date_str, "%Y-%m-%d")
    end_date = dt.strptime(end_date_str, "%Y-%m-%d")
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return dates



def get_analysis_data(date,room_id):
    global config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = f"SELECT `VALUE`, `TYPE` FROM ANALYSIS_DAY WHERE ROOM_ID={room_id} AND DATE='{date}';"
    cursor.execute(sql)
    sleeping_hour = None
    sleep_disruption = None
    disrupt_duration = None
    data = cursor.fetchall()
    if data:
        for row in data:
            if (row["TYPE"] == "sleeping_hour"):
                sleeping_hour = row["VALUE"]
            if (row["TYPE"] == "sleep_disruption"):
                sleep_disruption = row["VALUE"]
            if (row["TYPE"] == "disrupt_duration"):
                disrupt_duration = row["VALUE"]
    cursor.close()
    connection.close()  

    return sleeping_hour, sleep_disruption, disrupt_duration

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

def check_anomaly(date,room_id,type,data,data_type,threshold=2.5,mode="week"):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    if (mode == "weekday"):
        sql = f"SELECT `VALUE` AS `AVERAGE`, `DATE` FROM `ANALYSIS_DAY` WHERE ROOM_ID={room_id} AND `TYPE`='{type}' AND `DATE` < '{date}' ORDER BY `DATE`;"
    else:
        sql = f"SELECT `AVERAGE` FROM `ANALYSIS` WHERE ROOM_ID={room_id} AND `TYPE`='{type}' AND EOW < '{date}' ORDER BY EOW;"
    cursor.execute(sql)
    all_data = cursor.fetchall()
    avgs = []
    temp_data = data
    if (data_type == "text"):
        data = text_to_seconds(data)
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
        else:
            average = float(average)
        
        avgs.append(average)
    flag = False
    if (mode == "weekday"):
        min_count = 5
    else:
        min_count = 15
    if (len(avgs) > min_count):

        if len(avgs) > 30:
            avgs = avgs[-30:]

        if is_anomaly(avgs,data,threshold):
            flag = True
        #     print("########################################",date,data,avgs, message)
        # elif (mode == "weekday"):
        #     print("########################################",date,data,avgs)

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

dates_between = get_dates_between(start_date, end_date)

for curr in dates_between:
    # print("Running current layman")
    rooms = get_rooms()
    for room in rooms:
        # if (room["ID"] != ):
        #     continue
        print(curr,room["ID"],room["ROOM_UUID"])
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate,disrupt_duration, current_sleeping_hour, current_sleep_disruption, current_disrupt_duration = getLaymanData(curr,room["ROOM_UUID"])
        insert_data(curr,room["ID"],"sleeping_hour",sleeping_hour)
        insert_data(curr,room["ID"],"time_in_bed",time_in_bed)
        insert_data(curr,room["ID"],"bed_time",bed_time)
        insert_data(curr,room["ID"],"wake_up_time",wake_up_time)
        insert_data(curr,room["ID"],"in_room",in_room)
        insert_data(curr,room["ID"],"sleep_disruption",sleep_disruption)
        insert_data(curr,room["ID"],"breath_rate",breath_rate)
        insert_data(curr,room["ID"],"heart_rate",heart_rate)
        insert_data(curr,room["ID"],"disrupt_duration",disrupt_duration)

        if (current_sleeping_hour):
            insert_data(curr,room["ID"],"sleeping_hour",current_sleeping_hour,mode="day")
        
        if (current_sleep_disruption):
            insert_data(curr,room["ID"],"sleep_disruption",current_sleep_disruption,mode="day")

        if (current_disrupt_duration):
            insert_data(curr,room["ID"],"disrupt_duration",current_disrupt_duration,mode="day")