from datetime import datetime, timedelta
import mysql.connector
from user.config import config, vernemq

config = config()

def getLaymanData(date,room_uuid):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    result = {
        "data":{
            "room_id":room_uuid,
            "room_name":None,
            "sleeping_hour":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            },
            "bed_time":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            },
            "wake_up_time":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            },
            "time_in_bed":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            },
            "in_room":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            },
            "sleep_disruption":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            },
            "breath_rate":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            },
            "heart_rate":{
                "average":"-",
                "max":"-",
                "min":"-",
                "previous_average":"-"
            }
        }
    }
    sql = "SELECT CONCAT(ROOM_NAME,'@',ROOM_LOC) AS room_name, ID FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_UUID='%s';"%(room_uuid)
    cursor.execute(sql)
    room_name = cursor.fetchone()
    if (room_name):
        result["data"]["room_name"] = room_name["room_name"]
        room_id = room_name["ID"]

        eow_datetime = datetime.strptime(date, "%Y-%m-%d")

        # Subtract 7 days
        previous_eow = eow_datetime - timedelta(days=7)

        previous_date = previous_eow.strftime("%Y-%m-%d")

        sleeping_hour_max,sleeping_hour_min,sleeping_hour_average = get_data_from_analysis(date,room_id,'sleeping_hour')
        result["data"]["sleeping_hour"]["max"] = sleeping_hour_max
        result["data"]["sleeping_hour"]["min"] = sleeping_hour_min
        result["data"]["sleeping_hour"]["average"] = sleeping_hour_average
        temp,temp,sleeping_hour_previous = get_data_from_analysis(previous_date,room_id,'sleeping_hour')
        result["data"]["sleeping_hour"]["previous_average"] = sleeping_hour_previous

        bed_time_max,bed_time_min,bed_time_average = get_data_from_analysis(date,room_id,'bed_time')
        result["data"]["bed_time"]["max"] = bed_time_max
        result["data"]["bed_time"]["min"] = bed_time_min
        result["data"]["bed_time"]["average"] = bed_time_average
        temp,temp,bed_time_previous = get_data_from_analysis(previous_date,room_id,'bed_time')
        result["data"]["bed_time"]["previous_average"] = bed_time_previous

        wake_up_time_max,wake_up_time_min,wake_up_time_average = get_data_from_analysis(date,room_id,'wake_up_time')
        result["data"]["wake_up_time"]["max"] = wake_up_time_max
        result["data"]["wake_up_time"]["min"] = wake_up_time_min
        result["data"]["wake_up_time"]["average"] = wake_up_time_average
        temp,temp,wake_up_time_previous = get_data_from_analysis(previous_date,room_id,'wake_up_time')
        result["data"]["wake_up_time"]["previous_average"] = wake_up_time_previous

        time_in_bed_max,time_in_bed_min,time_in_bed_average = get_data_from_analysis(date,room_id,'time_in_bed')
        result["data"]["time_in_bed"]["max"] = time_in_bed_max
        result["data"]["time_in_bed"]["min"] = time_in_bed_min
        result["data"]["time_in_bed"]["average"] = time_in_bed_average
        temp,temp,time_in_bed_previous = get_data_from_analysis(previous_date,room_id,'time_in_bed')
        result["data"]["time_in_bed"]["previous_average"] = time_in_bed_previous

        in_room_max,in_room_min,in_room_average = get_data_from_analysis(date,room_id,'in_room')
        result["data"]["in_room"]["max"] = in_room_max
        result["data"]["in_room"]["min"] = in_room_min
        result["data"]["in_room"]["average"] = in_room_average
        temp,temp,in_room_previous = get_data_from_analysis(previous_date,room_id,'in_room')
        result["data"]["in_room"]["previous_average"] = in_room_previous

        sleep_disruption_max,sleep_disruption_min,sleep_disruption_average = get_data_from_analysis(date,room_id,'sleep_disruption')
        result["data"]["sleep_disruption"]["max"] = sleep_disruption_max
        result["data"]["sleep_disruption"]["min"] = sleep_disruption_min
        result["data"]["sleep_disruption"]["average"] = sleep_disruption_average
        temp,temp,sleep_disruption_previous = get_data_from_analysis(previous_date,room_id,'sleep_disruption')
        result["data"]["sleep_disruption"]["previous_average"] = sleep_disruption_previous

        breath_rate_max,breath_rate_min,breath_rate_average = get_data_from_analysis(date,room_id,'breath_rate')
        result["data"]["breath_rate"]["max"] = breath_rate_max
        result["data"]["breath_rate"]["min"] = breath_rate_min
        result["data"]["breath_rate"]["average"] = breath_rate_average
        temp,temp,breath_rate_previous = get_data_from_analysis(previous_date,room_id,'breath_rate')
        result["data"]["breath_rate"]["previous_average"] = breath_rate_previous

        heart_rate_max,heart_rate_min,heart_rate_average = get_data_from_analysis(date,room_id,'heart_rate')
        result["data"]["heart_rate"]["max"] = heart_rate_max
        result["data"]["heart_rate"]["min"] = heart_rate_min
        result["data"]["heart_rate"]["average"] = heart_rate_average
        temp,temp,heart_rate_previous = get_data_from_analysis(previous_date,room_id,'heart_rate')
        result["data"]["heart_rate"]["previous_average"] = heart_rate_previous

    cursor.close()
    connection.close()
    return result

def get_data_from_analysis(date,room_id,type):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT max,min,average FROM `ANALYSIS` WHERE `TYPE`='%s' AND `ROOM_ID`=%s AND `EOW`='%s' UNION ALL SELECT '-' AS `max`,'-' AS `min`,'-' AS `average` FROM ANALYSIS WHERE (SELECT COUNT(*) FROM `ANALYSIS` WHERE `TYPE`='%s' AND `ROOM_ID`=%s AND `EOW`='%s')=0 LIMIT 1;"%(type,room_id,date,type,room_id,date)
    cursor.execute(sql)
    data = cursor.fetchone()
    min = data["min"]
    max = data["max"]
    average = data["average"]
    cursor.close()
    connection.close()

    return max,min,average