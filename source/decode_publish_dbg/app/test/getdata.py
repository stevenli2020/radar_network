from collections import defaultdict
import numpy as np 

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
    
def getPositionData(connection, data):
    # start_time = time.time()
    N = 10 # N is the dividing factor, e.g. 10 means every meter will be divided to 10 data points
    sigma = 3
    # connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
    result["_DBG"] = []
    if not 'DEVICEMAC' in data:
        result["ERROR"].append({'Message': 'MAC is empty!'})
        return result
    t = data['TIME']
    timeRange = "10 DAY"
    if t == "HOUR":
        timeRange = "1 HOUR"
    elif t == "DAY":
        timeRange = "1 DAY"
    elif t == "WEEK":
        timeRange = "1 WEEK"
    else:
        timeRange = "1 MONTH"   

    sql = "SELECT ROOM_X*%d AS X_RANGE,ROOM_Y*%d AS Y_RANGE FROM ROOMS_DETAILS RIGHT JOIN RL_ROOM_MAC ON ROOMS_DETAILS.ROOM_UUID=RL_ROOM_MAC.ROOM_UUID WHERE RL_ROOM_MAC.MAC='%s';" %(N, N, data['DEVICEMAC'])
    cursor.execute(sql)
    dbresult = cursor.fetchone()    
    X_RANGE = int(dbresult[0])
    Y_RANGE = int(dbresult[1])  
        
    sql = "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y,ROUND(MIN(PX),1),ROUND(MIN(PY),1) FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND PY IS NOT NULL;" %(data['DEVICEMAC'], timeRange)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    # print(dbresult)
    if dbresult[0] == None and dbresult[1] == None:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        # print(result)
        return result
    X_SIZE = int(dbresult[0]*N)
    Y_SIZE = int(dbresult[1]*N)
    X_MIN =  int(dbresult[2]*N)
    Y_MIN =  int(dbresult[3]*N)

    HMAP = np.zeros((X_RANGE*2, Y_RANGE*2))

    sql = "SELECT CONCAT(ROUND(PX*%d),',',ROUND(PY*%d)) AS XY,COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND `PY` IS NOT NULL GROUP BY XY ORDER BY XY ASC;" %(N, N, data['DEVICEMAC'], timeRange)
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    cursor.close()
    connection.close() 
    # print("second sql time: %s s"%(time.time()-start_time))
    print(dbresult)
    
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'DATA': 'No Data!'})
        return result
    for row in dbresult:
        # print(row)
        X,Y = row[0].split(",")   
        CNT = int(row[1])
        # print(int(X), int(Y), X_SHIFT+int(X), Y_SHIFT+int(Y), CNT)
        try:
            HMAP[X_RANGE+int(X)][Y_RANGE+int(Y)] += CNT
        except:
            continue
    # print(HMAP)
    # Apply Gaussian blur with a specified sigma value
    NEW_HMAP = gaussian_blur(HMAP, sigma)
    DATA = []
    MAX = np.amax(NEW_HMAP)
    for X in range(0, X_RANGE):
        for Y in range(0, Y_RANGE):
            try:
                VALUE = round(NEW_HMAP[X+X_RANGE,Y+Y_RANGE],2)
            except:
                VALUE = 0
            if VALUE > 0.03 * MAX:
                DATA.append([round(X, 1),round(Y, 1), VALUE])
    DATA.append([X_RANGE, Y_RANGE, 0]) 
    DATA.append([0, 0, 0]) 
    result["DATA"].append(DATA)
    result["MAX"].append(MAX)
    return result


def gaussian_blur(array, sigma):
    size = int(2 * np.ceil(3 * sigma) + 1)  # Determine the kernel size based on sigma
    # print("before kernel loop: %s s"%(time.time()-start_time))
    kernel = np.fromfunction(lambda x, y: (1 / (2 * np.pi * sigma ** 2)) * np.exp(
        -((x - size // 2) ** 2 + (y - size // 2) ** 2) / (2 * sigma ** 2)), (size, size))
    kernel = kernel / np.sum(kernel)  # Normalize the kernel

    blurred_array = np.zeros_like(array, dtype=float)
    # print("before padded loop: %s s"%(time.time()-start_time))
    # Pad the array to handle border pixels
    padded_array = np.pad(array, ((size // 2, size // 2), (size // 2, size // 2)), mode='constant')
    # print("before Gaussian filter loop: %s s"%(time.time()-start_time))
    # Apply the Gaussian filter
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            window = padded_array[i:i + size, j:j + size]
            blurred_array[i, j] = np.sum(window * kernel)
    # print("after Gaussian filter loop: %s s"%(time.time()-start_time))
    return blurred_array
