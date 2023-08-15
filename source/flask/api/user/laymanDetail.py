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
                "longest":"-",
                "shortest":"-",
                "previous_average":"-"
            },
            "wake_up_time":{
                "average":"-",
                "longest":"-",
                "shortest":"-",
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
            }
        }
    }
    sql = "SELECT CONCAT(ROOM_NAME,'@',ROOM_LOC) AS room_name FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s';"%(room_id)
    cursor.execute(sql)
    room_name = cursor.fetchone()
    if (room_name):
        result["data"]["room_name"] = room_name["room_name"]

    sql = "SELECT pd.`TIMESTAMP`,pd.`STATE`,pd.`IN_BED` FROM `RL_ROOM_MAC` rrm LEFT JOIN `PROCESSED_DATA` pd ON rrm.MAC=pd.MAC WHERE WEEK(pd.`TIMESTAMP`, 1) = WEEK(CURDATE(), 1) AND YEAR(pd.`TIMESTAMP`) = YEAR(CURDATE()) AND rrm.ROOM_UUID='%s';"%(room_id)
    cursor.execute(sql)
    processed_data = cursor.fetchall()
    if (processed_data):
        analysis = analyseLaymanData(processed_data)
        result["data"]["sleeping_hour"] = analysis["sleeping_hour"]
        result["data"]["time_in_bed"] = analysis["time_in_bed"]
        result["data"]["wake_up_time"] = analysis["wake_up_time"]
        result["data"]["bed_time"] = analysis["bed_time"]

    #     print(data)
    #     result["DATA"].append({"id":data["Id"]})
    # result["DATA"] =  #[{"MAC": MAC} for (MAC) in cursor]
    
    cursor.close()
    connection.close()
    return result

def analyseLaymanData(data):
    #seconds
    threshold = 60 * 10
    sleeping_threshold = 60 * 15

    analysis = {
        "timeslot":[]
    }

    curr_timeslot = 0

    last_row = None

    sleeping = False

    cache = []

    for row in data:

        if (len(analysis["timeslot"]) <= curr_timeslot):
            analysis["timeslot"].append([])

        if (row["STATE"] == 2 and row["IN_BED"] == 1):
            sleeping = True
            if (len(cache)>0):
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

    result = []

    sleeping_hours = []
    time_in_bed = []
    start_sleep_time = []
    wake_up_time = []

    for timeslot in analysis["timeslot"]:
        if (len(timeslot)>1):
            diff = timeslot[-1]["TIMESTAMP"] - timeslot[0]["TIMESTAMP"]
            
            time_in_bed.append(diff.total_seconds())

            if (diff.total_seconds() > sleeping_threshold):
                start_sleep_time.append(timeslot[0]["TIMESTAMP"])
                wake_up_time.append(timeslot[-1]["TIMESTAMP"])
                sleeping_hours.append(diff.total_seconds())
                
                result.append({
                    "data_length":len(timeslot),
                    "start":timeslot[0],
                    "end":timeslot[-1]
                })

    sleeping_longest = int(max(sleeping_hours))
    sleeping_shortest = int(min(sleeping_hours))
    sleeping_average = int(sum(sleeping_hours) / len(sleeping_hours))

    bed_longest = int(max(time_in_bed))
    bed_shortest = int(min(time_in_bed))
    bed_average = int(sum(time_in_bed) / len(time_in_bed))

    

    average_bedtime,earliest_bedtime,latest_bedtime = process_time(start_sleep_time)
    average_waketime,earliest_waketime,latest_waketime = process_time(wake_up_time)

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
            "longest":latest_bedtime,
            "shortest":earliest_bedtime,
            "previous_average": "-",
        },
        "wake_up_time":{
            "average":average_waketime,
            "longest":latest_waketime,
            "shortest":earliest_waketime,
            "previous_average": "-",
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
    if seconds > 0:
        result += f"{seconds}s"

    return result

def process_time(arr):
    # Function to convert datetime to minutes since midnight
    def datetime_to_minutes(dt):
        return dt.hour * 60 + dt.minute

    # Convert bedtime_array to minutes since midnight
    bedtime_minutes = [datetime_to_minutes(dt) for dt in arr]

    # Find the earliest, latest, and average bedtime values
    earliest_minutes = min(bedtime_minutes)
    latest_minutes = max(bedtime_minutes)
    average_minutes = sum(bedtime_minutes) / len(bedtime_minutes)

    # Function to convert minutes since midnight to 12-hour AM/PM time format
    def minutes_to_am_pm_time(minutes):
        hours, minutes = divmod(minutes, 60)
        period = "AM" if hours < 12 else "PM"
        if hours == 0:
            hours = 12  # Adjust 0 to 12 AM
        elif hours > 12:
            hours -= 12  # Convert to 12-hour format
        return f"{hours:02}:{minutes:02} {period}"

    # Convert the results back to 12-hour AM/PM time format
    earliest = minutes_to_am_pm_time(earliest_minutes)
    latest = minutes_to_am_pm_time(latest_minutes)
    average = minutes_to_am_pm_time(int(average_minutes))

    return average,earliest,latest