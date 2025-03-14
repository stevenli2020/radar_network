import mysql.connector
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import json
import time


np.set_printoptions(precision=2)
config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}
now = datetime.now()
format_now = now.strftime('%Y-%m-%d %H:%M:%S.%f')

def getSummaryDataofPosition(data):
    start_time = time.time()
    N = 10 # N is the dividing factor, e.g. 10 means every meter will be divided to 10 data points
    sigma = 2
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    result = defaultdict(list)
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
    sql = "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND PY IS NOT NULL;" %(data['DEVICEMAC'], timeRange)
    cursor.execute(sql)
    dbresult = cursor.fetchone() 
    # print(dbresult)
    # print("first sql time: %s s"%(time.time()-start_time))
    if dbresult[0] == None and dbresult[1] == None:
        # print("No data")
        result["ERROR"].append({'Message': 'No data!'})
        # print(result)
        return result
    X_SHIFT = int(dbresult[0]*N)
    X_SIZE = int(dbresult[0]*N)*4
    Y_SHIFT = int(dbresult[1]*N)
    Y_SIZE = int(dbresult[1]*N)*4

    HMAP = np.zeros((X_SIZE, Y_SIZE))
    HMAP2 = np.zeros((X_SHIFT, X_SHIFT))
        

    sql = "SELECT CONCAT(ROUND(PX*%d),',',ROUND(PY*%d)) AS XY,COUNT(*) AS CNT FROM Gaitmetrics.PROCESSED_DATA WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND `PY` IS NOT NULL GROUP BY XY ORDER BY XY ASC;" %(N, N, data['DEVICEMAC'], timeRange)
    # print(sql)
    cursor.execute(sql)
    dbresult = cursor.fetchall() 
    cursor.close()
    connection.close() 
    # print("second sql time: %s s"%(time.time()-start_time))
    # print(dbresult)
    if not dbresult:
        # print("No data")
        result["ERROR"].append({'DATA': 'No Data!'})
        return result
    for row in dbresult:
        # print(row)
        X,Y = row[0].split(",")   
        CNT = int(row[1])
        # print(int(X), int(Y), X_SHIFT+int(X), Y_SHIFT+int(Y), CNT)
        HMAP[X_SHIFT+int(X)][Y_SHIFT+int(Y)] += CNT

    # print(HMAP)
    # Apply Gaussian blur with a specified sigma value

    NEW_HMAP = gaussian_blur(HMAP, sigma, start_time)
    print("after gaussian time: %s s"%(time.time()-start_time))
    # print("\nOriginal HMAP:")
    # print(HMAP)
    # print("\nBlurred HMAP:")
    # print(NEW_HMAP)
    # print("MAX VALUE: %f" %(np.max(NEW_HMAP)))

    # print("\nShifted HMAP:")
    HMAP2 = NEW_HMAP[X_SHIFT:X_SHIFT*2,Y_SHIFT:Y_SHIFT*2]
    # print(HMAP2)

    DATA = []
    # print("\nUnpack data:")
    # print("before loop: %s s"%(time.time()-start_time))
    for X in range(0, X_SHIFT-1):
        for Y in range(0, Y_SHIFT-1):
            DATA.append([round(X, 1),round(Y, 1), round(HMAP2[X,Y],2)])
    # print("after loop: %s s"%(time.time()-start_time))
    # print(DATA)           
    result["DATA"].append(DATA)
    return result



def gaussian_blur2(array, sigma, start_time):
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


def gaussian_blur(array, sigma, start_time):
    size = int(2 * np.ceil(3 * sigma) + 1)  # Determine the kernel size based on sigma
    kernel = np.fromfunction(lambda x, y: (1 / (2 * np.pi * sigma ** 2)) * np.exp(
        -((x - size // 2) ** 2 + (y - size // 2) ** 2) / (2 * sigma ** 2)), (size, size))
    kernel = kernel / np.sum(kernel)  # Normalize the kernel

    blurred_array = np.zeros_like(array, dtype=float)

    # Pad the array to handle border pixels
    padded_array = np.pad(array, ((size // 2, size // 2), (size // 2, size // 2)), mode='constant')

    # Apply the Gaussian filter
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            window = padded_array[i:i + size, j:j + size]
            blurred_array[i, j] = np.sum(window * kernel)

    return blurred_array

INPUT={}
INPUT['TIME']="WEEK"
INPUT['DEVICEMAC']="F412FAE26208"
R = getSummaryDataofPosition(INPUT)
print(R)
