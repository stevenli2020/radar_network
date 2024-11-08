import math
from unittest import result
import mysql.connector
from user.config import config
from datetime import datetime, timedelta
from user.parseFrame import *
import pytz
import copy
from collections import defaultdict
import numpy as np
import json
import time
import pandas as pd
from tzlocal import get_localzone

config = config()
now = datetime.now()
format_now = now.strftime("%Y-%m-%d %H:%M:%S.%f")


def getSaveRawData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = {}
    now = datetime.now()
    if data["CUSTOM"] == 1:  # check request time include custom time
        ts = data["TIME"].split("-")  # split request time into start time and stop time
        sql = (
            "SELECT * FROM RECORD_RAW_DATA WHERE MAC='%s' AND TIME BETWEEN '%s' AND '%s' "
            % (data["DEVICEMAC"], ts[0], ts[-1])
        )  # sql query
    else:
        t = data["TIME"].split(" ")[0]
        if "MINUTE" in data["TIME"]:  # check request time in minute
            before = now - timedelta(minutes=int(t))  # minus current time t minute
            format_before = before.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )  # change time format
        elif "HOUR" in data["TIME"]:  # check reqest time in hour
            before = now - timedelta(hours=int(t))  # minus current time t hour
            format_before = before.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )  # change time format
        sql = (
            "SELECT * FROM RECORD_RAW_DATA WHERE MAC='%s' AND TIME BETWEEN '%s' AND '%s' "
            % (data["DEVICEMAC"], format_before, format_now)
        )  # sql query
    cursor.execute(sql)
    dbresult = cursor.fetchall()  # get all retrieve data
    if dbresult:
        my_list = []
        for x in dbresult:
            in_data = str(x[3]).split(",")  # split raw data into individual
            # print(in_data)
            byteAD = bytearray()
            for x in in_data:
                ts, hexD = x.split(":")  # split timestamp and radar raw data
                if "'" in hexD:
                    hexD = hexD.replace("'", "")
                    byteAD = bytearray.fromhex(hexD)  # convert hex string to byte array
                else:
                    byteAD = bytearray.fromhex(hexD)  # convert hex string to byte array
                tz = pytz.timezone("Asia/Singapore")
                ts = datetime.fromtimestamp(
                    float(ts), tz
                )  # change time into timestamp format
                if len(hexD) > 104:  # check raw data is not empty
                    outputDict = parseStandardFrame(
                        byteAD
                    )  # convert byte array data into pointcloud data
                    print(outputDict)
                    decodeData = {}
                    if "numDetectedTracks" in outputDict:
                        decodeData["timestamp"] = str(ts)[:23]
                        decodeData["numDetectedTracks"] = outputDict[
                            "numDetectedTracks"
                        ]
                    # if "numDetectedPoints" in outputDict:
                    #     decodeData['numDetectedPoints'] = outputDict['numDetectedPoints']
                    if "trackData" in outputDict:
                        decodeData["trackData"] = outputDict["trackData"].tolist()
                    if decodeData:
                        dict_copy = copy.deepcopy(decodeData)
                        my_list.append(dict_copy)
            # result["DATA"] = [{"ID": ID, "TIME": TIME, "MAC": MAC, "RAW_DATA": RAW_DATA} for (ID, TIME, MAC, RAW_DATA) in dbresult]
        if my_list:
            result["DATA"] = my_list
        else:
            result["CODE"] = 0
        # print(my_list)
    else:
        result["CODE"] = -1
    # result["DATA"] = [{"ID": ID, "TIME": TIME, "MAC": MAC, "RAW_DATA": RAW_DATA} for (ID, TIME, MAC, RAW_DATA) in cursor]
    cursor.close()
    connection.close()
    return result


def get_interval_tables(cursor, mode):
    cursor.execute("SELECT DATE_FORMAT(CURRENT_DATE(), '%Y-%m-%d') AS format_date")
    formatted_date = cursor.fetchall()[0][0]

    end_date = datetime.strptime(formatted_date, "%Y-%m-%d")
    if mode == "1 WEEK":
        start_date = end_date - timedelta(days=7)
    elif mode == "1 MONTH":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=1)

    return get_table_dates_between(
        cursor, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )


def get_table_dates_between(cursor, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    tables = []
    current_date = start_date

    while current_date <= end_date:
        table_name = "PROCESSED_DATA_" + current_date.strftime("%Y_%m_%d")
        if check_table_exist(cursor, table_name):
            tables.append("PROCESSED_DATA_" + current_date.strftime("%Y_%m_%d"))
        current_date += timedelta(days=1)

    return tables


def check_table_exist(cursor, table_name):
    table_exists_query = f"SHOW TABLES LIKE '{table_name}'"
    cursor.execute(table_exists_query)
    table_exists = cursor.fetchone()

    if not table_exists:
        return False
    return True


def getHistOfVitalData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    sql = (
        "SELECT GROUP_CONCAT(MAC) FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID WHERE ROOMS_DETAILS.ROOM_UUID ='%s'"
        % (data["ROOM_UUID"])
    )
    cursor.execute(sql)
    dbresult = cursor.fetchone()

    try:
        db = dbresult[0].split(",")
        MAC_LIST = ""
        for MAC in db:
            if MAC_LIST != "":
                MAC_LIST += ","
            MAC_LIST += f"""'{MAC}'"""
        List = f"IN ({MAC_LIST})"
    except:
        result["ERROR"].append({"Message": "No data related to room name!"})
        return result
    if data["CUSTOM"] != 1:
        tables = get_interval_tables(cursor, data["TIME"])
    else:
        tables = get_table_dates_between(cursor, data["TIMESTART"], data["TIMEEND"])

    dbresult = []

    for table in tables:
        try:
            mode = data.get("TIME")
            if data["CUSTOM"] != 1:
                sql = f"SELECT `TIMESTAMP`, `HEART_RATE`, `BREATH_RATE` FROM Gaitmetrics.{table} WHERE MAC {List} AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL {mode}) AND HEART_RATE IS NOT NULL AND HEART_RATE >0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE >0;"
            else:
                sql = f"SELECT `TIMESTAMP`, `HEART_RATE`, `BREATH_RATE` FROM Gaitmetrics.{table} WHERE MAC {List} AND HEART_RATE IS NOT NULL AND HEART_RATE >0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE >0;"

            print(sql)

            cursor.execute(sql)
            db_data = cursor.fetchall()
            if db_data:
                dbresult += db_data
        except Exception as e:
            print("No data in", table)

    if not dbresult:
        result["ERROR"].append({"Message": "No data!"})
        return result

    df = pd.DataFrame(dbresult, columns=["TIMESTAMP", "HEART_RATE", "BREATH_RATE"])

    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

    # Get the local timezone
    local_timezone = get_localzone()

    # Localize timestamps to the local timezone
    df["TIMESTAMP"] = df["TIMESTAMP"].dt.tz_localize(local_timezone)

    # # Subtract 8 hours from each timestamp
    df["TIMESTAMP"] = df["TIMESTAMP"].dt.tz_convert("UTC")

    # df['TIMESTAMP'] -= timedelta(hours=8)

    average_heart_rate = round(df["HEART_RATE"].mean(), 1)
    average_breath_rate = round(df["BREATH_RATE"].mean(), 1)

    df.set_index("TIMESTAMP", inplace=True)

    df_resampled = df.resample("1Min").mean()

    df_resampled.fillna(0, inplace=True)

    data_obj = {}
    for index, row in df_resampled.iterrows():
        t = int(index.timestamp())
        if not result.get("TIME_START"):
            result["TIME_START"].append(t)
        data_obj[t] = [round(row["HEART_RATE"], 1), round(row["BREATH_RATE"], 1)]

    new_query_data = []
    for t, d in data_obj.items():
        new_query_data.append(str(d[0]) + "," + str(d[1]))

    result_data = ";".join(new_query_data)
    result["DATA"].append(result_data)

    result["AVG"].append([average_heart_rate, average_breath_rate])
    cursor.close()
    connection.close()
    return result


def getHistOfWallData(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    sql = (
        "SELECT GROUP_CONCAT(DEVICES.MAC) FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID LEFT JOIN Gaitmetrics.DEVICES ON RL_ROOM_MAC.MAC=DEVICES.MAC WHERE ROOMS_DETAILS.ROOM_UUID ='%s' AND DEVICES.`TYPE` IN ('1','2');"
        % (data["ROOM_UUID"])
    )
    cursor.execute(sql)
    dbresult = cursor.fetchone()

    try:
        db = dbresult[0].split(",")
        MAC_LIST = ""
        for MAC in db:
            if MAC_LIST != "":
                MAC_LIST += ","
            MAC_LIST += f"""'{MAC}'"""
        List = f"IN ({MAC_LIST})"
    except:
        result["ERROR"].append({"Message": "No data related to room name!"})
        return result
    if data["CUSTOM"] != 1:
        tables = get_interval_tables(cursor, data["TIME"])
    else:
        tables = get_table_dates_between(cursor, data["TIMESTART"], data["TIMEEND"])

    dbresult = []

    for table in tables:
        try:
            mode = data.get("TIME")
            if data["CUSTOM"] != 1:
                sql = f"SELECT `TIMESTAMP`, 1 AS `WALL_DATA_COUNT` FROM Gaitmetrics.{table} WHERE MAC {List} AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL {mode});"
            else:
                sql = f"SELECT `TIMESTAMP`, 1 AS `WALL_DATA_COUNT` FROM Gaitmetrics.{table} WHERE MAC {List};"

            print(sql)

            cursor.execute(sql)
            db_data = cursor.fetchall()
            if db_data:
                dbresult += db_data
        except Exception as e:
            print("No data in", table)

    if not dbresult:
        result["ERROR"].append({"Message": "No data!"})
        return result

    df = pd.DataFrame(dbresult, columns=["TIMESTAMP", "WALL_DATA_COUNT"])

    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

    # Get the local timezone
    local_timezone = get_localzone()

    # Localize timestamps to the local timezone
    df["TIMESTAMP"] = df["TIMESTAMP"].dt.tz_localize(local_timezone)

    # # Subtract 8 hours from each timestamp
    df["TIMESTAMP"] = df["TIMESTAMP"].dt.tz_convert("UTC")

    df.set_index("TIMESTAMP", inplace=True)

    df_resampled = df.resample("1Min").count()

    df_resampled.fillna(0, inplace=True)

    data_obj = {}
    for index, row in df_resampled.iterrows():
        t = int(index.timestamp())
        if not result.get("TIME_START"):
            result["TIME_START"].append(t)
        data_obj[t] = [round(row["WALL_DATA_COUNT"], 1)]

    new_query_data = []
    for t, d in data_obj.items():
        new_query_data.append(str(d[0]))

    result_data = ";".join(new_query_data)
    result["DATA"].append(result_data)

    cursor.close()
    connection.close()
    return result


def getAnalyticDataofPosture(data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)

    # Initialize counters
    IN_ROOM_SECONDS = {"HOUR": 0, "DAY": 0, "WEEK": 0, "MONTH": 0}
    IN_BED_SECONDS = {"HOUR": 0, "DAY": 0, "WEEK": 0, "MONTH": 0}
    TIME_CONVERSION = {
        "HOUR": 60,
        "DAY": 1440,
        "WEEK": 10080,
        "MONTH": 43200,
    }  # Minutes in respective time periods

    # Fetch MAC addresses for the specified ROOM_UUID
    sql = """
        SELECT GROUP_CONCAT(MAC) 
        FROM Gaitmetrics.ROOMS_DETAILS 
        LEFT JOIN Gaitmetrics.RL_ROOM_MAC 
        ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID 
        WHERE ROOMS_DETAILS.ROOM_UUID = %s
    """
    cursor.execute(sql, (data["ROOM_UUID"],))
    dbresult = cursor.fetchone()

    if not dbresult or not dbresult[0]:
        result["ERROR"].append({"Message": "No data related to room name!"})
        return result

    mac_list = dbresult[0].split(",")
    mac_list_str = "IN (%s)" % ",".join("'" + mac + "'" for mac in mac_list)

    TIME_RANGE = ["HOUR", "DAY", "WEEK", "MONTH"]
    for T in TIME_RANGE:
        print(T)
        tables = get_interval_tables(cursor, f"1 {T}")

        if tables:
            combine_table_query = " UNION ".join(
                f"SELECT * FROM Gaitmetrics.{table} WHERE MAC {mac_list_str} AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL 1 {T}) AND OBJECT_LOCATION IS NOT NULL"
                for table in tables
            )
            sql = f"""
                SELECT 
                    COUNT(CASE WHEN IR>0 THEN 1 END) AS IR_COUNT,
                    COUNT(CASE WHEN IB>0 THEN 1 END) AS IB_COUNT 
                FROM (
                    SELECT 
                        DATE_FORMAT(TIMESTAMP, '%Y-%m-%d %H:%i') AS T, 
                        SUM(OBJECT_LOCATION) > 0 AS IR, 
                        SUM(IN_BED) > 0 AS IB 
                    FROM ({combine_table_query}) AS PROCESSED_DATA 
                    GROUP BY T
                ) AS T1
            """
            cursor.execute(sql)
            dbresult = cursor.fetchone()
            IR, IB = dbresult if dbresult else (0, 0)
        else:
            IR, IB = 0, 0

        IN_ROOM_SECONDS[T] = IR * 60
        IN_BED_SECONDS[T] = IB * 60

        conversion_factor = TIME_CONVERSION[T]
        if not result.get("DATA"):
            result["DATA"].append(
                {
                    f"IN_ROOM_SECONDS_{T}": IN_ROOM_SECONDS[T],
                    f"IN_BED_SECONDS_{T}": IN_BED_SECONDS[T],
                    f"IN_ROOM_PCT_{T}": round(IR * 100 / conversion_factor, 2),
                    f"IN_BED_PCT_{T}": round(IB * 100 / conversion_factor, 2),
                }
            )
        else:
            result["DATA"][0][f"IN_ROOM_SECONDS_{T}"] = IN_ROOM_SECONDS[T]
            result["DATA"][0][f"IN_BED_SECONDS_{T}"] = IN_BED_SECONDS[T]
            result["DATA"][0][f"IN_ROOM_PCT_{T}"] = round(
                IR * 100 / conversion_factor, 2
            )
            result["DATA"][0][f"IN_BED_PCT_{T}"] = round(
                IB * 100 / conversion_factor, 2
            )
        print(IR, IB)

    cursor.close()
    connection.close()
    return result


def getSummaryDataofPosition(data):
    # start_time = time.time()
    N = 10  # N is the dividing factor, e.g. 10 means every meter will be divided to 10 data points
    sigma = 3
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    result["_DBG"] = []
    if not "DEVICEMAC" in data:
        result["ERROR"].append({"Message": "MAC is empty!"})
        return result
    t = data["TIME"]
    timeRange = "10 DAY"
    if t == "HOUR":
        timeRange = "1 HOUR"
    elif t == "DAY":
        timeRange = "1 DAY"
    elif t == "WEEK":
        timeRange = "1 WEEK"
    elif t == "MONTH":
        timeRange = "1 MONTH"
    # macString = "IN ('"+db[0]+"','"+db[1]+"')"
    sql = (
        "SELECT ROOM_X*%d AS X_RANGE,ROOM_Y*%d AS Y_RANGE,ID FROM ROOMS_DETAILS RIGHT JOIN RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID WHERE RL_ROOM_MAC.MAC='%s';"
        % (N, N, data["DEVICEMAC"])
    )
    cursor.execute(sql)
    dbresult = cursor.fetchone()
    X_RANGE = int(dbresult[0])
    Y_RANGE = int(dbresult[1])
    ROOM_ID = int(dbresult[2])

    sql = (
        "SELECT X_START, X_END, Y_START, Y_END FROM ROOMS_FILTER_AREA WHERE ROOM_ID='%s';"
        % (ROOM_ID)
    )
    cursor.execute(sql)
    areas = cursor.fetchall()
    filtering = ""
    for area in areas:
        X_START = area[0]
        X_END = area[1]
        Y_START = area[2]
        Y_END = area[3]
        if filtering == "":
            filtering = f" AND ((PX < {X_START} OR PX > {X_END}) AND (PY < {Y_START} OR PY > {Y_END})"
        else:
            filtering += f" AND (PX < {X_START} OR PX > {X_END}) AND (PY < {Y_START} OR PY > {Y_END})"

    if filtering != "":
        filtering += ")"

    if t == "CUSTOM":
        tables = get_table_dates_between(cursor, data["TIMESTART"], data["TIMEEND"])
        sql = (
            "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y,ROUND(MIN(PX),1),ROUND(MIN(PY),1) FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` BETWEEN '%s' AND '%s' AND `PX` IS NOT NULL AND PY IS NOT NULL%s;"
            % (data["DEVICEMAC"], data["TIMESTART"], data["TIMEEND"], filtering)
        )
    else:
        tables = get_interval_tables(cursor, timeRange)
        sql = (
            "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y,ROUND(MIN(PX),1),ROUND(MIN(PY),1) FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND PY IS NOT NULL%s;"
            % (data["DEVICEMAC"], timeRange, filtering)
        )

    if len(tables) > 0:
        combine_table = []
        for table in tables:
            if t == "CUSTOM":
                combine_table.append(
                    f"""SELECT * FROM Gaitmetrics.{table} WHERE MAC='{data['DEVICEMAC']}' AND `PX` IS NOT NULL AND PY IS NOT NULL{filtering}"""
                )
            else:
                combine_table.append(
                    f"""SELECT * FROM Gaitmetrics.{table} WHERE MAC='{data['DEVICEMAC']}' AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL {timeRange}) AND `PX` IS NOT NULL AND PY IS NOT NULL{filtering}"""
                )

        combine_table_query = " UNION ".join(combine_table)
        sql = f"SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y,ROUND(MIN(PX),1),ROUND(MIN(PY),1) FROM ({combine_table_query}) AS PROCESSED_DATA;"
        cursor.execute(sql)
        dbresult = cursor.fetchone()
    else:
        dbresult = (None, None)

    # print(dbresult)
    if dbresult[0] == None and dbresult[1] == None:
        # print("No data")
        result["ERROR"].append({"Message": "No data!"})
        # print(result)
        return result
    X_SIZE = int(dbresult[0] * N)
    Y_SIZE = int(dbresult[1] * N)
    X_MIN = int(dbresult[2] * N)
    Y_MIN = int(dbresult[3] * N)

    HMAP = np.zeros((X_RANGE * 3, Y_RANGE * 3))
    if len(tables) > 0:
        combine_table = []
        for table in tables:
            if t == "CUSTOM":
                combine_table.append(
                    f"""SELECT * FROM Gaitmetrics.{table} WHERE MAC='{data['DEVICEMAC']}' AND `PX` IS NOT NULL AND PY IS NOT NULL{filtering}"""
                )
            else:
                combine_table.append(
                    f"""SELECT * FROM Gaitmetrics.{table} WHERE MAC='{data['DEVICEMAC']}' AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL {timeRange}) AND `PX` IS NOT NULL AND PY IS NOT NULL{filtering}"""
                )

        combine_table_query = " UNION ".join(combine_table)
        sql = f"SELECT CONCAT(ROUND(PX*{N}),',',ROUND(PY*{N})) AS XY,COUNT(*) AS CNT FROM ({combine_table_query}) AS PROCESSED_DATA GROUP BY XY ORDER BY XY ASC;"

        cursor.execute(sql)
        dbresult = cursor.fetchall()
    else:
        dbresult = []

    cursor.close()
    connection.close()
    # print("second sql time: %s s"%(time.time()-start_time))
    # print(dbresult)
    # result["_DBG"]=dbresult
    if not dbresult:
        # print("No data")
        result["ERROR"].append({"DATA": "No Data!"})
        return result
    for row in dbresult:
        # print(row)
        X, Y = row[0].split(",")
        CNT = int(row[1])

        # print(int(X), int(Y), X_SHIFT+int(X), Y_SHIFT+int(Y), CNT)
        try:
            # result["_DBG"].append([X,Y,CNT])
            HMAP[X_RANGE + int(X)][Y_RANGE + int(Y)] += CNT
        except Exception as e:
            continue
    # print(HMAP)
    # Apply Gaussian blur with a specified sigma value
    NEW_HMAP = gaussian_blur(HMAP, sigma)
    DATA = []
    MAX = np.amax(NEW_HMAP)
    for X in range(0, X_RANGE):
        for Y in range(0, Y_RANGE):
            try:
                VALUE = round(NEW_HMAP[X + X_RANGE, Y + Y_RANGE], 2)
            except:
                VALUE = 0
            # result["_DBG"].append(VALUE)
            if VALUE > 0.03 * MAX:
                DATA.append([round(X, 1), round(Y, 1), VALUE])
    DATA.append([X_RANGE, Y_RANGE, 0])
    DATA.append([0, 0, 0])
    result["DATA"].append(DATA)
    result["MAX"].append(MAX)

    return result


def gaussian_blur(array, sigma):
    size = int(2 * np.ceil(3 * sigma) + 1)  # Determine the kernel size based on sigma
    # print("before kernel loop: %s s"%(time.time()-start_time))
    kernel = np.fromfunction(
        lambda x, y: (1 / (2 * np.pi * sigma**2))
        * np.exp(-((x - size // 2) ** 2 + (y - size // 2) ** 2) / (2 * sigma**2)),
        (size, size),
    )
    kernel = kernel / np.sum(kernel)  # Normalize the kernel

    blurred_array = np.zeros_like(array, dtype=float)
    # print("before padded loop: %s s"%(time.time()-start_time))
    # Pad the array to handle border pixels
    padded_array = np.pad(
        array, ((size // 2, size // 2), (size // 2, size // 2)), mode="constant"
    )
    # print("before Gaussian filter loop: %s s"%(time.time()-start_time))
    # Apply the Gaussian filter
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            window = padded_array[i : i + size, j : j + size]
            blurred_array[i, j] = np.sum(window * kernel)
    # print("after Gaussian filter loop: %s s"%(time.time()-start_time))
    return blurred_array
