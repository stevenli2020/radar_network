from collections import defaultdict

def getVitalData(CONN, PARAM):
    cursor = CONN.cursor()
    result = defaultdict(list)    
    sql = "SELECT GROUP_CONCAT(MAC) FROM Gaitmetrics.ROOMS_DETAILS LEFT JOIN Gaitmetrics.RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID = RL_ROOM_MAC.ROOM_UUID WHERE ROOMS_DETAILS.ROOM_UUID ='%s'" % (PARAM["ROOM_UUID"])
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    # print(dbresult)   
    try:
        db = dbresult[0].split(',')
        List = "IN ('"+db[0]+"','"+db[1]+"')"
    except:
        # print("No data related to room name")
        result["ERROR"].append({'Message': 'No data related to room name!'})
        return result
    sql = "SELECT DATE_FORMAT(TIMESTAMP, \'%%Y-%%m-%%d %%H:%%i\') AS T, ROUND(AVG(HEART_RATE),1) AS HR, ROUND(AVG(BREATH_RATE),1) AS BR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s) AND HEART_RATE IS NOT NULL AND HEART_RATE !=0 AND BREATH_RATE IS NOT NULL AND BREATH_RATE !=0 GROUP BY T ORDER BY `T` ASC;" %(List, PARAM['TIME'])
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        return result
    result['DATA'].append(dbresult)
    sql = "SELECT ROUND(AVG(HEART_RATE), 1) as AHR, ROUND(AVG(BREATH_RATE), 1) as ABR FROM Gaitmetrics.PROCESSED_DATA WHERE MAC %s AND HEART_RATE > 0 AND BREATH_RATE > 0 AND TIMESTAMP > DATE_SUB(NOW(), INTERVAL %s);" %(List, PARAM['TIME'])
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    result["AVG"].append(dbresult)
    cursor.close()
    CONN.close()
    return result    
    