from datetime import datetime
import mysql.connector
from user.config import config, vernemq

config = config()

def getLaymanData(room_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    result = {
        "data":{
            "room_id":room_id,
            "room_name":None,
            "sleeping_hour":{
                "average":"-",
                "longest":"-",
                "shortest":"-",
                "previous_average":"-"
            },
            "bed_time":{
                "average":"-",
                "latest":"-",
                "earliest":"-",
                "previous_average":"-"
            },
            "wake_up_time":{
                "average":"-",
                "latest":"-",
                "earliest":"-",
                "previous_average":"-"
            },
            "time_in_bed":{
                "average":"-",
                "longest":"-",
                "shortest":"-",
                "previous_average":"-"
            },
            "in_room":{
                "average":"-",
                "longest":"-",
                "shortest":"-",
                "previous_average":"-"
            },
            "sleep_disruption":{
                "average":"-",
                "most":"-",
                "least":"-",
                "previous_average":"-"
            },
            "breath_rate":{
                "average":"-",
                "highest":"-",
                "lowest":"-",
                "previous_average":"-"
            },
            "heart_rate":{
                "average":"-",
                "highest":"-",
                "lowest":"-",
                "previous_average":"-"
            }
        }
    }
    sql = "SELECT CONCAT(ROOM_NAME,'@',ROOM_LOC) AS room_name FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s';"%(room_id)
    cursor.execute(sql)
    room_name = cursor.fetchone()
    if (room_name):
        result["data"]["room_name"] = room_name["room_name"]

    sql = "SELECT pd.`TIMESTAMP`,pd.`STATE`,pd.`IN_BED`,pd.`BREATH_RATE`,pd.`HEART_RATE` FROM `RL_ROOM_MAC` rrm LEFT JOIN `PROCESSED_DATA` pd ON rrm.MAC=pd.MAC WHERE WEEK(pd.`TIMESTAMP`, 1) = WEEK('2023-08-18', 1) AND YEAR(pd.`TIMESTAMP`) = YEAR('2023-08-18') AND rrm.ROOM_UUID='%s' ORDER BY TIMESTAMP;"%(room_id)
    cursor.execute(sql)
    processed_data = cursor.fetchall()
    if (processed_data):
        analysis = analyseLaymanData(processed_data)
        result["data"]["sleeping_hour"] = analysis["sleeping_hour"]
        result["data"]["time_in_bed"] = analysis["time_in_bed"]
        result["data"]["wake_up_time"] = analysis["wake_up_time"]
        result["data"]["bed_time"] = analysis["bed_time"]
        result["data"]["in_room"] = analysis["in_room"]
        result["data"]["sleep_disruption"] = analysis["sleep_disruption"]
        result["data"]["breath_rate"] = analysis["breath_rate"]
        result["data"]["heart_rate"] = analysis["heart_rate"]

    #     print(data)
    #     result["DATA"].append({"id":data["Id"]})
    # result["DATA"] =  #[{"MAC": MAC} for (MAC) in cursor]
    
    cursor.close()
    connection.close()
    return result

def analyseLaymanData(data):
    # in seconds
    threshold = 60 * 20
    sleeping_threshold = 60 * 30
    inroom_threshold = 60
    disruption_threshold = 60 * 5

    analysis = {"timeslot":[]}
    inroom_analysis = {}

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

        if (row["STATE"] == 2 and row["IN_BED"] == 1):
            sleeping = True
            if (len(cache)>0):
                diff = cache[-1]["TIMESTAMP"] - cache[0]["TIMESTAMP"]
                if (diff.total_seconds() > disruption_threshold):
                    current_disruption += 1
                analysis["timeslot"][curr_timeslot] += cache
                cache = []
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

            sleep_percentage = 0
            sleep_count = 0
            for t in timeslot:
                if t["STATE"] == 2 and t["IN_BED"] == 1:
                    sleep_count+=1
            sleep_percentage = sleep_count/len(timeslot)

            if (diff.total_seconds() > sleeping_threshold and sleep_percentage >= 0.3):
                start_sleep_time.append(timeslot[0]["TIMESTAMP"])
                wake_up_time.append(timeslot[-1]["TIMESTAMP"])
                sleeping_hours.append(diff.total_seconds())
                
                result.append({
                    "data_length":len(timeslot),
                    "start":timeslot[0],
                    "end":timeslot[-1]
                })

    inroom_arr = []

    for date in inroom_analysis:
        inroom_second = 0
        for ts in inroom_analysis[date]:
            inroom_arr.append({
                "from":ts[0]["TIMESTAMP"],
                "to":ts[-1]["TIMESTAMP"]
            })
            diff = ts[-1]["TIMESTAMP"] - ts[0]["TIMESTAMP"]
            inroom_second += diff.total_seconds()

        inroom_seconds.append(inroom_second)

    print(result)

    sleeping_longest = int(max(sleeping_hours))
    sleeping_shortest = int(min(sleeping_hours))
    sleeping_average = int(sum(sleeping_hours) / len(sleeping_hours))

    bed_longest = int(max(time_in_bed))
    bed_shortest = int(min(time_in_bed))
    bed_average = int(sum(time_in_bed) / len(time_in_bed))

    inroom_longest = int(max(inroom_seconds))
    inroom_shortest = int(min(inroom_seconds))
    inroom_average = int(sum(inroom_seconds) / len(inroom_seconds))

    average_bedtime,earliest_bedtime,latest_bedtime = bedtime_processing(start_sleep_time)
    average_waketime,earliest_waketime,latest_waketime = waketime_processing(wake_up_time)

    disruptions.append(current_disruption)
    disruptions = disruptions[1:]

    disruption_most = int(max(disruptions))
    disruption_least = int(min(disruptions))
    disruption_average = sum(disruptions) / len(disruptions)

    breath_highest = max(breath_rate)
    breath_lowest = min(breath_rate)
    breath_average = sum(breath_rate) / len(breath_rate)

    heart_highest = max(heart_rate)
    heart_lowest = min(heart_rate)
    heart_average = sum(heart_rate) / len(heart_rate)

    return {
        "sleeping_hour":{
            "average":seconds_to_text(sleeping_average),
            "longest":seconds_to_text(sleeping_longest),
            "shortest":seconds_to_text(sleeping_shortest),
            "previous_average": "-",
        },
        "time_in_bed":{
            "average":seconds_to_text(bed_average),
            "longest":seconds_to_text(bed_longest),
            "shortest":seconds_to_text(bed_shortest),
            "previous_average": "-",
        },
        "bed_time":{
            "average":average_bedtime,
            "latest":latest_bedtime,
            "earliest":earliest_bedtime,
            "previous_average": "-",
        },
        "wake_up_time":{
            "average":average_waketime,
            "latest":latest_waketime,
            "earliest":earliest_waketime,
            "previous_average": "-",
        },
        "in_room":{
            "average":seconds_to_text(inroom_average),
            "longest":seconds_to_text(inroom_longest),
            "shortest":seconds_to_text(inroom_shortest),
            "previous_average":"-"
        },
        "sleep_disruption":{
            "average":round(disruption_average,3),
            "most":disruption_most,
            "least":disruption_least,
            "previous_average":"-"
        },
        "breath_rate":{
            "average":round(breath_average,3),
            "highest":breath_highest,
            "lowest":breath_lowest,
            "previous_average":"-"
        },
        "heart_rate":{
            "average":round(heart_average,3),
            "highest":heart_highest,
            "lowest":heart_lowest,
            "previous_average":"-"
        }
    }

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

def process_time(arr):
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
    temp = [minutes_to_am_pm_time(datetime_to_minutes(dt)) for dt in arr]

    # Find the earliest, latest, and average bedtime values
    earliest_minutes = min(bedtime_minutes)
    latest_minutes = max(bedtime_minutes)
    average_minutes = sum(bedtime_minutes) / len(bedtime_minutes)

    

    # Convert the results back to 12-hour AM/PM time format
    earliest = minutes_to_am_pm_time(earliest_minutes)
    latest = minutes_to_am_pm_time(latest_minutes)
    average = minutes_to_am_pm_time(int(average_minutes))

    return average,earliest,latest,temp
