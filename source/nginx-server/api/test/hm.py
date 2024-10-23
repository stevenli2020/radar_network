#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2
import numpy as np
import mysql.connector
import sys
# np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)
config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}

def gaussian_blur(array, sigma):
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


N = 10          # N is the dividing factor, e.g. 10 means every meter will be divided to 10 data points
sigma = 2      #
INPUT={}
INPUT['TIME']="1 WEEK"
INPUT['DEVICEMAC']="F412FAE26208"

connection = mysql.connector.connect(**config)
cursor = connection.cursor(dictionary=True)        


sql = "SELECT ROUND((MAX(PX)-MIN(PX)),1) AS DELTA_X,ROUND((MAX(PY)-MIN(PY)),1) AS DELTA_Y FROM `PROCESSED_DATA` WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND PY IS NOT NULL;" %(INPUT['DEVICEMAC'], INPUT['TIME'])
# print(sql)
# exit()  
cursor.execute(sql)
dbresult = cursor.fetchone() 
if dbresult == None:
    print("No data")
    exit()
    
X_SHIFT = int(dbresult["DELTA_X"]*N)
X_SIZE = int(dbresult["DELTA_X"]*N)*4
Y_SHIFT = int(dbresult["DELTA_Y"]*N)
Y_SIZE = int(dbresult["DELTA_Y"]*N)*4

# print("X_SIZE = %d, Y_SIZE = %d" %(X_SIZE, Y_SIZE))
# print("X_SHIFT = %d, Y_SHIFT = %d" %(X_SHIFT, Y_SHIFT))
# exit()
# init 2D matrix
HMAP = np.zeros((X_SIZE, Y_SIZE))
HMAP2 = np.zeros((X_SHIFT, X_SHIFT))

sql = "SELECT CONCAT(ROUND(PX*%d),',',ROUND(PY*%d)) AS XY,COUNT(*) AS CNT FROM `PROCESSED_DATA` WHERE MAC='%s' AND `TIMESTAMP` > DATE_SUB(NOW(), INTERVAL %s) AND `PX` IS NOT NULL AND `PY` IS NOT NULL GROUP BY XY ORDER BY XY ASC;" %(N, N, INPUT['DEVICEMAC'], INPUT['TIME'])
# print(sql)
cursor.execute(sql)
dbresult = cursor.fetchall() 
cursor.close()
connection.close() 

if dbresult == None:
    print("No data")
    exit()
for row in dbresult:
    # print(row)
    X,Y = row["XY"].split(",")   
    CNT = int(row["CNT"])
    # print(int(X), int(Y), X_SHIFT+int(X), Y_SHIFT+int(Y), CNT)
    HMAP[X_SHIFT+int(X)][Y_SHIFT+int(Y)] += CNT

# print(HMAP)
# Apply Gaussian blur with a specified sigma value

NEW_HMAP = gaussian_blur(HMAP, sigma)

print("\nOriginal HMAP:")
print(HMAP)
print("\nBlurred HMAP:")
print(NEW_HMAP)
# print("MAX VALUE: %f" %(np.max(NEW_HMAP)))

print("\nShifted HMAP:")
HMAP2 = NEW_HMAP[X_SHIFT:X_SHIFT*2,Y_SHIFT:Y_SHIFT*2]
print(HMAP2)

DATA = []
print("\nUnpack data:")
for X in range(0, X_SHIFT-1):
    for Y in range(0, Y_SHIFT-1):
        DATA.append([X,Y, round(HMAP2[X,Y],2)])
        
print(DATA)


