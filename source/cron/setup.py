from datetime import datetime as dt,timedelta
import schedule
import datetime
import time
import mysql.connector
from pytz import timezone

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

    sql = "SELECT pd.`TIMESTAMP`, pd.`STATE`, pd.`IN_BED`, pd.`BREATH_RATE`, pd.`HEART_RATE` FROM `RL_ROOM_MAC` rrm LEFT JOIN `PROCESSED_DATA` pd ON rrm.MAC = pd.MAC WHERE pd.`TIMESTAMP` BETWEEN DATE_SUB('%s', INTERVAL 6 DAY) AND DATE_ADD('%s', INTERVAL 1 DAY) AND rrm.ROOM_UUID = '%s' ORDER BY pd.`TIMESTAMP`;"%(date,date,room_uuid)
    cursor.execute(sql)
    processed_data = cursor.fetchall()
    if (processed_data):
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate = analyseLaymanData(processed_data)
        
    cursor.close()
    connection.close()
    return sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate

def get_week_start_end(date):
    # Find the start (Monday) of the week

    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    start_of_week = date - datetime.timedelta(days=date.weekday())

    # Find the end (Sunday) of the week
    end_of_week = start_of_week + datetime.timedelta(days=6)

    return start_of_week, end_of_week

def insert_data(date,room_id,type,data):
    if data:
        global config
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        query = f"SELECT * FROM ANALYSIS WHERE `EOW`='{date}' AND `ROOM_ID`='{room_id}' AND `TYPE`='{type}';"
        cursor.execute(query)
        existing_data = cursor.fetchone()

        if existing_data is None:

            max = data.get("max")
            min = data.get("min")
            average = data.get("average")
            # Data doesn't exist, so insert it
            insert_query = f"INSERT INTO ANALYSIS (EOW,ROOM_ID,TYPE,MAX,MIN,AVERAGE) VALUES ('{date}', '{room_id}', '{type}', '{max}', '{min}', '{average}')"
            cursor.execute(insert_query)
            connection.commit()
            
        else:
            max = data.get("max")
            min = data.get("min")
            average = data.get("average")
            try:
                update_query = f"UPDATE ANALYSIS SET `MAX`='{max}',`MIN`='{min}',`AVERAGE`='{average}' WHERE `EOW`='{date}' AND `ROOM_ID`='{room_id}' AND `TYPE`='{type}';"
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
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate = getLaymanData(eow,room["ROOM_UUID"])
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
        print(curr,room["ID"],room["ROOM_UUID"])
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate = getLaymanData(curr,room["ROOM_UUID"])
        insert_data(curr,room["ID"],"sleeping_hour",sleeping_hour)
        insert_data(curr,room["ID"],"time_in_bed",time_in_bed)
        insert_data(curr,room["ID"],"bed_time",bed_time)
        insert_data(curr,room["ID"],"wake_up_time",wake_up_time)
        insert_data(curr,room["ID"],"in_room",in_room)
        insert_data(curr,room["ID"],"sleep_disruption",sleep_disruption)
        insert_data(curr,room["ID"],"breath_rate",breath_rate)
        insert_data(curr,room["ID"],"heart_rate",heart_rate)

def analyseLaymanData(data):
    # in seconds
    threshold = 60 * 20
    sleeping_threshold = 60 * 30
    inroom_threshold = 60
    disruption_threshold = 60 * 3
    disruption_restore_threshold = 60 * 10

    analysis = {"timeslot":[]}
    inroom_analysis = {}
    onbed_analysis = {}
    sleeping_analysis = {}

    curr_timeslot = 0
    curr_day_timeslot = 0
    last_row = None
    inroom_last_row = None
    sleeping = False
    cache = []
    inroom_cache = []
    disruptions = []

    breath_rate = []
    heart_rate = []

    current_disruption = 0
    last_disruption_time = None

    for row in data:

        if (len(analysis["timeslot"]) <= curr_timeslot):
            disruptions.append(current_disruption)
            current_disruption = 0
            analysis["timeslot"].append([])

        if (row["BREATH_RATE"] is not None):
            breath_rate.append(row["BREATH_RATE"])

        if (row["HEART_RATE"] is not None):
            heart_rate.append(row["HEART_RATE"])

        date_str = str(row["TIMESTAMP"].date())

        if (date_str not in inroom_analysis):
            curr_day_timeslot = 0
            inroom_analysis[date_str] = []

        if (len(inroom_analysis[date_str]) <= curr_day_timeslot):
            inroom_analysis[date_str].append([])

        if (date_str not in onbed_analysis):
            onbed_analysis[date_str] = []
        
        if (date_str not in sleeping_analysis):
            sleeping_analysis[date_str] = []

        if (row["STATE"] == 2 and row["IN_BED"] == 1):
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
                    if (diff.total_seconds() > disruption_restore_threshold):
                        last_disruption_time = None
                        current_disruption += 1
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

        if (row["STATE"] == 2 and row["IN_BED"] == 1):
            last_row = row

        if (inroom_last_row):
            diff = row["TIMESTAMP"] - inroom_last_row["TIMESTAMP"]

            if ((diff.total_seconds()) > inroom_threshold):
                curr_day_timeslot += 1
                inroom_analysis[date_str].append([])

        if (len(inroom_analysis[date_str][curr_day_timeslot]) <= 1):
            inroom_analysis[date_str][curr_day_timeslot].append(row)
        else:
            inroom_analysis[date_str][curr_day_timeslot][-1] = row
        inroom_last_row = row
        

    result = []
    sleeping_hours = []
    time_in_bed = []
    start_sleep_time = []
    wake_up_time = []
    inroom_seconds = []

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
                for i in range(len(timeslot)):
                    if previous_date == None:
                        previous_date = timeslot[i]

                    if start_date == None:
                        start_date = timeslot[i]

                    date_str = str(timeslot[i]["TIMESTAMP"].date())

                    if (str(previous_date["TIMESTAMP"].date()) != date_str):
                        onbed_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds())
                        start_date = timeslot[i]

                    previous_date = timeslot[i]

                if (previous_date and start_date):
                    onbed_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds())


            sleep_percentage = 0
            sleep_count = 0
            for t in timeslot:
                if t["STATE"] == 2 and t["IN_BED"] == 1:
                    sleep_count+=1
            sleep_percentage = sleep_count/len(timeslot)

            if (diff.total_seconds() > sleeping_threshold and sleep_percentage >= 0.3):
                if (len(timeslot) > 1):
                    start_sleep_time.append(timeslot[0]["TIMESTAMP"])
                    wake_up_time.append(timeslot[-1]["TIMESTAMP"])
                    sleeping_hours.append(diff.total_seconds())

                    if (start_date_str == end_date_str):
                        sleeping_analysis[start_date_str].append(diff.total_seconds())
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
                                sleeping_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds())
                                start_date = timeslot[i]

                            previous_date = timeslot[i]

                        if (previous_date and start_date):
                            sleeping_analysis[str(previous_date["TIMESTAMP"].date())].append((previous_date["TIMESTAMP"] - start_date["TIMESTAMP"]).total_seconds())
                    
                    result.append({
                        "data_length":len(timeslot),
                        "start":timeslot[0],
                        "end":timeslot[-1]
                    })

    inroom_arr = []

    for date in inroom_analysis:
        inroom_second = 0
        for ts in inroom_analysis[date]:
            if (len(ts) > 1):
                inroom_arr.append({
                    "from":ts[0]["TIMESTAMP"],
                    "to":ts[-1]["TIMESTAMP"]
                })
                diff = ts[-1]["TIMESTAMP"] - ts[0]["TIMESTAMP"]
                inroom_second += diff.total_seconds()

        inroom_seconds.append(inroom_second)

    onbed_seconds = []

    for date in onbed_analysis:
        onbed_second = 0
        for s in onbed_analysis[date]:
            onbed_second += s

        onbed_seconds.append(onbed_second)

    sleeping_seconds = []

    for date in sleeping_analysis:
        sleeping_second = 0
        for s in sleeping_analysis[date]:
            sleeping_second += s

        sleeping_seconds.append(sleeping_second)

    sleeping_seconds = list(filter(filter_non_zero, sleeping_seconds))
    
    try:
        sleeping_longest = int(max(sleeping_seconds))
        sleeping_shortest = int(min(sleeping_seconds))
        sleeping_average = int(sum(sleeping_seconds) / len(sleeping_seconds))

        sleeping_hour_result = {
            "average":seconds_to_text(sleeping_average),
            "max":seconds_to_text(sleeping_longest),
            "min":seconds_to_text(sleeping_shortest),
        }
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
    except Exception as e:
        in_room_result = None

    try:
        average_bedtime,earliest_bedtime,latest_bedtime = bedtime_processing(start_sleep_time)
        bed_time_result = {
            "average":average_bedtime,
            "max":latest_bedtime,
            "min":earliest_bedtime,
        }
    except Exception as e:
        bed_time_result = None

    try:
        average_waketime,earliest_waketime,latest_waketime = waketime_processing(wake_up_time)
        wake_up_time_result = {
            "average":average_waketime,
            "max":latest_waketime,
            "min":earliest_waketime,
        }
    except Exception as e:
        wake_up_time_result = None

    disruptions.append(current_disruption)
    disruptions = disruptions[1:]

    try:
        disruption_most = int(max(disruptions))
        disruption_least = int(min(disruptions))
        disruption_average = sum(disruptions) / len(disruptions)
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
        breath_highest = max(breath_rate)
        breath_lowest = min(breath_rate)
        breath_average = sum(breath_rate) / len(breath_rate)

        breath_rate_result = {
            "average":round(breath_average,3),
            "max":breath_highest,
            "min":breath_lowest,
        }
    except Exception as e:
        breath_rate_result = None

    try:
        heart_highest = max(heart_rate)
        heart_lowest = min(heart_rate)
        heart_average = sum(heart_rate) / len(heart_rate)
        heart_rate_result = {
            "average":round(heart_average,3),
            "max":heart_highest,
            "min":heart_lowest,
        }
    except Exception as e:
        heart_rate_result = None

    return sleeping_hour_result,time_in_bed_result,bed_time_result,wake_up_time_result,in_room_result,sleep_disruption_result,breath_rate_result,heart_rate_result

def filter_non_zero(number):
    return number != 0

def seconds_to_text(seconds):
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
        if (waketime_minutes[i] > 20*60):
            waketime_minutes[i] -= 24 * 60
        # waketime_minutes[i] = minutes_to_am_pm_time(waketime_minutes[i])

    average_waketime = int(sum(waketime_minutes) / len(waketime_minutes))
    average_waketime = minutes_to_am_pm_time(average_waketime)

    return average_waketime,earliest_waketime,latest_waketime

start_date = "2023-06-05"
end_date = "2023-09-02"

def get_dates_between(start_date_str, end_date_str):
    start_date = dt.strptime(start_date_str, "%Y-%m-%d")
    end_date = dt.strptime(end_date_str, "%Y-%m-%d")
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return dates

dates_between = get_dates_between(start_date, end_date)

for curr in dates_between:
    print("Running current layman")
    rooms = get_rooms()
    for room in rooms:
        print(curr,room["ID"],room["ROOM_UUID"])
        sleeping_hour,time_in_bed,bed_time,wake_up_time,in_room,sleep_disruption,breath_rate,heart_rate = getLaymanData(curr,room["ROOM_UUID"])
        insert_data(curr,room["ID"],"sleeping_hour",sleeping_hour)
        insert_data(curr,room["ID"],"time_in_bed",time_in_bed)
        insert_data(curr,room["ID"],"bed_time",bed_time)
        insert_data(curr,room["ID"],"wake_up_time",wake_up_time)
        insert_data(curr,room["ID"],"in_room",in_room)
        insert_data(curr,room["ID"],"sleep_disruption",sleep_disruption)
        insert_data(curr,room["ID"],"breath_rate",breath_rate)
        insert_data(curr,room["ID"],"heart_rate",heart_rate)