#!/usr/bin/python3
# -*- coding: utf-8 -*-
# v=1.2

import paho.mqtt.client as mqtt
import mysql.connector
import time
from datetime import datetime, timedelta, timezone
import json
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
from json import JSONEncoder
from parseFrame1 import *
import statistics
import copy
import pytz
import _thread
import atexit
import requests
import threading
import multiprocessing
from multiprocessing import Process, Queue, Pool, Manager
##while 1: #time.sleep(10)

# brokerAddress="vernemq" 
# clientID="0002"
# userName="decode-publish"  
# userPassword="/-K3tuBhod3-FIzv"
# dataBuffer=[]
# SpecialSensors={}

#clientID = "1235"
#userName = "js-client2"
#userPassword = "c764eb2b5fa2d259dc667e2b9e195218"

brokerAddress="vernemq" 
clientID="0015"
userName="decode-publish-dbg-steven"  
userPassword="/-K3tuBhod3-FIzv"
dataBuffer=[]
SpecialSensors={}

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
}

# Parameters Initialization For Radar Analytics
wallStateParam = {}
ceilStateParam = {}
vitalStateParam = {}
devicesTbl = {}
algoCfg = {}

xShift = 0
yShift = 0
zShift = 1.0
rotXDegree = 0
rotYDegree = 0
rotZDegree = 0

radarType = 'vital'
mac = '123456'
aggregate_period = 2 # seconds
breathRate_MA = 0 
heartRate_MA = 0

manager = Manager()
# sharedList = manager.list()
# sharedList.append(wallStateParam)
# sharedList.append(ceilStateParam)
# sharedList.append(vitalStateParam)
# sharedDataBuffer = manager.list()
stateParam_sharedDict = manager.dict()
algoCfg_sharedDict = manager.dict()
devicesTbl_sharedDict = manager.dict()
macQueue = Queue()
stateParamQueue = Queue()
dataBufferQueue = Queue()
processDataQueue = Queue()

def cleanup():
    global mqttc
    mqttc.publish("/GMT/USVC/DECODE_PUBLISH/STATUS","DISCONNECTED",1,True)
    print("\nDisconnecting...\n")
    mqttc.disconnect()
    time.sleep(1)
    print("Exit\n")

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

# Decode, Process, and Publish MQTT Data Packets from Radar
# def decode_process_publish(mac, data, radarType, xShift, yShift, zShift, rotXDegree, rotYDegree, rotZDegree, aggregate_period):
def decode_process_publish(mac, data):
    global mqttc, config, aggregate_period, devicesTbl, breathRate_MA, heartRate_MA, algoCfg
    my_list = []
    print("algorithm configuration: ", algoCfg)
    # for x in data:
    print(len(data.items()))
    for ts_str, byteAD in data.items():
        print("parsing data")
        try:
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        if ts == 0:
            continue

        # if len(byteAD) > 52:
        if len(byteAD) > 0:
            # Error happens occasionally when decoding the raw data frame,
            # may require error analysis in future to find out the actual cause.
            try:
                outputDict = parseStandardFrame(byteAD)
            except:
                outputDict = None
                continue
            print(mac)
            # print(byteAD)
            # print(outputDict)
            # --------------------------------- Wall-Mounted Radar Tracking and Posture Analysis -------------------------------
            # ------------------------------------------------------------------------------------------------------------------
            DEVICE = devicesTbl[mac]
            if DEVICE["TYPE"] == '1':
                radarType = 'wall'
            elif DEVICE["TYPE"] == '2':
                radarType = 'ceil'
            elif DEVICE["TYPE"] == '3':
                radarType = 'vital'
            xShift = DEVICE["DEPLOY_X"]
            yShift = DEVICE["DEPLOY_Y"]
            zShift = DEVICE["DEPLOY_Z"] 
            rotXDegree = DEVICE["ROT_X"]
            rotYDegree = DEVICE["ROT_Y"]
            rotZDegree = DEVICE["ROT_Z"]

            if "fall_deltaZHeight_" + mac in algoCfg["DATA"]:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight_"+mac]
            else:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight"]

            if "fall_deltaZPos_" + mac in algoCfg["DATA"]:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos_"+mac]
            else:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos"]

            if "fall_bodyWidth_" + mac in algoCfg["DATA"]:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth_"+mac]
            else:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth"]

            if "fall_averageHeight_" + mac in algoCfg["DATA"]:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight_"+mac]
            else:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight"]

            if "fall_minZVel_" + mac in algoCfg["DATA"]:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel_"+mac]
            else:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel"]

            if "fall_numFrames_" + mac in algoCfg["DATA"]:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames_"+mac])
            else:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames"])

            if "vital_periodStationary_" + mac in algoCfg["DATA"]:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary_"+mac]
            else:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary"]

            if "vital_distanceMoved_" + mac in algoCfg["DATA"]:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved_"+mac]
            else:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved"]

            if "vital_xPos_" + mac in algoCfg["DATA"]:
                xPos_threshold = algoCfg["DATA"]["vital_xPos_"+mac]
            else:
                xPos_threshold = algoCfg["DATA"]["vital_xPos"]

            if "vital_zPos_" + mac in algoCfg["DATA"]:
                zPos_threshold = algoCfg["DATA"]["vital_zPos_"+mac]
            else:
                zPos_threshold = algoCfg["DATA"]["vital_zPos"]

            if "aggregatePeriod_" + mac in algoCfg["DATA"]:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod_"+mac]
            else:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod"]

            if radarType == 'wall':
                global wallStateParam

                if mac not in wallStateParam:
                    wallStateParam[mac] = {}
                    wallStateParam[mac]['timeNow'] = 0
                    wallStateParam[mac]['multi_frame_count'] = 2
                    wallStateParam[mac]['label_state'] = ['Moving', 'Upright', 'Laying', 'Fall', 'None', 'Social']

                # Read Radar Setup from Database
                # xShift, yShift, zShift, rotXDegree, rotYDegree, rotZDegree = readRadarSetup(mac)

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                wallStateParam[mac]['radar_coord'] = radar_coord

                # Radar Elevation Angle of Rotation, +ve Anti-Clockwise
                # rotXDegree = DEVICE["ROT_X"]
                elevRadian = rotXDegree * np.pi / 180  # Angle in Radian
                rotXMat = np.asarray([[1, 0, 0], \
                                      [0, np.cos(elevRadian), -np.sin(elevRadian)], \
                                      [0, np.sin(elevRadian), np.cos(elevRadian)]])  # Rotation Matrix
                wallStateParam[mac]['rotXMat'] = rotXMat

                # Radar Rotation about y-axis, +ve Anti-Clockwise
                # rotYDegree = DEVICE["ROT_Y"]
                rotYRadian = rotYDegree * np.pi / 180  # Angle in Radian
                rotYMat = np.asarray([[np.cos(rotYRadian), 0, np.sin(rotYRadian)], [0, 1, 0],
                                      [-np.sin(rotYRadian), 0, np.cos(rotYRadian)]])  # Rotation Matrix
                wallStateParam[mac]['rotYMat'] = rotYMat

                # Radar Azimuth Angle of Rotation, +ve Anti-Clockwise
                # rotZDegree = DEVICE["ROT_Z"]
                azimuthRadian = rotZDegree * np.pi / 180  # Angle in Radian
                rotZMat = np.asarray([[np.cos(azimuthRadian), -np.sin(azimuthRadian), 0], \
                                      [np.sin(azimuthRadian), np.cos(azimuthRadian), 0], \
                                      [0, 0, 1]])  # Rotation Matrix
                wallStateParam[mac]['rotZMat'] = rotZMat

                # Radar Time Stamp
                deltaT = ts - wallStateParam[mac]['timeNow']
                wallStateParam[mac]['timeNow'] = ts

                # Parameters Re-Initialization if Time Interval between Consecutive Data Frames Larger than Certain Threshold
                # For Robust Analytics with Data Frames / Packets Drop

                # print(deltaT)
                if deltaT > 100:
                    wallStateParam[mac]['x0'] = np.nan
                    wallStateParam[mac]['y0'] = np.nan
                    wallStateParam[mac]['z0'] = np.nan
                    wallStateParam[mac]['timeStamp_stationary'] = np.nan
                    wallStateParam[mac]['period_stationary'] = np.nan
                    wallStateParam[mac]['timeStamp_lastSignOfLife'] = np.nan
                    wallStateParam[mac]['period_noSignOfLife'] = np.nan
                    wallStateParam[mac]['x_coord_multi'] = []
                    wallStateParam[mac]['y_coord_multi'] = []
                    wallStateParam[mac]['z_coord_multi'] = []
                    wallStateParam[mac]['rollingX'] = []
                    wallStateParam[mac]['rollingY'] = []
                    wallStateParam[mac]['rollingZ'] = []
                    wallStateParam[mac]['rollingZVel'] = []
                    wallStateParam[mac]['minZVel'] = []
                    wallStateParam[mac]['rollingHeight'] = []
                    wallStateParam[mac]['averageX'] = []
                    wallStateParam[mac]['averageY'] = []
                    wallStateParam[mac]['averageZ'] = []
                    wallStateParam[mac]['averageHeight'] = []
                    wallStateParam[mac]['labelCount'] = []
                    wallStateParam[mac]['labelGuess'] = []
                    wallStateParam[mac]['trackPos'] = np.zeros((0, 3))  # tracker position
                    wallStateParam[mac]['trackVelocity'] = np.zeros((0, 3))  # tracker velocity
                    wallStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    wallStateParam[mac]['previous_pointClouds'] = np.zeros((0, 7))  # previous point clouds
                    wallStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    wallStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp', 'trackIndex', 'numSubjects', 'roomOccupancy',
                                                                            'posX', 'posY', 'posZ', 'velX', 'velY', 'velZ', 'accX', 'accY', 'accZ', 
                                                                            'bodyHeight', 'bodyWidth', 'state', 'kidOrAdult', 'signOfLife', 'pointCloudDetected'])

                # Read parsed data from radar output dictionary
                # Radar Trackers' Data Extraction
                if outputDict is not None:
                  if 'numDetectedTracks' in outputDict:
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()

                    # Decode 3D People Counting Target List TLV
                    # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                    # 3D Struct format
                    # uint32_t     tid;     /*! @brief   tracking ID */
                    # float        posX;    /*! @brief   Detected target X coordinate, in m */
                    # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                    # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                    # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                    # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                    # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                    # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                    # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                    # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                    # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                    # float        g;
                    # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                    trackData = outputDict['trackData']

                    # if numTracks == 1:

                    #     # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                    #     trackId = trackData[0, 0]
                    #     x_pos = trackData[0, 1]
                    #     y_pos = trackData[0, 2]
                    #     z_pos = trackData[0, 3]
                    #     x_vel = trackData[0, 4]
                    #     y_vel = trackData[0, 5]
                    #     z_vel = trackData[0, 6]
                    #     x_acc = trackData[0, 7]
                    #     y_acc = trackData[0, 8]
                    #     z_acc = trackData[0, 9]

                    #     # Tracker polar coordinates
                    #     trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                    #     trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                    #     trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                    #     trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                        # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                        # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                        # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                        # trackerElevationVelocity
                        # print(trackerRange, trackerAzimuth)

                    #     # Rotation of tracker's position and velocity coordinates
                    #     [x_pos, y_pos, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_pos, y_pos, 1])
                    #     [x_vel, y_vel, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_vel, y_vel, 1])
                    #     [x_acc, y_acc, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_acc, y_acc, 1])
                    #     [dum, y_pos, z_pos] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_pos, z_pos])
                    #     [dum, y_vel, z_vel] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_vel, z_vel])
                    #     [dum, y_acc, z_acc] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_acc, z_acc])
                    #     [x_pos, dum, z_pos] = np.matmul(wallStateParam[mac]['rotYMat'], [x_pos, 1, z_pos])
                    #     [x_vel, dum, z_vel] = np.matmul(wallStateParam[mac]['rotYMat'], [x_vel, 1, z_vel])
                    #     [x_acc, dum, z_acc] = np.matmul(wallStateParam[mac]['rotYMat'], [x_acc, 1, z_acc])

                    #     # Horizontal shifting of tracker's position coordinates
                    #     x_pos = x_pos + wallStateParam[mac]['radar_coord'][0]
                    #     y_pos = y_pos + wallStateParam[mac]['radar_coord'][1]
                        # z_pos = z_pos + wallStateParam[mac]['radar_coord'][2]

                        # Tracker velocity (normalized) direction
                        # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                        # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                        # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                    #     wall_Dict['posX'] = x_pos
                    #     wall_Dict['posY'] = y_pos
                    #     wall_Dict['posZ'] = z_pos
                    #     wall_Dict['velX'] = x_vel
                    #     wall_Dict['velY'] = y_vel
                    #     wall_Dict['velZ'] = z_vel
                    #     wall_Dict['accX'] = x_acc
                    #     wall_Dict['accY'] = y_acc
                    #     wall_Dict['accZ'] = z_acc

                    # Read parsed data from radar output dictionary
                    # Radar Point Clouds + Trackers' Data Extraction and Processing
                    if len(wallStateParam[mac]['previous_pointClouds']) >= 0 and 'trackIndexes' in outputDict:
                      trackIndices = outputDict['trackIndexes']

                      if numTracks > 0 and len(wallStateParam[mac]['previous_pointClouds']) >= 0 and \
                        len(wallStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        wallStateParam[mac]['previous_pointClouds'][:,6] = trackIndices
                        snr = wallStateParam[mac]['previous_pointClouds'][:,4]
                        wallStateParam[mac]['previous_pointClouds'] = wallStateParam[mac]['previous_pointClouds'][snr > 7,:]
                        trackIndices = trackIndices[snr > 7]
                        x_coord = wallStateParam[mac]['previous_pointClouds'][:,0]
                        y_coord = wallStateParam[mac]['previous_pointClouds'][:,1]
                        z_coord = wallStateParam[mac]['previous_pointClouds'][:,2]
                        v_coord = wallStateParam[mac]['previous_pointClouds'][:,3]
                        points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Radar Point Clouds Rotation about the Z axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotZMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 0:2] = points_dum[:, 0:2]

                        # Radar Point Clouds Rotation about the X axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotXMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 1:] = points_dum[:, 1:]

                        # Radar Point Clouds Rotation about the Y axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotYMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 0] = points_dum[:, 0]
                        points[:, 2] = points_dum[:, 2]

                        # Shifting of Radar Point Clouds' Coordinates
                        points[:, 0] = points[:, 0] + wallStateParam[mac]['radar_coord'][0]
                        points[:, 1] = points[:, 1] + wallStateParam[mac]['radar_coord'][1]
                        # points[:, 2] = points[:, 2] + wallStateParam[mac]['radar_coord'][2]
                       
                        x_coord = points[:, 0]
                        y_coord = points[:, 1]
                        z_coord = points[:, 2]

                        # Process individual tracker's data for Posture Analytics
                        for trackIdx in range(numTracks):

                            print("number of tracks = ", numTracks)

                            # Time Stamp
                            wall_Dict = {}
                            wall_Dict['timeStamp'] = ts

                            # Point Cloud Detected ?
                            if 'pointCloud' in outputDict:
                              if len(outputDict['pointCloud']) > 0:
                                wall_Dict['pointCloudDetected'] = 1
                              else:
                                wall_Dict['pointCloudDetected'] = 0 

                            # Track Index
                            trackId = trackData[trackIdx, 0]
                            wall_Dict['trackIndex'] = trackId
                            # if np.isnan(trackId):
                            #     continue

                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]
                            x_acc = trackData[trackIdx, 7]
                            y_acc = trackData[trackIdx, 8]
                            z_acc = trackData[trackIdx, 9]

                            # Tracker polar coordinates
                            trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                            trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Rotation of tracker's position and velocity coordinates
                            [x_pos, y_pos, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_pos, y_pos, 1])
                            [x_vel, y_vel, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_vel, y_vel, 1])
                            [x_acc, y_acc, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_acc, y_acc, 1])
                            [dum, y_pos, z_pos] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_pos, z_pos])
                            [dum, y_vel, z_vel] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_vel, z_vel])
                            [dum, y_acc, z_acc] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_acc, z_acc])
                            [x_pos, dum, z_pos] = np.matmul(wallStateParam[mac]['rotYMat'], [x_pos, 1, z_pos])
                            [x_vel, dum, z_vel] = np.matmul(wallStateParam[mac]['rotYMat'], [x_vel, 1, z_vel])
                            [x_acc, dum, z_acc] = np.matmul(wallStateParam[mac]['rotYMat'], [x_acc, 1, z_acc])

                            # Horizontal shifting of tracker's position coordinates
                            x_pos = x_pos + wallStateParam[mac]['radar_coord'][0]
                            y_pos = y_pos + wallStateParam[mac]['radar_coord'][1]
                            # z_pos = z_pos + wallStateParam[mac]['radar_coord'][2]

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos, y_pos, z_pos]], (len(trackPos), 1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # ---------------- Posture Estimation ----------------
                            # ----------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(wallStateParam[mac]['trackPos']) == 0 or np.sum(wallStateParam[mac]['trackIDs'] == trackId) == 0:
                                wallStateParam[mac]['trackIDs'] = np.concatenate((wallStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                wallStateParam[mac]['trackPos'] = np.concatenate((wallStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                wallStateParam[mac]['trackVelocity'] = np.concatenate((wallStateParam[mac]['trackVelocity'], [[x_vel, y_vel, z_vel]]), axis=0)
                                wallStateParam[mac]['trackerInvalid'] = np.concatenate((wallStateParam[mac]['trackerInvalid'], [0]), axis=0)

                                # Append Parameters for positional change detection and dimensional analysis for posture analytics
                                wallStateParam[mac]['rollingX'].append([])
                                wallStateParam[mac]['rollingY'].append([])
                                wallStateParam[mac]['rollingZ'].append([])
                                wallStateParam[mac]['rollingZVel'].append([])
                                wallStateParam[mac]['minZVel'].append([])
                                wallStateParam[mac]['rollingHeight'].append([])
                                wallStateParam[mac]['averageX'].append([])
                                wallStateParam[mac]['averageY'].append([])
                                wallStateParam[mac]['averageZ'].append([])
                                wallStateParam[mac]['averageHeight'].append([])
                                wallStateParam[mac]['x_coord_multi'].append([])
                                wallStateParam[mac]['y_coord_multi'].append([])
                                wallStateParam[mac]['z_coord_multi'].append([])
                                wallStateParam[mac]['labelCount'].append(4)
                                wallStateParam[mac]['labelGuess'].append(4)

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(wallStateParam[mac]['trackIDs']))[wallStateParam[mac]['trackIDs'] == trackId][0]

                                # Update tracker information
                                wallStateParam[mac]['trackerInvalid'][minDistIdx] = wallStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                wallStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                wallStateParam[mac]['trackVelocity'][minDistIdx] = [x_vel, y_vel, z_vel]

                                # Sign Of life
                                if numTracks == 1:
                                    if math.isnan(wallStateParam[mac]['x0']):
                                        wallStateParam[mac]['x0'] = x_pos
                                        wallStateParam[mac]['y0'] = y_pos
                                        wallStateParam[mac]['z0'] = z_pos
                                    else:
                                        distanceMoved = np.abs(wallStateParam[mac]['x0'] - x_pos) + np.abs(wallStateParam[mac]['y0'] - y_pos) + np.abs(wallStateParam[mac]['z0'] - z_pos)
                                        wallStateParam[mac]['x0'] = x_pos
                                        wallStateParam[mac]['y0'] = y_pos
                                        wallStateParam[mac]['z0'] = z_pos
                                        if distanceMoved > 0.1 or math.isnan(wallStateParam[mac]['timeStamp_stationary']):
                                            wallStateParam[mac]['timeStamp_stationary'] = ts
                                        else:
                                            
                                            if len(x_coord[trackIndices == trackId]) > 0 or math.isnan(wallStateParam[mac]['timeStamp_lastSignOfLife']):
                                                wallStateParam[mac]['timeStamp_lastSignOfLife'] = ts
                                            else:
                                                wallStateParam[mac]['period_noSignOfLife'] = ts - wallStateParam[mac]['timeStamp_lastSignOfLife']
                                                wallStateParam[mac]['period_stationary'] = wallStateParam[mac]['timeStamp_lastSignOfLife'] - wallStateParam[mac]['timeStamp_stationary']
                                                if wallStateParam[mac]['period_noSignOfLife'] > 60 and wallStateParam[mac]['period_stationary'] > 60:
                                                    wall_Dict['signOfLife'] = 0
                                                    
                                                    # Publish alert via MQTT communication channel
                                                    # pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":1, "DETAILS":"NOSIGNOFLIFE"}
                                                    # jsonData = json.dumps(pubPayload)
                                                    # mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                                else:
                                                    wall_Dict['signOfLife'] = 1

                                # Multi-Frame Aggregation
                                wallStateParam[mac]['x_coord_multi'][minDistIdx].append(x_coord[trackIndices == trackId])
                                wallStateParam[mac]['y_coord_multi'][minDistIdx].append(y_coord[trackIndices == trackId])
                                wallStateParam[mac]['z_coord_multi'][minDistIdx].append(z_coord[trackIndices == trackId])
                                if len(wallStateParam[mac]['x_coord_multi'][minDistIdx]) > wallStateParam[mac]['multi_frame_count']:
                                    wallStateParam[mac]['x_coord_multi'][minDistIdx].pop(0)
                                    wallStateParam[mac]['y_coord_multi'][minDistIdx].pop(0)
                                    wallStateParam[mac]['z_coord_multi'][minDistIdx].pop(0)

                                # Rolling Average
                                wallStateParam[mac]['rollingX'][minDistIdx].append(x_pos)
                                wallStateParam[mac]['rollingY'][minDistIdx].append(y_pos)
                                wallStateParam[mac]['rollingZ'][minDistIdx].append(z_pos)
                                wallStateParam[mac]['rollingZVel'][minDistIdx].append(z_vel)

                                if len(wallStateParam[mac]['rollingX'][minDistIdx]) >= 10:
                                    wallStateParam[mac]['averageX'][minDistIdx].append(np.average(wallStateParam[mac]['rollingX'][minDistIdx]))
                                    wallStateParam[mac]['averageY'][minDistIdx].append(np.average(wallStateParam[mac]['rollingY'][minDistIdx]))
                                    wallStateParam[mac]['averageZ'][minDistIdx].append(np.average(wallStateParam[mac]['rollingZ'][minDistIdx]))
                                    del wallStateParam[mac]['rollingX'][minDistIdx][0]
                                    del wallStateParam[mac]['rollingY'][minDistIdx][0]
                                    del wallStateParam[mac]['rollingZ'][minDistIdx][0]

                                if len(wallStateParam[mac]['rollingZVel'][minDistIdx]) >= numFrames_threshold:
                                    wallStateParam[mac]['minZVel'][minDistIdx].append(np.percentile(wallStateParam[mac]['rollingZVel'][minDistIdx], 5))
                                    del wallStateParam[mac]['rollingZVel'][minDistIdx][0]
                                    if len(wallStateParam[mac]['minZVel'][minDistIdx]) >= 10:
                                        del wallStateParam[mac]['minZVel'][minDistIdx][0]

                                if len(wallStateParam[mac]['averageX'][minDistIdx]) > numFrames_threshold:
                                    deltaX = wallStateParam[mac]['averageX'][minDistIdx][-1] - wallStateParam[mac]['averageX'][minDistIdx][-10]
                                    deltaY = wallStateParam[mac]['averageY'][minDistIdx][-1] - wallStateParam[mac]['averageY'][minDistIdx][-10]
                                    deltaZ = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-10]
                                    # deltaZPos = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-47]
                                    deltaZPos = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-numFrames_threshold]
                                    del wallStateParam[mac]['averageX'][minDistIdx][0]
                                    del wallStateParam[mac]['averageY'][minDistIdx][0]
                                    del wallStateParam[mac]['averageZ'][minDistIdx][0]

                                    deltaDisp = np.sqrt(deltaX ** 2 + deltaY ** 2 + deltaZ ** 2)
                                    deltaDist = np.sqrt(deltaX ** 2 + deltaY ** 2)

                                    # Disable posture estimation if number of subjects > 1 or subject's range > 5m, or subject's
                                    # azimuth or elevation angle > 50 degrees.
                                    # if numTracks > 1:
                                    #     wallStateParam[mac]['labelCount'][minDistIdx] = 5
                                    #     wallStateParam[mac]['labelGuess'][minDistIdx] = 5
                                    #     wall_Dict['state'] = 5

                                    # if trackerRange > 10 or np.abs(trackerAzimuth) > 50 or np.abs(trackerElevation) > 40:
                                    #     wallStateParam[mac]['labelCount'][minDistIdx] = 4
                                    #     wallStateParam[mac]['labelGuess'][minDistIdx] = 4

                                    # elif len(x_coord[trackIndices == trackId]) > 10:
                                    # elif numTracks == 1:

                                    # elif deltaDisp > 0.05 and len(x_coord[trackIndices == trackId]) > 5:
                                    if len(x_coord[trackIndices == trackId]) > 5:
                                        x_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['x_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        y_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['y_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_height = np.percentile(np.concatenate(wallStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [99])
                                        z_height = z_height + wallStateParam[mac]['radar_coord'][2]
                                        body_width = np.sqrt(x_dim ** 2 + y_dim ** 2)
                                        # print(z_height, z_dim, body_width)
                                        wall_Dict['bodyHeight'] = z_dim[0]
                                        wall_Dict['bodyWidth'] = body_width[0]

                                        wallStateParam[mac]['rollingHeight'][minDistIdx].append(z_height)

                                        if len(wallStateParam[mac]['rollingHeight'][minDistIdx]) == 10:
                                            wallStateParam[mac]['averageHeight'][minDistIdx].append(np.average(wallStateParam[mac]['rollingHeight'][minDistIdx]))
                                            del(wallStateParam[mac]['rollingHeight'][minDistIdx][0])

                                        # if len(wallStateParam[mac]['averageHeight'][minDistIdx]) == 47:
                                        if len(wallStateParam[mac]['averageHeight'][minDistIdx]) == numFrames_threshold:
                                          # deltaHeight = wallStateParam[mac]['averageHeight'][minDistIdx][-1] - wallStateParam[mac]['averageHeight'][minDistIdx][-47]
                                          deltaHeight = wallStateParam[mac]['averageHeight'][minDistIdx][-1] - wallStateParam[mac]['averageHeight'][minDistIdx][-numFrames_threshold]
                                          del(wallStateParam[mac]['averageHeight'][minDistIdx][0])

                                          if deltaHeight < deltaZHeight_threshold and deltaZPos < deltaZPos_threshold and body_width > bodyWidth_threshold and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < averageHeight_threshold and wallStateParam[mac]['minZVel'][minDistIdx][-1] < minZVel_threshold:
                                          # if deltaHeight < -1 and deltaZPos < -1 and body_width > 1 and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < 0.8: # and z_height < 1.0 and ((body_width) / (z_dim + 0.2)) > 1.0:
                                          # if deltaHeight < -0.8 and deltaZPos < -0.8 and body_width > 0.8 and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < 0.8: # and ((body_width) / (wallStateParam[mac]['averageHeight'][minDistIdx][-1])) > 1.5:
                                            # print('Fall')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 3
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            wall_Dict['state'] = 3

                                            # Publish alert via MQTT communication channel
                                            pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":1, "DETAILS":"FALL"}
                                            jsonData = json.dumps(pubPayload)
                                            mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                          elif deltaDist > 0.3:
                                            # print('Moving')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 0
                                            wall_Dict['state'] = 0

                                            # Adult and Kid Differentiation
                                            if z_height > 1.5 and z_height < 2.0 and body_width < 1.0:
                                                wall_Dict['kidOrAdult'] = 1
                                            elif z_height > 0.4 and z_height < 1.0 and body_width < 0.5:
                                                wall_Dict['kidOrAdult'] = 0

                                          elif body_width > 1 and z_height < 1.5 and ((body_width) / (z_dim + 0.2)) > 1.5:
                                            # print('Laying')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 2
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            wall_Dict['state'] = 2

                                          elif z_dim > 0.5 and body_width > 0.3 and z_height > 0.5 and ((z_dim) / (body_width + 0.0001)) > 1.2:
                                            # print('Upright')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 1
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 1
                                            wall_Dict['state'] = 1

                                          else:
                                            wallStateParam[mac]['labelCount'][minDistIdx] = wallStateParam[mac]['labelGuess'][minDistIdx]
                                            # wall_Dict['state'] = wallStateParam[mac]['label_state'][wallStateParam[mac]['labelCount'][minDistIdx]]
                                            wall_Dict['state'] = wallStateParam[mac]['labelCount'][minDistIdx]

                                # ----------------------------------------------------
                                # ----------------------------------------------------

                            # Tracker position, velocity, and acceleration
                            wall_Dict['posX'] = x_pos
                            wall_Dict['posY'] = y_pos
                            wall_Dict['posZ'] = z_pos
                            wall_Dict['velX'] = x_vel
                            wall_Dict['velY'] = y_vel
                            wall_Dict['velZ'] = z_vel
                            wall_Dict['accX'] = x_acc
                            wall_Dict['accY'] = y_acc
                            wall_Dict['accZ'] = z_acc

                            # Room Occupancy Detection
                            wall_Dict['numSubjects'] = numTracks
                            if numTracks > 0:
                                wall_Dict['roomOccupancy'] = True
                            elif numTracks == 0:
                                wall_Dict['roomOccupancy'] = False

                            # Time Series Data Aggregation                
                            if wallStateParam[mac]['pandasDF'].empty:
                                
                                # Append data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                            elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                                # print(wallStateParam[mac]['pandasDF']['trackIndex'].unique())
                                if len(wallStateParam[mac]['pandasDF']['trackIndex'].unique()) > 0:
                                  
                                  for trackInd in wallStateParam[mac]['pandasDF']['trackIndex'].unique():
                                    
                                    if np.isnan(trackInd):
                                        continue

                                    pandasDF_dum = wallStateParam[mac]['pandasDF'].loc[wallStateParam[mac]['pandasDF']['trackIndex'] == trackInd]

                                    aggregate_dict = {}
                                    aggregate_dict['timeStamp'] = round(pandasDF_dum['timeStamp'].mean(skipna=True),2)
                                    aggregate_dict['numSubjects'] = pandasDF_dum['numSubjects'].mean(skipna=True)
                                    aggregate_dict['roomOccupancy'] = pandasDF_dum['roomOccupancy'].mean(skipna=True)
                                    aggregate_dict['trackIndex'] = int(trackInd)
                                    aggregate_dict['posX'] = pandasDF_dum['posX'].mean(skipna=True)
                                    aggregate_dict['posY'] = pandasDF_dum['posY'].mean(skipna=True)
                                    aggregate_dict['posZ'] = pandasDF_dum['posZ'].mean(skipna=True)
                                    aggregate_dict['velX'] = pandasDF_dum['velX'].mean(skipna=True)
                                    aggregate_dict['velY'] = pandasDF_dum['velY'].mean(skipna=True)
                                    aggregate_dict['velZ'] = pandasDF_dum['velZ'].mean(skipna=True)
                                    aggregate_dict['accX'] = pandasDF_dum['accX'].max(skipna=True)
                                    aggregate_dict['accY'] = pandasDF_dum['accY'].max(skipna=True)
                                    aggregate_dict['accZ'] = pandasDF_dum['accZ'].max(skipna=True)
                                    aggregate_dict['bodyHeight'] = pandasDF_dum['bodyHeight'].mean(skipna=True)
                                    aggregate_dict['bodyWidth'] = pandasDF_dum['bodyWidth'].mean(skipna=True)

                                    if not pandasDF_dum['state'].mode(dropna=True).empty:
                                        aggregate_dict['state'] = pandasDF_dum['state'].mode(dropna=True).iloc[0]
                                    else:
                                        aggregate_dict['state'] = np.nan
                                    aggregate_dict['kidOrAdult'] = pandasDF_dum['kidOrAdult'].mean(skipna=True)
                                    aggregate_dict['signOfLife'] = pandasDF_dum['signOfLife'].mean(skipna=True)
                                    aggregate_dict['pointCloudDetected'] = pandasDF_dum['pointCloudDetected'].mean(skipna=True)

                                    # if aggregate_dict['state'].dropna().empty:
                                    # print(aggregate_dict)
                                    if math.isnan(aggregate_dict['state']):
                                        aggregate_dict['state'] = None
                                    elif pandasDF_dum['state'].isin([3]).sum() > 0:
                                        aggregate_dict['state'] = 'Fall'
                                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                                    elif aggregate_dict['state'] != 4:
                                        aggregate_dict['state'] = wallStateParam[mac]['label_state'][int(aggregate_dict['state'])]
                                    else:
                                        aggregate_dict['state'] = None

                                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                                    if math.isnan(aggregate_dict['kidOrAdult']):
                                        aggregate_dict['kidOrAdult'] = None
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                                        aggregate_dict['kidOrAdult'] = 'Kid'
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                                        aggregate_dict['kidOrAdult'] = 'Adult'

                                    # aggregate_dict = aggregate_dict.to_dict('r')
                                    # if aggregate_dict:
                                    # print("YYYYYYYYY")
                                    # aggregate_dict = aggregate_dict[0]
                                    if not math.isnan(aggregate_dict['numSubjects']):
                                        aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                                    if not math.isnan(aggregate_dict['roomOccupancy']):
                                        aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                                    if not math.isnan(aggregate_dict['signOfLife']):
                                      # aggregate_dict['signOfLife'] = bool(round(aggregate_dict['signOfLife']))
                                      if aggregate_dict['signOfLife'] > 0:
                                        aggregate_dict['signOfLife'] = 1
                                      elif aggregate_dict['signOfLife'] == 0:
                                        aggregate_dict['signOfLife'] = 0
                                    if not math.isnan(aggregate_dict['pointCloudDetected']):
                                      if aggregate_dict['pointCloudDetected'] > 0:
                                        aggregate_dict['pointCloudDetected'] = 1
                                      elif aggregate_dict['pointCloudDetected'] == 0:
                                        aggregate_dict['pointCloudDetected'] = 0

                                    for key, value in aggregate_dict.items():
                                        if str(value)[0:3] == 'nan':
                                            aggregate_dict[key] = None

                                    # print(aggregate_dict['state'])
                                    dict_copy = copy.deepcopy(aggregate_dict)
                                    my_list.append(dict_copy)
                                    # print(json_string)

                                # Update the new data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                                wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                            else:
            
                                # Append data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                                # print(wallStateParam)

                        # Remove unused trackers' information and parameters
                        trackerInvalidIdx = np.arange(len(wallStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[wallStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            wallStateParam[mac]['x_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['y_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['z_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingX'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingY'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingZ'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingZVel'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['minZVel'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingHeight'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageX'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageY'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageZ'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageHeight'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['labelCount'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['labelGuess'].pop(trackerInvalidIdx[Idx])

                        wallStateParam[mac]['trackPos'] = wallStateParam[mac]['trackPos'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackVelocity'] = wallStateParam[mac]['trackVelocity'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackIDs'] = wallStateParam[mac]['trackIDs'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackerInvalid'] = wallStateParam[mac]['trackerInvalid'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackerInvalid'] = wallStateParam[mac]['trackerInvalid'] + 1

                  else:
                    
                    wall_Dict = {}
                    wall_Dict['timeStamp'] = ts

                    # Point Cloud Detected ?
                    if 'pointCloud' in outputDict:
                      if len(outputDict['pointCloud']) > 0:
                        wall_Dict['pointCloudDetected'] = 1
                      else:
                        wall_Dict['pointCloudDetected'] = 0                    

                    # Time Series Data Aggregation 
                    if "pandasDF" in wallStateParam[mac]:
                        if wallStateParam[mac]['pandasDF'].empty:
                            # Append data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                        elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                            aggregate_dict = {}
                            aggregate_dict['timeStamp'] = round(wallStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                            aggregate_dict['numSubjects'] = 0
                            aggregate_dict['roomOccupancy'] = False
                            aggregate_dict['trackIndex'] = None
                            aggregate_dict['posX'] = None
                            aggregate_dict['posY'] = None
                            aggregate_dict['posZ'] = None
                            aggregate_dict['velX'] = None
                            aggregate_dict['velY'] = None
                            aggregate_dict['velZ'] = None
                            aggregate_dict['accX'] = None
                            aggregate_dict['accY'] = None
                            aggregate_dict['accZ'] = None
                            aggregate_dict['bodyHeight'] = None
                            aggregate_dict['bodyWidth'] = None
                            aggregate_dict['state'] = None
                            aggregate_dict['kidOrAdult'] = None
                            aggregate_dict['signOfLife'] = None
                            aggregate_dict['pointCloudDetected'] = wallStateParam[mac]['pandasDF']['pointCloudDetected'].mean(skipna=True)

                            if not math.isnan(aggregate_dict['pointCloudDetected']):
                              if aggregate_dict['pointCloudDetected'] > 0:
                                aggregate_dict['pointCloudDetected'] = 1
                              elif aggregate_dict['pointCloudDetected'] == 0:
                                aggregate_dict['pointCloudDetected'] = 0
                            else:
                              aggregate_dict['pointCloudDetected'] = None

                            # print(aggregate_dict['state'])
                            dict_copy = copy.deepcopy(aggregate_dict)
                            my_list.append(dict_copy)
                            # print(json_string)

                            # Update the new data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                            wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                        else:
                            # Append data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                     

                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    wallStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']

                # Time Series Data Aggregation 
                # if "pandasDF" in wallStateParam[mac]:
                #     if wallStateParam[mac]['pandasDF'].empty:
                #         # Append data frame
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                #     elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                #         aggregate_dict = {}
                #         aggregate_dict['timeStamp'] = round(wallStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                #         aggregate_dict['numSubjects'] = wallStateParam[mac]['pandasDF']['numSubjects'].mean(skipna=True)
                #         aggregate_dict['roomOccupancy'] = wallStateParam[mac]['pandasDF']['roomOccupancy'].mean(skipna=True)
                #         aggregate_dict['posX'] = wallStateParam[mac]['pandasDF']['posX'].mean(skipna=True)
                #         aggregate_dict['posY'] = wallStateParam[mac]['pandasDF']['posY'].mean(skipna=True)
                #         aggregate_dict['posZ'] = wallStateParam[mac]['pandasDF']['posZ'].mean(skipna=True)
                #         aggregate_dict['velX'] = wallStateParam[mac]['pandasDF']['velX'].mean(skipna=True)
                #         aggregate_dict['velY'] = wallStateParam[mac]['pandasDF']['velY'].mean(skipna=True)
                #         aggregate_dict['velZ'] = wallStateParam[mac]['pandasDF']['velZ'].mean(skipna=True)
                #         aggregate_dict['accX'] = wallStateParam[mac]['pandasDF']['accX'].max(skipna=True)
                #         aggregate_dict['accY'] = wallStateParam[mac]['pandasDF']['accY'].max(skipna=True)
                #         aggregate_dict['accZ'] = wallStateParam[mac]['pandasDF']['accZ'].max(skipna=True)
                #         if not wallStateParam[mac]['pandasDF']['state'].mode(dropna=True).empty:
                #             aggregate_dict['state'] = wallStateParam[mac]['pandasDF']['state'].mode(dropna=True).iloc[0]
                #         else:
                #             aggregate_dict['state'] = np.nan
                #         aggregate_dict['kidOrAdult'] = wallStateParam[mac]['pandasDF']['kidOrAdult'].mean(skipna=True)
 
                #         # if aggregate_dict['state'].dropna().empty:
                #         # print(aggregate_dict)
                #         if math.isnan(aggregate_dict['state']):
                #             aggregate_dict['state'] = None
                #         elif wallStateParam[mac]['pandasDF']['state'].isin([3]).sum() > 0:
                #             aggregate_dict['state'] = 'Fall'
                #         # elif aggregate_dict['state'].isin([4]).sum() == 0:
                #         elif aggregate_dict['state'] != 4:
                #             aggregate_dict['state'] = wallStateParam[mac]['label_state'][
                #                 int(aggregate_dict['state'])]
                #         else:
                #             aggregate_dict['state'] = None

                #         # if aggregate_dict['kidOrAdult'].dropna().empty:
                #         if math.isnan(aggregate_dict['kidOrAdult']):
                #             aggregate_dict['kidOrAdult'] = None
                #         # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                #         elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                #             aggregate_dict['kidOrAdult'] = 'Kid'
                #         # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                #         elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                #             aggregate_dict['kidOrAdult'] = 'Adult'

                #         # aggregate_dict = aggregate_dict.to_dict('r')
                #         # if aggregate_dict:
                #             # print("YYYYYYYYY")
                #             # aggregate_dict = aggregate_dict[0]
                #         if not math.isnan(aggregate_dict['numSubjects']):
                #             aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                #         if not math.isnan(aggregate_dict['roomOccupancy']):
                #             aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                #         for key, value in aggregate_dict.items():
                #             if str(value)[0:3] == 'nan':
                #                 aggregate_dict[key] = None

                #         # print(aggregate_dict['state'])
                #         dict_copy = copy.deepcopy(aggregate_dict)
                #         my_list.append(dict_copy)
                #         # print(json_string)

                #         # Update the new data frame
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                #     else:
                #         # Append data frame
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                # print(wallStateParam)
    
            # --------------------------------- Ceil-Mounted Radar Tracking and Posture Analysis -------------------------------
            # ------------------------------------------------------------------------------------------------------------------

            elif radarType == 'ceil':

                global ceilStateParam

                if mac not in ceilStateParam:
                    ceilStateParam[mac] = {}
                    ceilStateParam[mac]['timeNow'] = 0
                    ceilStateParam[mac]['multi_frame_count'] = 1
                    ceilStateParam[mac]['label_state'] = ['Moving', 'Upright', 'Laying', 'Fall', 'None', 'Social']

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                ceilStateParam[mac]['radar_coord'] = radar_coord

                # Radar Rotation about y-axis, +ve Anti-Clockwise
                rotYRadian = rotYDegree * np.pi / 180  # Angle in Radian
                rotYMat = np.asarray([[np.cos(rotYRadian), 0, np.sin(rotYRadian)], [0, 1, 0],
                                      [-np.sin(rotYRadian), 0, np.cos(rotYRadian)]])  # Rotation Matrix
                ceilStateParam[mac]['rotYMat'] = rotYMat

                deltaT = ts - ceilStateParam[mac]['timeNow']
                ceilStateParam[mac]['timeNow'] = ts

                # Time-Interval Thresholding for Robust Analytics with Data Packets Drop
                if deltaT > 5:
                    # Parameters Re-Initialization
                    ceilStateParam[mac]['x_coord_multi'] = []
                    ceilStateParam[mac]['y_coord_multi'] = []
                    ceilStateParam[mac]['z_coord_multi'] = []
                    ceilStateParam[mac]['rollingX'] = []
                    ceilStateParam[mac]['rollingY'] = []
                    ceilStateParam[mac]['rollingZ'] = []
                    ceilStateParam[mac]['averageX'] = []
                    ceilStateParam[mac]['averageY'] = []
                    ceilStateParam[mac]['averageZ'] = []
                    ceilStateParam[mac]['labelCount'] = []
                    ceilStateParam[mac]['labelGuess'] = []
                    ceilStateParam[mac]['trackPos'] = np.zeros((0, 3))  # tracker position
                    ceilStateParam[mac]['trackVelocity'] = np.zeros((0, 3))  # tracker velocity
                    ceilStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    ceilStateParam[mac]['previous_pointClouds'] = np.zeros((0, 7))  # previous point clouds
                    ceilStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    ceilStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp', 'trackIndex', 'numSubjects', 'roomOccupancy',
                                                                            'posX', 'posY', 'posZ', 'velX', 'velY', 'velZ', 'accX', 'accY', 'accZ', 
                                                                            'bodyHeight', 'bodyWidth', 'state', 'kidOrAdult'])

                # print(outputDict)
                if outputDict is not None:
                  if "numDetectedTracks" in outputDict:
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()

                    # Decode 3D People Counting Target List TLV
                    # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                    # 3D Struct format
                    # uint32_t     tid;     /*! @brief   tracking ID */
                    # float        posX;    /*! @brief   Detected target X coordinate, in m */
                    # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                    # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                    # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                    # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                    # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                    # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                    # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                    # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                    # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                    # float        g;
                    # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                    trackData = outputDict['trackData']
                    # trackHeight = outputDict['trackHeight']

                    # if numTracks == 1:

                        # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                    #     trackId = trackData[0, 0]
                    #     x_pos = trackData[0, 1]
                    #     y_pos = trackData[0, 2]
                    #     z_pos = trackData[0, 3]
                    #     x_vel = trackData[0, 4]
                    #     y_vel = trackData[0, 5]
                    #     z_vel = trackData[0, 6]
                    #     x_acc = trackData[0, 7]
                    #     y_acc = trackData[0, 8]
                    #     z_acc = trackData[0, 9]

                        # Tracker polar coordinates
                    #     trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                    #     trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                    #     trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                    #     trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                        # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                        # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                        # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                        # trackerElevationVelocity
                        # print(trackerRange, trackerAzimuth)

                        # Tracker coordinates and velocity vector transformation
                    #     [x_pos, dum, z_pos] = np.matmul(rotYMat, [x_pos, 1, z_pos])
                    #     [x_vel, dum, z_vel] = np.matmul(rotYMat, [x_vel, 1, z_vel])
                    #     [x_acc, dum, z_acc] = np.matmul(rotYMat, [x_acc, 1, z_acc])
                    #     x_pos = x_pos + ceilStateParam[mac]['radar_coord'][0]
                    #     z_pos = z_pos + ceilStateParam[mac]['radar_coord'][1]

                        # Tracker velocity (normalized) direction
                        # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                        # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                        # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                    #     ceil_Dict['posX'] = x_pos
                    #     ceil_Dict['posY'] = z_pos
                    #     ceil_Dict['posZ'] = -y_pos
                    #     ceil_Dict['velX'] = x_vel
                    #     ceil_Dict['velY'] = z_vel
                    #     ceil_Dict['velZ'] = -y_vel
                    #     ceil_Dict['accX'] = x_acc
                    #     ceil_Dict['accY'] = z_acc
                    #     ceil_Dict['accZ'] = -y_acc

                    # if dataOk and len(detObj["x"]) > 1:
                    if len(ceilStateParam[mac]['previous_pointClouds']) > 0 and "trackIndexes" in outputDict:
                      trackIndices = outputDict['trackIndexes']

                      if numTracks > 0 and len(ceilStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(ceilStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        ceilStateParam[mac]['previous_pointClouds'][:, 6] = trackIndices
                        snr = ceilStateParam[mac]['previous_pointClouds'][:, 4]
                        ceilStateParam[mac]['previous_pointClouds'] = ceilStateParam[mac]['previous_pointClouds'][snr > 7, :]
                        trackIndices = trackIndices[snr > 7]
                        # colorMap_pointClouds = np.zeros((len(trackIndices),3)) + 0.8
                        x_coord = ceilStateParam[mac]['previous_pointClouds'][:, 0]
                        y_coord = ceilStateParam[mac]['previous_pointClouds'][:, 1]
                        z_coord = ceilStateParam[mac]['previous_pointClouds'][:, 2]
                        v_coord = ceilStateParam[mac]['previous_pointClouds'][:, 3]
                        points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Geometric Transformation
                        points = np.matmul(rotYMat, np.transpose(points))
                        points = np.transpose(points)
                        points[:, 0] = points[:, 0] + ceilStateParam[mac]['radar_coord'][0]
                        points[:, 2] = points[:, 2] + ceilStateParam[mac]['radar_coord'][2]

                        x_coord = points[:, 0]
                        y_coord = points[:, 1]
                        z_coord = points[:, 2]

                        # Read and draw trackers' information
                        for trackIdx in range(numTracks):

                            # Time Stamp
                            ceil_Dict = {}
                            ceil_Dict['timeStamp'] = ts

                            # Track Index
                            trackId = trackData[trackIdx, 0]
                            ceil_Dict['trackIndex'] = trackId

                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]
                            x_acc = trackData[trackIdx, 7]
                            y_acc = trackData[trackIdx, 8]
                            z_acc = trackData[trackIdx, 9]

                            # Tracker polar coordinates
                            trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                            trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Tracker coordinates and velocity vector transformation
                            [x_pos, dum, z_pos] = np.matmul(rotYMat, [x_pos, 1, z_pos])
                            [x_vel, dum, z_vel] = np.matmul(rotYMat, [x_vel, 1, z_vel])
                            x_pos = x_pos + ceilStateParam[mac]['radar_coord'][0]
                            z_pos = z_pos + ceilStateParam[mac]['radar_coord'][2]

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos, y_pos, z_pos]], (len(trackPos), 1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # -------------------------------- Posture Estimation ----------------------------------------------
                            # --------------------------------------------------------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(ceilStateParam[mac]['trackPos']) == 0 or np.sum(ceilStateParam[mac]['trackIDs'] == trackId) == 0:
                                # trackPos = np.concatenate((trackPos, [[x_pos,y_pos,z_pos]]), axis=0)
                                ceilStateParam[mac]['trackIDs'] = np.concatenate((ceilStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                ceilStateParam[mac]['trackPos'] = np.concatenate((ceilStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                ceilStateParam[mac]['trackVelocity'] = np.concatenate((ceilStateParam[mac]['trackVelocity'], [[x_vel, y_vel, z_vel]]), axis=0)
                                ceilStateParam[mac]['trackerInvalid'] = np.concatenate((ceilStateParam[mac]['trackerInvalid'], [0]), axis=0)

                                # Append Parameters for positional change detection and dimensional analysis
                                ceilStateParam[mac]['rollingX'].append([])
                                ceilStateParam[mac]['rollingY'].append([])
                                ceilStateParam[mac]['rollingZ'].append([])
                                ceilStateParam[mac]['averageX'].append([])
                                ceilStateParam[mac]['averageY'].append([])
                                ceilStateParam[mac]['averageZ'].append([])
                                ceilStateParam[mac]['x_coord_multi'].append([])
                                ceilStateParam[mac]['y_coord_multi'].append([])
                                ceilStateParam[mac]['z_coord_multi'].append([])
                                ceilStateParam[mac]['labelCount'].append(4)
                                ceilStateParam[mac]['labelGuess'].append(4)

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(ceilStateParam[mac]['trackIDs']))[ceilStateParam[mac]['trackIDs'] == trackId][0]

                                # Update tracker information
                                ceilStateParam[mac]['trackerInvalid'][minDistIdx] = ceilStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                ceilStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                ceilStateParam[mac]['trackVelocity'][minDistIdx] = [x_vel, y_vel, z_vel]

                                # Multi-Frame Aggregation
                                ceilStateParam[mac]['x_coord_multi'][minDistIdx].append(x_coord[trackIndices == trackId])
                                ceilStateParam[mac]['y_coord_multi'][minDistIdx].append(y_coord[trackIndices == trackId])
                                ceilStateParam[mac]['z_coord_multi'][minDistIdx].append(z_coord[trackIndices == trackId])
                                if len(ceilStateParam[mac]['x_coord_multi'][minDistIdx]) > ceilStateParam[mac]['multi_frame_count']:
                                    ceilStateParam[mac]['x_coord_multi'][minDistIdx].pop(0)
                                    ceilStateParam[mac]['y_coord_multi'][minDistIdx].pop(0)
                                    ceilStateParam[mac]['z_coord_multi'][minDistIdx].pop(0)

                                # Rolling Average
                                ceilStateParam[mac]['rollingX'][minDistIdx].append(x_pos)
                                ceilStateParam[mac]['rollingY'][minDistIdx].append(y_pos)
                                ceilStateParam[mac]['rollingZ'][minDistIdx].append(z_pos)

                                if len(ceilStateParam[mac]['rollingX'][minDistIdx]) >= 5:
                                    ceilStateParam[mac]['averageX'][minDistIdx].append(np.average(ceilStateParam[mac]['rollingX'][minDistIdx]))
                                    ceilStateParam[mac]['averageY'][minDistIdx].append(np.average(ceilStateParam[mac]['rollingY'][minDistIdx]))
                                    ceilStateParam[mac]['averageZ'][minDistIdx].append(np.average(ceilStateParam[mac]['rollingZ'][minDistIdx]))
                                    del ceilStateParam[mac]['rollingX'][minDistIdx][0]
                                    del ceilStateParam[mac]['rollingY'][minDistIdx][0]
                                    del ceilStateParam[mac]['rollingZ'][minDistIdx][0]

                                if len(ceilStateParam[mac]['averageX'][minDistIdx]) > 10:
                                    deltaX = ceilStateParam[mac]['averageX'][minDistIdx][-1] - ceilStateParam[mac]['averageX'][minDistIdx][-5]
                                    deltaY = ceilStateParam[mac]['averageY'][minDistIdx][-1] - ceilStateParam[mac]['averageY'][minDistIdx][-5]
                                    deltaZ = ceilStateParam[mac]['averageZ'][minDistIdx][-1] - ceilStateParam[mac]['averageZ'][minDistIdx][-5]
                                    del ceilStateParam[mac]['averageX'][minDistIdx][0]
                                    del ceilStateParam[mac]['averageY'][minDistIdx][0]
                                    del ceilStateParam[mac]['averageZ'][minDistIdx][0]

                                    deltaDisp = np.sqrt(deltaX ** 2 + deltaY ** 2 + deltaZ ** 2)
                                    deltaDist = np.sqrt(deltaX ** 2 + deltaZ ** 2)

                                    # Disable posture estimation if number of subjects > 1 or subject's range > 5m, or subject's
                                    # azimuth or elevation angle > 50 degrees.
                                    # if numTracks > 1:
                                    #     ceilStateParam[mac]['labelCount'][minDistIdx] = 5
                                    #     ceilStateParam[mac]['labelGuess'][minDistIdx] = 5
                                    #     ceil_Dict['state'] = 5

                                    if trackerRange > 5 or np.abs(trackerAzimuth) > 50 or np.abs(trackerElevation) > 40:
                                        ceilStateParam[mac]['labelCount'][minDistIdx] = 4
                                        ceilStateParam[mac]['labelGuess'][minDistIdx] = 4

                                    # elif len(x_coord[trackIndices == trackId]) > 10:
                                    # elif numTracks == 1:

                                    # elif deltaDisp > 0.1 and len(x_coord[trackIndices == trackId]) > 10:
                                    elif len(x_coord[trackIndices == trackId]) > 10:

                                        x_dim = np.diff(np.percentile(np.concatenate(ceilStateParam[mac]['x_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        y_dim = np.diff(np.percentile(np.concatenate(ceilStateParam[mac]['y_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_dim = np.diff(np.percentile(np.concatenate(ceilStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        y_height = np.percentile(np.concatenate(ceilStateParam[mac]['y_coord_multi'][minDistIdx][:], axis=0), [1])
                                        y_height = ceilStateParam[mac]['radar_coord'][2] - y_height
                                        body_width = np.sqrt(x_dim ** 2 + z_dim ** 2)
                                        # print(y_height, y_dim, body_width)
                                        ceil_Dict['bodyHeight'] = y_height[0]
                                        ceil_Dict['bodyWidth'] = body_width[0]

                                        if deltaY > 0.35 and body_width > 0.5 and y_height < 1.0 and ((body_width) / (y_height + 0.2)) > 1.0:
                                            # print("Fall")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 3
                                            ceilStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            ceil_Dict['state'] = 3

                                            # Publish alert via MQTT communication channel
                                            pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":2, "DETAILS":"FALL"}
                                            jsonData = json.dumps(pubPayload)
                                            mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                        elif deltaDist > 0.3:
                                            # print("Moving")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 0
                                            ceil_Dict['state'] = 0

                                            # Adult and Kid Differentiation
                                            if y_height > 1.5 and y_height < 2.0 and body_width < 1.0:
                                                ceil_Dict['kidOrAdult'] = 1

                                            elif y_height > 0.4 and y_height < 1.0 and body_width < 0.5:
                                                ceil_Dict['kidOrAdult'] = 0

                                        elif body_width > 0.5 and y_height < 1.1 and ((body_width) / (y_height + 0.2)) > 1.8:
                                            # print("Laying")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 2
                                            ceilStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            ceil_Dict['state'] = 2

                                        elif body_width > 0.2 and y_height > 0.5 and ((y_height) / (body_width + 0.0001)) > 1.2:
                                            # print("Upright")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 1
                                            ceilStateParam[mac]['labelGuess'][minDistIdx] = 1
                                            ceil_Dict['state'] = 1

                                        else:
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = ceilStateParam[mac]['labelGuess'][minDistIdx]
                                            # ceil_Dict['state'] = ceilStateParam[mac]['label_state'][ceilStateParam[mac]['labelCount'][minDistIdx]]
                                            ceil_Dict['state'] = ceilStateParam[mac]['labelCount'][minDistIdx]

                                # ----------------------------------------------------------------------------------------------
                                # ----------------------------------------------------------------------------------------------

                            # Tracker position, velocity, and acceleration
                            ceil_Dict['posX'] = x_pos
                            ceil_Dict['posY'] = z_pos
                            ceil_Dict['posZ'] = -y_pos
                            ceil_Dict['velX'] = x_vel
                            ceil_Dict['velY'] = z_vel
                            ceil_Dict['velZ'] = -y_vel
                            ceil_Dict['accX'] = x_acc
                            ceil_Dict['accY'] = z_acc
                            ceil_Dict['accZ'] = -y_acc

                            # Room Occupancy Detection
                            ceil_Dict['numSubjects'] = numTracks
                            if numTracks > 0:
                                ceil_Dict['roomOccupancy'] = True
                            elif numTracks == 0:
                                ceil_Dict['roomOccupancy'] = False

                            # Time Series Data Aggregation
                            if ceilStateParam[mac]['pandasDF'].empty:
                                
                                # Append data frame
                                ceilStateParam[mac]['pandasDF'] = pd.concat(ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict]), ignore_index=True)

                            elif (ceil_Dict['timeStamp'] - ceilStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                                if len(ceilStateParam[mac]['pandasDF']['trackIndex'].unique()) > 0:
                                  
                                  for trackInd in ceilStateParam[mac]['pandasDF']['trackIndex'].unique():
                                    
                                    if np.isnan(trackInd):
                                        continue

                                    pandasDF_dum = ceilStateParam[mac]['pandasDF'].loc[ceilStateParam[mac]['pandasDF']['trackIndex'] == trackInd]

                                    aggregate_dict = {}
                                    aggregate_dict['timeStamp'] = round(pandasDF_dum['timeStamp'].mean(skipna=True),2)
                                    aggregate_dict['numSubjects'] = pandasDF_dum['numSubjects'].mean(skipna=True)
                                    aggregate_dict['roomOccupancy'] = pandasDF_dum['roomOccupancy'].mean(skipna=True)
                                    aggregate_dict['trackIndex'] = int(trackInd)
                                    aggregate_dict['posX'] = pandasDF_dum['posX'].mean(skipna=True)
                                    aggregate_dict['posY'] = pandasDF_dum['posY'].mean(skipna=True)
                                    aggregate_dict['posZ'] = pandasDF_dum['posZ'].mean(skipna=True)
                                    aggregate_dict['velX'] = pandasDF_dum['velX'].mean(skipna=True)
                                    aggregate_dict['velY'] = pandasDF_dum['velY'].mean(skipna=True)
                                    aggregate_dict['velZ'] = pandasDF_dum['velZ'].mean(skipna=True)
                                    aggregate_dict['accX'] = pandasDF_dum['accX'].max(skipna=True)
                                    aggregate_dict['accY'] = pandasDF_dum['accY'].max(skipna=True)
                                    aggregate_dict['accZ'] = pandasDF_dum['accZ'].max(skipna=True)
                                    aggregate_dict['bodyHeight'] = pandasDF_dum['bodyHeight'].mean(skipna=True)
                                    aggregate_dict['bodyWidth'] = pandasDF_dum['bodyWidth'].mean(skipna=True)

                                    if not pandasDF_dum['state'].mode(dropna=True).empty:
                                        aggregate_dict['state'] = pandasDF_dum['state'].mode(dropna=True).iloc[0]
                                    else:
                                        aggregate_dict['state'] = np.nan
                                    aggregate_dict['kidOrAdult'] = pandasDF_dum['kidOrAdult'].mean(skipna=True)

                                    # if aggregate_dict['state'].dropna().empty:
                                    # print(aggregate_dict)
                                    if math.isnan(aggregate_dict['state']):
                                        aggregate_dict['state'] = None
                                    elif pandasDF_dum['state'].isin([3]).sum() > 0:
                                        aggregate_dict['state'] = 'Fall'
                                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                                    elif aggregate_dict['state'] != 4:
                                        aggregate_dict['state'] = ceilStateParam[mac]['label_state'][int(aggregate_dict['state'])]
                                    else:
                                        aggregate_dict['state'] = None

                                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                                    if math.isnan(aggregate_dict['kidOrAdult']):
                                        aggregate_dict['kidOrAdult'] = None
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                                        aggregate_dict['kidOrAdult'] = 'Kid'
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                                        aggregate_dict['kidOrAdult'] = 'Adult'

                                    # aggregate_dict = aggregate_dict.to_dict('r')
                                    # if aggregate_dict:
                                    # print("YYYYYYYYY")
                                    # aggregate_dict = aggregate_dict[0]
                                    if not math.isnan(aggregate_dict['numSubjects']):
                                        aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                                    if not math.isnan(aggregate_dict['roomOccupancy']):
                                        aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                                    for key, value in aggregate_dict.items():
                                        if str(value)[0:3] == 'nan':
                                            aggregate_dict[key] = None

                                    print(aggregate_dict['state'])
                                    dict_copy = copy.deepcopy(aggregate_dict)
                                    my_list.append(dict_copy)
                                    # print(json_string)

                                # Update the new data frame
                                ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)
                                ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].iloc[-1:,:]

                            else:
                    
                                # Append data frame
                                ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)


                        # Remove unused tracker information and parameters
                        trackerInvalidIdx = np.arange(len(ceilStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[ceilStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            ceilStateParam[mac]['x_coord_multi'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['y_coord_multi'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['z_coord_multi'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['rollingX'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['rollingY'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['rollingZ'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['averageX'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['averageY'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['averageZ'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['labelCount'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['labelGuess'].pop(trackerInvalidIdx[Idx])

                        ceilStateParam[mac]['trackPos'] = ceilStateParam[mac]['trackPos'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackVelocity'] = ceilStateParam[mac]['trackVelocity'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackIDs'] = ceilStateParam[mac]['trackIDs'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackerInvalid'] = ceilStateParam[mac]['trackerInvalid'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackerInvalid'] = ceilStateParam[mac]['trackerInvalid'] + 1

                  else:
                    
                    ceil_Dict = {}
                    ceil_Dict['timeStamp'] = ts
                    
                    # Time Series Data Aggregation 
                    if "pandasDF" in ceilStateParam[mac]:
                        if ceilStateParam[mac]['pandasDF'].empty:
                            # Append data frame
                            ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)

                        elif (ceil_Dict['timeStamp'] - ceilStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                            aggregate_dict = {}
                            aggregate_dict['timeStamp'] = round(ceilStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                            aggregate_dict['numSubjects'] = 0
                            aggregate_dict['roomOccupancy'] = False
                            aggregate_dict['trackIndex'] = None
                            aggregate_dict['posX'] = None
                            aggregate_dict['posY'] = None
                            aggregate_dict['posZ'] = None
                            aggregate_dict['velX'] = None
                            aggregate_dict['velY'] = None
                            aggregate_dict['velZ'] = None
                            aggregate_dict['accX'] = None
                            aggregate_dict['accY'] = None
                            aggregate_dict['accZ'] = None
                            aggregate_dict['bodyHeight'] = None
                            aggregate_dict['bodyWidth'] = None
                            aggregate_dict['state'] = None
                            aggregate_dict['kidOrAdult'] = None

                            # print(aggregate_dict['state'])
                            dict_copy = copy.deepcopy(aggregate_dict)
                            my_list.append(dict_copy)
                            # print(json_string)

                            # Update the new data frame
                            ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)
                            ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].iloc[-1:,:]

                        else:
                            # Append data frame
                            ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)


                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    ceilStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']

                # Time Series Data Aggregation
                # if ceilStateParam[mac]['pandasDF'].empty:
                    # Append data frame
                #     ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].append(ceil_Dict, ignore_index=True)

                # elif (ceil_Dict['timeStamp'] - ceilStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:
                    # aggregate_dict = ceilStateParam[mac]['pandasDF'].agg({'timeStamp':'mean',
                    #                                                'numSubjects': 'mean',
                    #                                                'roomOccupancy': 'mean',
                    #                                                'posX':'mean', 'posY':'mean', 'posZ':'mean',
                    #                                                'velX':'mean', 'velY':'mean', 'velZ':'mean',
                    #                                                'accX':'max', 'accY':'max', 'accZ':'max',
                    #                                                'state': lambda x: pd.Series.mode(x, dropna=True),
                    #                                                'kidOrAdult': 'mean'})

                    # if aggregate_dict['state'].dropna().empty:
                    #     aggregate_dict['state'] = None
                    # elif ceilStateParam[mac]['pandasDF']['state'].isin([3]).sum() > 0:
                    #     aggregate_dict['state'] = 'Fall'
                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                    #     aggregate_dict['state'] = ceilStateParam[mac]['label_state'][int(aggregate_dict['state'].iloc[0])]
                    # else:
                    #     aggregate_dict['state'] = None

                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                    #     aggregate_dict['kidOrAdult'] = None
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                    #     aggregate_dict['kidOrAdult'] = 'Kid'
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                    #     aggregate_dict['kidOrAdult'] = 'Adult'

                    # aggregate_dict = aggregate_dict.to_dict('r')
                    # if aggregate_dict:
                    #     aggregate_dict = aggregate_dict[0]
                    #     for key, value in aggregate_dict.items():
                    #         if str(value)[0:3] == 'nan':
                    #             aggregate_dict[key] = None
                    #     # aggregate_dict['timeStamp'] = str(dt.fromtimestamp(float(aggregate_dict['timeStamp']), tz))[:23]
                    #     aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                    #     aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                    #     # json_string = json.dumps(aggregate_dict, indent=4)
                        
                    # else:
                    #     aggregate_dict = {}
                    #     aggregate_dict['timeStamp'] = ceilStateParam[mac]['pandasDF']['timeStamp'].agg('mean')
                    #     aggregate_dict['numSubjects'] = 0
                    #     aggregate_dict['roomOccupancy'] = False

                    # aggregate_dict = {}
                    # aggregate_dict['timeStamp'] = round(ceilStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                    # aggregate_dict['numSubjects'] = ceilStateParam[mac]['pandasDF']['numSubjects'].mean(skipna=True)
                    # aggregate_dict['roomOccupancy'] = ceilStateParam[mac]['pandasDF']['roomOccupancy'].mean(skipna=True)
                    # aggregate_dict['posX'] = ceilStateParam[mac]['pandasDF']['posX'].mean(skipna=True)
                    # aggregate_dict['posY'] = ceilStateParam[mac]['pandasDF']['posY'].mean(skipna=True)
                    # aggregate_dict['posZ'] = ceilStateParam[mac]['pandasDF']['posZ'].mean(skipna=True)
                    # aggregate_dict['velX'] = ceilStateParam[mac]['pandasDF']['velX'].mean(skipna=True)
                    # aggregate_dict['velY'] = ceilStateParam[mac]['pandasDF']['velY'].mean(skipna=True)
                    # aggregate_dict['velZ'] = ceilStateParam[mac]['pandasDF']['velZ'].mean(skipna=True)
                    # aggregate_dict['accX'] = ceilStateParam[mac]['pandasDF']['accX'].max(skipna=True)
                    # aggregate_dict['accY'] = ceilStateParam[mac]['pandasDF']['accY'].max(skipna=True)
                    # aggregate_dict['accZ'] = ceilStateParam[mac]['pandasDF']['accZ'].max(skipna=True)
                    # if not ceilStateParam[mac]['pandasDF']['state'].mode(dropna=True).empty:
                    #     aggregate_dict['state'] = ceilStateParam[mac]['pandasDF']['state'].mode(dropna=True).iloc[0]
                    # else:
                    #     aggregate_dict['state'] = np.nan
                    # aggregate_dict['kidOrAdult'] = ceilStateParam[mac]['pandasDF']['kidOrAdult'].mean(skipna=True)

                    # if aggregate_dict['state'].dropna().empty:
                    # print(aggregate_dict)
                    # if math.isnan(aggregate_dict['state']):
                    #     aggregate_dict['state'] = None
                    # elif ceilStateParam[mac]['pandasDF']['state'].isin([3]).sum() > 0:
                    #     aggregate_dict['state'] = 'Fall'
                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                    # elif aggregate_dict['state'] != 4:
                    #     aggregate_dict['state'] = ceilStateParam[mac]['label_state'][int(aggregate_dict['state'])]
                    # else:
                    #     aggregate_dict['state'] = None

                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                    # if math.isnan(aggregate_dict['kidOrAdult']):
                    #     aggregate_dict['kidOrAdult'] = None
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                    # elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                    #     aggregate_dict['kidOrAdult'] = 'Kid'
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                    # elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                    #     aggregate_dict['kidOrAdult'] = 'Adult'

                    # aggregate_dict = aggregate_dict.to_dict('r')
                    # if aggregate_dict:
                        # print("YYYYYYYYY")
                        # aggregate_dict = aggregate_dict[0]
                    # if not math.isnan(aggregate_dict['numSubjects']):
                    #     aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                    # if not math.isnan(aggregate_dict['roomOccupancy']):
                    #     aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                    # for key, value in aggregate_dict.items():
                    #     if str(value)[0:3] == 'nan':
                    #         aggregate_dict[key] = None

                    # print(aggregate_dict['state'])
                    # dict_copy = copy.deepcopy(aggregate_dict)
                    # my_list.append(dict_copy)
                    # print(json_string)

                    # Update the new data frame
                    # ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].append(ceil_Dict, ignore_index=True)
                    # ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].iloc[-1:,:]

                # else:
                    # Append data frame
                    # ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].append(ceil_Dict, ignore_index=True)

            # --------------------------------- Radar Tracking and Vital Sign Detection ----------------------------------------
            # ------------------------------------------------------------------------------------------------------------------

            elif radarType == 'vital':

                global vitalStateParam

                if mac not in vitalStateParam:
                    vitalStateParam[mac] = {}
                    vitalStateParam[mac]['timeNow'] = 0
                    vitalStateParam[mac]['label_state'] = ['Out of Bed', 'In Bed', 'Imminent Bed Exit']

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                vitalStateParam[mac]['radar_coord'] = radar_coord

                # Radar Time Stamp
                # deltaT = outputDict['timeStamp'] - vitalStateParam[mac]['timeNow']
                # vitalStateParam[mac]['timeNow'] = outputDict['timeStamp']
                # vital_dict = {}
                # vital_dict['timeStamp'] = outputDict['timeStamp']
                deltaT = ts - vitalStateParam[mac]['timeNow']
                vitalStateParam[mac]['timeNow'] = ts
                vital_dict = {}
                vital_dict['timeStamp'] = ts

                # Parameters Re-Initialization if Time Interval between Consecutive Data Frames Larger than Certain Threshold
                # For Robust Analytics with Data Frames / Packets Drop
                if deltaT > 5:
                    vitalStateParam[mac]['x0'] = np.nan
                    vitalStateParam[mac]['y0'] = np.nan
                    vitalStateParam[mac]['z0'] = np.nan
                    vitalStateParam[mac]['periodStationary'] = 0
                    vitalStateParam[mac]['prevTimeStationary'] = 0
                    vitalStateParam[mac]['prevBreathRate'] = 0
                    vitalStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    vitalStateParam[mac]['trackPos'] = np.zeros((0, 3))
                    vitalStateParam[mac]['label_list'] = []
                    vitalStateParam[mac]['rollingVelY'] = []
                    vitalStateParam[mac]['rollingHeight'] = []
                    vitalStateParam[mac]['previous_pointClouds'] = []  # previous point clouds
                    vitalStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    vitalStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp','bedOccupancy','breathRate','heartRate','inBedMoving','signOfLife','pointCloudDetected'])

                # Vital Sign Data Extraction
                # numTracks = 0
                # print("============================\n", outputDict,"\n------------------------------\n",vitalStateParam, "\n==============================")
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    if len(outputDict['pointCloud']) > 0:
                      vital_dict['pointCloudDetected'] = 1
                    else:
                      vital_dict['pointCloudDetected'] = 0 

                  if "numDetectedTracks" in outputDict:
                    print("+++++++++++++++++++++")
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()
                    # print(count_subjectStationary)
                    # print(vitalStateParam[mac]['periodStationary'])
                    
                    if len(vitalStateParam[mac]['previous_pointClouds']) > 0 and "trackIndexes" in outputDict:
                     trackIndices = outputDict['trackIndexes']

                     if numTracks > 0 and len(vitalStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(vitalStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                      if ('vitals' in outputDict) and vitalStateParam[mac]['periodStationary'] > periodStationary_threshold:  # and count_subjectStationary > 100:
                        vitalsDict = outputDict['vitals']
                        # if count_vitalSign == 0:
                        #     Breathsignal = np.array(vitalsDict['breathWaveform'])
                        #     Heartbeatsignal = np.array(vitalsDict['heartWaveform'])
                        #     count_vitalSign += 1
                        # else:
                        #     Breathsignal = np.concatenate((Breathsignal, np.array(vitalsDict['breathWaveform'])), axis=0)
                        #     Heartbeatsignal = np.concatenate((Heartbeatsignal, np.array(vitalsDict['heartWaveform'])), axis=0)
                        #     count_vitalSign += 1

                        # if count_vitalSign == 17:
                        #     Breathsignal = Breathsignal[15:]
                        #     Heartbeatsignal = Heartbeatsignal[15:]
                        #     count_vitalSign = 16

                        curBreathRate = float(vitalsDict["breathRate"])
                        curHeartRate = float(vitalsDict["heartRate"])

                        if vitalStateParam[mac]['prevBreathRate'] > 0:
                            if curBreathRate - vitalStateParam[mac]['prevBreathRate'] > 1:
                                curBreathRate = vitalStateParam[mac]['prevBreathRate'] + np.random.uniform(0, 0.5, 1)[0]
                            elif vitalStateParam[mac]['prevBreathRate'] - curBreathRate > 1:
                                curBreathRate = vitalStateParam[mac]['prevBreathRate'] - np.random.uniform(0, 0.5, 1)[0]

                        # if curBreathRate > 25:
                            # curBreathRate = None
                        # elif curBreathRate < 6:
                            # curBreathRate = None

                        # if curHeartRate > 200:
                            # curHeartRate = None
                        # elif curHeartRate < 30:
                            # curHeartRate = None

                        # if breathRate_MA!=0 and curBreathRate != None:
                        #     if curBreathRate > 3*breathRate_MA or curBreathRate < 0.3*breathRate_MA:
                        #         curBreathRate = None
                        #     else:
                        #         breathRate_MA = (breathRate_MA + curBreathRate)/2
                        # else:
                        #     breathRate_MA = curBreathRate
                            
                        # if heartRate_MA!=0 and curHeartRate != None:
                        #     if curHeartRate > 3*heartRate_MA or curHeartRate < 0.3*heartRate_MA:
                        #         curHeartRate = None
                        #     else:
                        #         heartRate_MA = (heartRate_MA + curHeartRate)/2     
                        # else:
                        #     heartRate_MA = curHeartRate                          

                        vital_dict['breathRate'] = curBreathRate
                        vital_dict['heartRate'] = curHeartRate
                        vitalStateParam[mac]['prevBreathRate'] = curBreathRate
                        # print("\n*******************\nvital_dict: ", vital_dict)

                      elif vitalStateParam[mac]['periodStationary'] <= periodStationary_threshold:  # count_subjectStationary <= 100:
                        # print("\n*******************\nvital_dict: X", )
                        # count_vitalSign = 0
                        vitalStateParam[mac]['prevBreathRate'] = 0
                        # vital_dict['breathRate'] = []
                        # vital_dict['heartRate'] = []

                      # if dataOk and len(detObj["x"]) > 1:
                      if numTracks > 0 and len(vitalStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(vitalStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Sign of Life
                        vital_dict['signOfLife'] = 1

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        vitalStateParam[mac]['previous_pointClouds'][:, 6] = trackIndices
                        # snr = vitalStateParam[mac]['previous_pointClouds'][:, 4]
                        # vitalStateParam[mac]['previous_pointClouds'] = vitalStateParam[mac]['previous_pointClouds'][snr > 7, :]
                        # trackIndices = trackIndices[snr > 7]
                        # x_coord = vitalStateParam[mac]['previous_pointClouds'][:, 0]
                        y_coord = vitalStateParam[mac]['previous_pointClouds'][:, 1]
                        # z_coord = vitalStateParam[mac]['previous_pointClouds'][:, 2]
                        v_coord = vitalStateParam[mac]['previous_pointClouds'][:, 3]
                        # points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Decode 3D People Counting Target List TLV
                        # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                        # 3D Struct format
                        # uint32_t     tid;     /*! @brief   tracking ID */
                        # float        posX;    /*! @brief   Detected target X coordinate, in m */
                        # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                        # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                        # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                        # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                        # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                        # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                        # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                        # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                        # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                        # float        g;
                        # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                        trackData = outputDict['trackData']

                        for trackIdx in range(numTracks):
                           
                            print("number of tracks = ", numTracks)
                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]

                            # Tracker polar coordinates
                            # trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2) # tracker range projected onto the x-y plane
                            # trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            # trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            # trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos,y_pos,z_pos]], (len(trackPos),1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # ----------------- Bed Occupancy Detection and Stationary / Moving Subject Analysis ---------------
                            # --------------------------------------------------------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(vitalStateParam[mac]['trackPos']) == 0 or np.sum(vitalStateParam[mac]['trackIDs'] == trackId) == 0:
                                vitalStateParam[mac]['trackPos'] = np.concatenate((vitalStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                vitalStateParam[mac]['trackIDs'] = np.concatenate((vitalStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                # trackPos = np.concatenate((trackPos, [[x_pos, y_pos, z_pos]]), axis=0)
                                # trackVelocity = np.concatenate((trackVelocity, [[x_vel, y_vel, z_vel]]), axis=0)
                                vitalStateParam[mac]['trackerInvalid'] = np.concatenate((vitalStateParam[mac]['trackerInvalid'], [0]), axis=0)
                                vitalStateParam[mac]['rollingVelY'].append([])
                                vitalStateParam[mac]['rollingHeight'].append([])

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(vitalStateParam[mac]['trackIDs']))[vitalStateParam[mac]['trackIDs'] == trackId][0]
                                vitalStateParam[mac]['trackerInvalid'][minDistIdx] = vitalStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                vitalStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                # trackVelocity[minDistIdx] = [x_vel, y_vel, z_vel]

                                if math.isnan(vitalStateParam[mac]['x0']):
                                    distanceMoved = 10 # Arbitrary large value
                                else:
                                    distanceMoved = np.abs(vitalStateParam[mac]['x0'] - x_pos) + np.abs(vitalStateParam[mac]['y0'] - y_pos) + np.abs(vitalStateParam[mac]['z0'] - z_pos)
                                    
                                vitalStateParam[mac]['x0'] = x_pos
                                vitalStateParam[mac]['y0'] = y_pos
                                vitalStateParam[mac]['z0'] = z_pos

                                # Rolling tracker velocity and height
                                y_height = np.percentile(y_coord, [1])
                                y_height = vitalStateParam[mac]['radar_coord'][1] - y_height
                                vitalStateParam[mac]['rollingVelY'][minDistIdx].append(y_vel)
                                vitalStateParam[mac]['rollingHeight'][minDistIdx].append(y_height)

                                # State of the subject
                                # print(np.linalg.norm([x_vel, y_vel, z_vel]))
                                # if np.average(vitalStateParam[mac]['rollingVelY'][minDistIdx]) < -0.3 and np.average(vitalStateParam[mac]['rollingHeight'][minDistIdx]) > 1.1 and \
                                    # len(vitalStateParam[mac]['rollingHeight'][minDistIdx]) == 5 and np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5:
                                    # label_list.append(3)
                                    # count_subjectStationary = 0
                                    # periodStationary = 0
                                    # vital_dict['bedOccupancy'] = 1
                                    # vitalStateParam[mac]['periodStationary'] = 0
                                    # vitalStateParam[mac]['label_list'].append(2)

                                # elif np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5 and np.linalg.norm([x_vel, y_vel, z_vel]) <= 0.3:
                                if len(v_coord[trackIndices == trackId]) > 0:
                                  # if np.abs(x_pos) < 0.6 and np.abs(z_pos) < 0.6 and np.percentile(np.abs(v_coord[trackIndices == trackId]), [99]) <= 1:
                                  if np.abs(x_pos) < xPos_threshold and np.abs(z_pos) < zPos_threshold and distanceMoved < distanceMoved_threshold:
                                    # if np.abs(x_pos) < 0.8 and np.abs(z_pos) < 0.8 and np.percentile(v_coord, [99]) <= 0.3:
                                    # print("In Bed, Subject Stationary")
                                    vital_dict['bedOccupancy'] = 1
                                    # label_list.append(0)
                                    # count_subjectStationary += 1
                                    if vitalStateParam[mac]['prevTimeStationary'] == 0:
                                        vitalStateParam[mac]['prevTimeStationary'] = ts
                                    deltaTime = ts - vitalStateParam[mac]['prevTimeStationary']
                                    vitalStateParam[mac]['periodStationary'] = vitalStateParam[mac]['periodStationary'] + deltaTime
                                    vitalStateParam[mac]['prevTimeStationary'] = ts
                                    # print(vitalStateParam[mac]['periodStationary'])
                                    vitalStateParam[mac]['label_list'].append(1)

                                  # elif np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5 and np.linalg.norm([x_vel, y_vel, z_vel]) > 0.3:
                                  # elif np.abs(x_pos) < 0.6 and np.abs(z_pos) < 0.6 and np.percentile(np.abs(v_coord[trackIndices == trackId]), [99]) > 1:
                                  elif np.abs(x_pos) < xPos_threshold and np.abs(z_pos) < zPos_threshold:
                                    # elif np.abs(x_pos) < 0.8 and np.abs(z_pos) < 0.8 and np.percentile(v_coord, [99]) > 0.3:
                                    # print("In Bed, Subject Moving")
                                    vital_dict['bedOccupancy'] = 1
                                    vital_dict['inBedMoving'] = 1
                                    # label_list.append(1)
                                    # count_subjectStationary = 0
                                    vitalStateParam[mac]['periodStationary'] = 0
                                    vitalStateParam[mac]['label_list'].append(1)

                                  elif np.abs(x_pos) > 1.0 or np.abs(z_pos) > 1.0:
                                    # print("Out of Bed")
                                    vital_dict['bedOccupancy'] = 0
                                    # label_list.append(2)
                                    # count_subjectStationary = 0
                                    vitalStateParam[mac]['periodStationary'] = 0
                                    vitalStateParam[mac]['label_list'].append(0)

                                  if len(vitalStateParam[mac]['rollingHeight'][minDistIdx]) > 4:
                                    del vitalStateParam[mac]['rollingHeight'][minDistIdx][0]
                                    del vitalStateParam[mac]['rollingVelY'][minDistIdx][0]

                                elif np.abs(x_pos) < 0.5:
                                    vital_dict['bedOccupancy'] = 1

                                elif np.abs(x_pos) > 1.0:
                                    vital_dict['bedOccupancy'] = 0

                            # --------------------------------------------------------------------------------------------------
                            # --------------------------------------------------------------------------------------------------

                        # Remove unused tracker information and parameters
                        trackerInvalidIdx = np.arange(len(vitalStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[vitalStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            rollingVelY.pop(trackerInvalidIdx[Idx])
                            rollingHeight.pop(trackerInvalidIdx[Idx])
                        vitalStateParam[mac]['trackPos']  = vitalStateParam[mac]['trackPos'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackIDs'] = vitalStateParam[mac]['trackIDs'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackerInvalid'] = vitalStateParam[mac]['trackerInvalid'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackerInvalid'] = vitalStateParam[mac]['trackerInvalid'] + 1

                if len(vitalStateParam[mac]['label_list']) >= 10:
                    if statistics.mode(vitalStateParam[mac]['label_list']) == 2:
                        
                        # Publish alert via MQTT communication channel
                        pubPayload = {"TIMESTAMP":ts, "URGENCY":2, "TYPE":3, "DETAILS":"IMMINENT BED EXIT"}
                        jsonData = json.dumps(pubPayload)
                        mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                    vitalStateParam[mac]['label_list'] = []

                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    vitalStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']
                # time.sleep(0.01)  # Sampling frequency of 30 Hz
                
                # print(vitalStateParam[mac]['pandasDF'])
                # Time Series Data Aggregation
                
                if vitalStateParam[mac]['pandasDF'].empty:
                    # Append data frame
                    vitalStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp','bedOccupancy','breathRate','heartRate','inBedMoving','signOfLife','pointCloudDetected'])
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)

                elif (vital_dict['timeStamp'] - vitalStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:
                    # aggregate_dict = vitalStateParam[mac]['pandasDF'].agg({'timeStamp': ['mean'], 'bedOccupancy': 'mean',
                    #                                                        'breathRate': 'mean', 'heartRate': 'mean'})

                    # print(vitalStateParam[mac]['pandasDF'])
                    # aggregate_dict = aggregate_dict.to_dict('r')
                    # aggregate_dict = aggregate_dict[0]
                    # if str(aggregate_dict['bedOccupancy']) != 'nan':
                    #     for key, value in aggregate_dict.items():
                    #         if str(value)[0:3] == 'nan':
                    #             aggregate_dict[key] = None
                    #     # aggregate_dict['timeStamp'] = str(dt.fromtimestamp(float(aggregate_dict['timeStamp']), tz))[:23]
                    #     if aggregate_dict['bedOccupancy'] is not None:
                    #         aggregate_dict['bedOccupancy'] = bool(round(aggregate_dict['bedOccupancy']))
                    #     # json_string = json.dumps(aggregate_dict, indent=4)
                        
                    # else:
                    #     aggregate_dict = {}
                    #     aggregate_dict['timeStamp'] = vitalStateParam[mac]['pandasDF']['timeStamp'].agg('mean')
                    #     aggregate_dict['numSubjects'] = 0
                    #     aggregate_dict['bedOccupancy'] = False
                    #     # json_string = '{}'

                    aggregate_dict = {}
                    aggregate_dict['timeStamp'] = round(vitalStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                    aggregate_dict['bedOccupancy'] = vitalStateParam[mac]['pandasDF']['bedOccupancy'].mean(skipna=True)
                    aggregate_dict['breathRate'] = vitalStateParam[mac]['pandasDF']['breathRate'].mean(skipna=True)
                    aggregate_dict['heartRate'] = vitalStateParam[mac]['pandasDF']['heartRate'].mean(skipna=True)
                    aggregate_dict['inBedMoving'] = vitalStateParam[mac]['pandasDF']['inBedMoving'].mean(skipna=True)
                    aggregate_dict['signOfLife'] = vitalStateParam[mac]['pandasDF']['signOfLife'].mean(skipna=True)
                    aggregate_dict['pointCloudDetected'] = vitalStateParam[mac]['pandasDF']['pointCloudDetected'].mean(skipna=True)

                    if not math.isnan(aggregate_dict['bedOccupancy']):
                        aggregate_dict['bedOccupancy'] = bool(round(aggregate_dict['bedOccupancy']))
                    if not math.isnan(aggregate_dict['inBedMoving']):
                        aggregate_dict['inBedMoving'] = bool(round(aggregate_dict['inBedMoving']))
                    if not math.isnan(aggregate_dict['signOfLife']):
                        aggregate_dict['signOfLife'] = bool(round(aggregate_dict['signOfLife']))
                    if not math.isnan(aggregate_dict['pointCloudDetected']):
                        if aggregate_dict['pointCloudDetected'] > 0:
                            aggregate_dict['pointCloudDetected'] = 1
                        elif aggregate_dict['pointCloudDetected'] == 0:
                            aggregate_dict['pointCloudDetected'] = 0
                    else:
                        aggregate_dict['pointCloudDetected'] = None

                    for key, value in aggregate_dict.items():
                        if str(value)[0:3] == 'nan':
                            aggregate_dict[key] = None

                    dict_copy = copy.deepcopy(aggregate_dict)
                    my_list.append(dict_copy)
                    # print("JSON: ", json_string)

                    # Update the new data frame
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)
                    vitalStateParam[mac]['pandasDF'] = vitalStateParam[mac]['pandasDF'].iloc[-1:, :]
                else:
                    # Append data frame
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)

                # Write key-value dictionary to JSON file
                # json_string = json.dumps(vital_dict, indent=4)
                # json.dump(json_string, outputFile)
                # print(json_string)

            # ------------------------------------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------------------------------------
    try: 
        print("my_list: ", my_list)
        pubPayload = {
            "DATA": my_list
        }
        op = len(pubPayload["DATA"])
        if len(pubPayload["DATA"]) > 0:
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            print(f"on message {op}", radarType)
        
            if radarType == 'wall':
                pubPayload["TYPE"]="WALL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/"+mac+"/DATA/WALL/JSON", jsonData)
                print(result)
            elif radarType == 'ceil':
                pubPayload["TYPE"]="CEIL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/CEIL/JSON", jsonData)
                print(result)
            elif radarType == 'vital':
                pubPayload["TYPE"]="VITAL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/VITAL/JSON", jsonData)
                print(result)
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")              
            time.sleep(0.1)
            dataBuffer.append(jsonData)
    except Exception as e:
        print(e)

# Decode, Process, and Publish MQTT Data Packets from Radar
# def decode_process_publish(mac, data, radarType, xShift, yShift, zShift, rotXDegree, rotYDegree, rotZDegree, aggregate_period):
def decode_multiProcess_publish(stateParam_sharedDict, devicesTbl_sharedDict, algoCfg_sharedDict, processDataQueue, macQueue):
    # global mqttc, config, aggregate_period, devicesTbl, breathRate_MA, heartRate_MA, algoCfg
  while 1:
    while macQueue.empty():
        time.sleep(0.1)
    mac = macQueue.get()
    algoCfg = {"DATA":algoCfg_sharedDict["DATA"]}
    # print("MAC: ", mac)
    # print(devicesTbl_sharedDict[mac])    
    data = devicesTbl_sharedDict[mac]["DATA_QUEUE"]
    # print("Data: ",data)
    devicesTbl[mac] = devicesTbl_sharedDict[mac]
    if devicesTbl[mac]["TYPE"] == '1':
      if mac in stateParam_sharedDict:
        wallStateParam = {}
        wallStateParam[mac] = stateParam_sharedDict[mac]
      else:
        wallStateParam = {}
    elif devicesTbl[mac]["TYPE"] == '3':
      if mac in stateParam_sharedDict:
        vitalStateParam = {}
        vitalStateParam[mac] = stateParam_sharedDict[mac]
      else:
        vitalStateParam = {}

    my_list = []
    print("algorithm configuration: ", algoCfg)
    # for x in data:
    print(len(data.items()))
    for ts_str, byteAD in data.items():
        print("parsing data")
        try:
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        if ts == 0:
            continue

        # if len(byteAD) > 52:
        if len(byteAD) > 0:
            # Error happens occasionally when decoding the raw data frame,
            # may require error analysis in future to find out the actual cause.
            try:
                outputDict = parseStandardFrame(byteAD)
            except:
                outputDict = None
                continue
            print(mac)
            # print(byteAD)
            # print(outputDict)
            # --------------------------------- Wall-Mounted Radar Tracking and Posture Analysis -------------------------------
            # ------------------------------------------------------------------------------------------------------------------
            DEVICE = devicesTbl[mac]
            if DEVICE["TYPE"] == '1':
                radarType = 'wall'
            elif DEVICE["TYPE"] == '2':
                radarType = 'ceil'
            elif DEVICE["TYPE"] == '3':
                radarType = 'vital'
            xShift = DEVICE["DEPLOY_X"]
            yShift = DEVICE["DEPLOY_Y"]
            zShift = DEVICE["DEPLOY_Z"] 
            rotXDegree = DEVICE["ROT_X"]
            rotYDegree = DEVICE["ROT_Y"]
            rotZDegree = DEVICE["ROT_Z"]

            if "fall_deltaZHeight_" + mac in algoCfg["DATA"]:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight_"+mac]
            else:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight"]

            if "fall_deltaZPos_" + mac in algoCfg["DATA"]:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos_"+mac]
            else:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos"]

            if "fall_bodyWidth_" + mac in algoCfg["DATA"]:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth_"+mac]
            else:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth"]

            if "fall_averageHeight_" + mac in algoCfg["DATA"]:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight_"+mac]
            else:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight"]

            if "fall_minZVel_" + mac in algoCfg["DATA"]:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel_"+mac]
            else:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel"]

            if "fall_numFrames_" + mac in algoCfg["DATA"]:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames_"+mac])
            else:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames"])

            if "vital_periodStationary_" + mac in algoCfg["DATA"]:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary_"+mac]
            else:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary"]

            if "vital_distanceMoved_" + mac in algoCfg["DATA"]:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved_"+mac]
            else:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved"]

            if "vital_xPos_" + mac in algoCfg["DATA"]:
                xPos_threshold = algoCfg["DATA"]["vital_xPos_"+mac]
            else:
                xPos_threshold = algoCfg["DATA"]["vital_xPos"]

            if "vital_zPos_" + mac in algoCfg["DATA"]:
                zPos_threshold = algoCfg["DATA"]["vital_zPos_"+mac]
            else:
                zPos_threshold = algoCfg["DATA"]["vital_zPos"]

            if "aggregatePeriod_" + mac in algoCfg["DATA"]:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod_"+mac]
            else:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod"]

            if radarType == 'wall':
                # global wallStateParam
                if mac not in wallStateParam:
                    wallStateParam[mac] = {}
                    wallStateParam[mac]['timeNow'] = 0
                    wallStateParam[mac]['multi_frame_count'] = 2
                    wallStateParam[mac]['label_state'] = ['Moving', 'Upright', 'Laying', 'Fall', 'None', 'Social']

                # Read Radar Setup from Database
                # xShift, yShift, zShift, rotXDegree, rotYDegree, rotZDegree = readRadarSetup(mac)

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                wallStateParam[mac]['radar_coord'] = radar_coord

                # Radar Elevation Angle of Rotation, +ve Anti-Clockwise
                # rotXDegree = DEVICE["ROT_X"]
                elevRadian = rotXDegree * np.pi / 180  # Angle in Radian
                rotXMat = np.asarray([[1, 0, 0], \
                                      [0, np.cos(elevRadian), -np.sin(elevRadian)], \
                                      [0, np.sin(elevRadian), np.cos(elevRadian)]])  # Rotation Matrix
                wallStateParam[mac]['rotXMat'] = rotXMat

                # Radar Rotation about y-axis, +ve Anti-Clockwise
                # rotYDegree = DEVICE["ROT_Y"]
                rotYRadian = rotYDegree * np.pi / 180  # Angle in Radian
                rotYMat = np.asarray([[np.cos(rotYRadian), 0, np.sin(rotYRadian)], [0, 1, 0],
                                      [-np.sin(rotYRadian), 0, np.cos(rotYRadian)]])  # Rotation Matrix
                wallStateParam[mac]['rotYMat'] = rotYMat

                # Radar Azimuth Angle of Rotation, +ve Anti-Clockwise
                # rotZDegree = DEVICE["ROT_Z"]
                azimuthRadian = rotZDegree * np.pi / 180  # Angle in Radian
                rotZMat = np.asarray([[np.cos(azimuthRadian), -np.sin(azimuthRadian), 0], \
                                      [np.sin(azimuthRadian), np.cos(azimuthRadian), 0], \
                                      [0, 0, 1]])  # Rotation Matrix
                wallStateParam[mac]['rotZMat'] = rotZMat

                # Radar Time Stamp
                deltaT = ts - wallStateParam[mac]['timeNow']
                wallStateParam[mac]['timeNow'] = ts

                # Parameters Re-Initialization if Time Interval between Consecutive Data Frames Larger than Certain Threshold
                # For Robust Analytics with Data Frames / Packets Drop

                # print(deltaT)
                if deltaT > 100:
                    wallStateParam[mac]['x0'] = np.nan
                    wallStateParam[mac]['y0'] = np.nan
                    wallStateParam[mac]['z0'] = np.nan
                    wallStateParam[mac]['timeStamp_stationary'] = np.nan
                    wallStateParam[mac]['period_stationary'] = np.nan
                    wallStateParam[mac]['timeStamp_lastSignOfLife'] = np.nan
                    wallStateParam[mac]['period_noSignOfLife'] = np.nan
                    wallStateParam[mac]['x_coord_multi'] = []
                    wallStateParam[mac]['y_coord_multi'] = []
                    wallStateParam[mac]['z_coord_multi'] = []
                    wallStateParam[mac]['rollingX'] = []
                    wallStateParam[mac]['rollingY'] = []
                    wallStateParam[mac]['rollingZ'] = []
                    wallStateParam[mac]['rollingZVel'] = []
                    wallStateParam[mac]['minZVel'] = []
                    wallStateParam[mac]['rollingHeight'] = []
                    wallStateParam[mac]['averageX'] = []
                    wallStateParam[mac]['averageY'] = []
                    wallStateParam[mac]['averageZ'] = []
                    wallStateParam[mac]['averageHeight'] = []
                    wallStateParam[mac]['labelCount'] = []
                    wallStateParam[mac]['labelGuess'] = []
                    wallStateParam[mac]['trackPos'] = np.zeros((0, 3))  # tracker position
                    wallStateParam[mac]['trackVelocity'] = np.zeros((0, 3))  # tracker velocity
                    wallStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    wallStateParam[mac]['previous_pointClouds'] = np.zeros((0, 7))  # previous point clouds
                    wallStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    wallStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp', 'trackIndex', 'numSubjects', 'roomOccupancy',
                                                                            'posX', 'posY', 'posZ', 'velX', 'velY', 'velZ', 'accX', 'accY', 'accZ', 
                                                                            'bodyHeight', 'bodyWidth', 'state', 'kidOrAdult', 'signOfLife', 'pointCloudDetected'])

                # Read parsed data from radar output dictionary
                # Radar Trackers' Data Extraction
                if outputDict is not None:
                  if 'numDetectedTracks' in outputDict:
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()

                    # Decode 3D People Counting Target List TLV
                    # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                    # 3D Struct format
                    # uint32_t     tid;     /*! @brief   tracking ID */
                    # float        posX;    /*! @brief   Detected target X coordinate, in m */
                    # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                    # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                    # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                    # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                    # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                    # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                    # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                    # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                    # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                    # float        g;
                    # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                    trackData = outputDict['trackData']

                    # if numTracks == 1:

                    #     # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                    #     trackId = trackData[0, 0]
                    #     x_pos = trackData[0, 1]
                    #     y_pos = trackData[0, 2]
                    #     z_pos = trackData[0, 3]
                    #     x_vel = trackData[0, 4]
                    #     y_vel = trackData[0, 5]
                    #     z_vel = trackData[0, 6]
                    #     x_acc = trackData[0, 7]
                    #     y_acc = trackData[0, 8]
                    #     z_acc = trackData[0, 9]

                    #     # Tracker polar coordinates
                    #     trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                    #     trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                    #     trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                    #     trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                        # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                        # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                        # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                        # trackerElevationVelocity
                        # print(trackerRange, trackerAzimuth)

                    #     # Rotation of tracker's position and velocity coordinates
                    #     [x_pos, y_pos, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_pos, y_pos, 1])
                    #     [x_vel, y_vel, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_vel, y_vel, 1])
                    #     [x_acc, y_acc, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_acc, y_acc, 1])
                    #     [dum, y_pos, z_pos] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_pos, z_pos])
                    #     [dum, y_vel, z_vel] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_vel, z_vel])
                    #     [dum, y_acc, z_acc] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_acc, z_acc])
                    #     [x_pos, dum, z_pos] = np.matmul(wallStateParam[mac]['rotYMat'], [x_pos, 1, z_pos])
                    #     [x_vel, dum, z_vel] = np.matmul(wallStateParam[mac]['rotYMat'], [x_vel, 1, z_vel])
                    #     [x_acc, dum, z_acc] = np.matmul(wallStateParam[mac]['rotYMat'], [x_acc, 1, z_acc])

                    #     # Horizontal shifting of tracker's position coordinates
                    #     x_pos = x_pos + wallStateParam[mac]['radar_coord'][0]
                    #     y_pos = y_pos + wallStateParam[mac]['radar_coord'][1]
                        # z_pos = z_pos + wallStateParam[mac]['radar_coord'][2]

                        # Tracker velocity (normalized) direction
                        # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                        # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                        # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                    #     wall_Dict['posX'] = x_pos
                    #     wall_Dict['posY'] = y_pos
                    #     wall_Dict['posZ'] = z_pos
                    #     wall_Dict['velX'] = x_vel
                    #     wall_Dict['velY'] = y_vel
                    #     wall_Dict['velZ'] = z_vel
                    #     wall_Dict['accX'] = x_acc
                    #     wall_Dict['accY'] = y_acc
                    #     wall_Dict['accZ'] = z_acc

                    # Read parsed data from radar output dictionary
                    # Radar Point Clouds + Trackers' Data Extraction and Processing
                    if len(wallStateParam[mac]['previous_pointClouds']) >= 0 and 'trackIndexes' in outputDict:
                      trackIndices = outputDict['trackIndexes']

                      if numTracks > 0 and len(wallStateParam[mac]['previous_pointClouds']) >= 0 and \
                        len(wallStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        wallStateParam[mac]['previous_pointClouds'][:,6] = trackIndices
                        snr = wallStateParam[mac]['previous_pointClouds'][:,4]
                        wallStateParam[mac]['previous_pointClouds'] = wallStateParam[mac]['previous_pointClouds'][snr > 7,:]
                        trackIndices = trackIndices[snr > 7]
                        x_coord = wallStateParam[mac]['previous_pointClouds'][:,0]
                        y_coord = wallStateParam[mac]['previous_pointClouds'][:,1]
                        z_coord = wallStateParam[mac]['previous_pointClouds'][:,2]
                        v_coord = wallStateParam[mac]['previous_pointClouds'][:,3]
                        points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Radar Point Clouds Rotation about the Z axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotZMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 0:2] = points_dum[:, 0:2]

                        # Radar Point Clouds Rotation about the X axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotXMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 1:] = points_dum[:, 1:]

                        # Radar Point Clouds Rotation about the Y axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotYMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 0] = points_dum[:, 0]
                        points[:, 2] = points_dum[:, 2]

                        # Shifting of Radar Point Clouds' Coordinates
                        points[:, 0] = points[:, 0] + wallStateParam[mac]['radar_coord'][0]
                        points[:, 1] = points[:, 1] + wallStateParam[mac]['radar_coord'][1]
                        # points[:, 2] = points[:, 2] + wallStateParam[mac]['radar_coord'][2]
                       
                        x_coord = points[:, 0]
                        y_coord = points[:, 1]
                        z_coord = points[:, 2]

                        # Process individual tracker's data for Posture Analytics
                        for trackIdx in range(numTracks):

                            print("number of tracks = ", numTracks)

                            # Time Stamp
                            wall_Dict = {}
                            wall_Dict['timeStamp'] = ts

                            # Point Cloud Detected ?
                            if 'pointCloud' in outputDict:
                              if len(outputDict['pointCloud']) > 0:
                                wall_Dict['pointCloudDetected'] = 1
                              else:
                                wall_Dict['pointCloudDetected'] = 0 

                            # Track Index
                            trackId = trackData[trackIdx, 0]
                            wall_Dict['trackIndex'] = trackId
                            # if np.isnan(trackId):
                            #     continue

                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]
                            x_acc = trackData[trackIdx, 7]
                            y_acc = trackData[trackIdx, 8]
                            z_acc = trackData[trackIdx, 9]

                            # Tracker polar coordinates
                            trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                            trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Rotation of tracker's position and velocity coordinates
                            [x_pos, y_pos, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_pos, y_pos, 1])
                            [x_vel, y_vel, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_vel, y_vel, 1])
                            [x_acc, y_acc, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_acc, y_acc, 1])
                            [dum, y_pos, z_pos] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_pos, z_pos])
                            [dum, y_vel, z_vel] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_vel, z_vel])
                            [dum, y_acc, z_acc] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_acc, z_acc])
                            [x_pos, dum, z_pos] = np.matmul(wallStateParam[mac]['rotYMat'], [x_pos, 1, z_pos])
                            [x_vel, dum, z_vel] = np.matmul(wallStateParam[mac]['rotYMat'], [x_vel, 1, z_vel])
                            [x_acc, dum, z_acc] = np.matmul(wallStateParam[mac]['rotYMat'], [x_acc, 1, z_acc])

                            # Horizontal shifting of tracker's position coordinates
                            x_pos = x_pos + wallStateParam[mac]['radar_coord'][0]
                            y_pos = y_pos + wallStateParam[mac]['radar_coord'][1]
                            # z_pos = z_pos + wallStateParam[mac]['radar_coord'][2]

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos, y_pos, z_pos]], (len(trackPos), 1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # ---------------- Posture Estimation ----------------
                            # ----------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(wallStateParam[mac]['trackPos']) == 0 or np.sum(wallStateParam[mac]['trackIDs'] == trackId) == 0:
                                wallStateParam[mac]['trackIDs'] = np.concatenate((wallStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                wallStateParam[mac]['trackPos'] = np.concatenate((wallStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                wallStateParam[mac]['trackVelocity'] = np.concatenate((wallStateParam[mac]['trackVelocity'], [[x_vel, y_vel, z_vel]]), axis=0)
                                wallStateParam[mac]['trackerInvalid'] = np.concatenate((wallStateParam[mac]['trackerInvalid'], [0]), axis=0)

                                # Append Parameters for positional change detection and dimensional analysis for posture analytics
                                wallStateParam[mac]['rollingX'].append([])
                                wallStateParam[mac]['rollingY'].append([])
                                wallStateParam[mac]['rollingZ'].append([])
                                wallStateParam[mac]['rollingZVel'].append([])
                                wallStateParam[mac]['minZVel'].append([])
                                wallStateParam[mac]['rollingHeight'].append([])
                                wallStateParam[mac]['averageX'].append([])
                                wallStateParam[mac]['averageY'].append([])
                                wallStateParam[mac]['averageZ'].append([])
                                wallStateParam[mac]['averageHeight'].append([])
                                wallStateParam[mac]['x_coord_multi'].append([])
                                wallStateParam[mac]['y_coord_multi'].append([])
                                wallStateParam[mac]['z_coord_multi'].append([])
                                wallStateParam[mac]['labelCount'].append(4)
                                wallStateParam[mac]['labelGuess'].append(4)

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(wallStateParam[mac]['trackIDs']))[wallStateParam[mac]['trackIDs'] == trackId][0]

                                # Update tracker information
                                wallStateParam[mac]['trackerInvalid'][minDistIdx] = wallStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                wallStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                wallStateParam[mac]['trackVelocity'][minDistIdx] = [x_vel, y_vel, z_vel]

                                # Sign Of life
                                if numTracks == 1:
                                    if math.isnan(wallStateParam[mac]['x0']):
                                        wallStateParam[mac]['x0'] = x_pos
                                        wallStateParam[mac]['y0'] = y_pos
                                        wallStateParam[mac]['z0'] = z_pos
                                    else:
                                        distanceMoved = np.abs(wallStateParam[mac]['x0'] - x_pos) + np.abs(wallStateParam[mac]['y0'] - y_pos) + np.abs(wallStateParam[mac]['z0'] - z_pos)
                                        wallStateParam[mac]['x0'] = x_pos
                                        wallStateParam[mac]['y0'] = y_pos
                                        wallStateParam[mac]['z0'] = z_pos
                                        if distanceMoved > 0.1 or math.isnan(wallStateParam[mac]['timeStamp_stationary']):
                                            wallStateParam[mac]['timeStamp_stationary'] = ts
                                        else:
                                            
                                            if len(x_coord[trackIndices == trackId]) > 0 or math.isnan(wallStateParam[mac]['timeStamp_lastSignOfLife']):
                                                wallStateParam[mac]['timeStamp_lastSignOfLife'] = ts
                                            else:
                                                wallStateParam[mac]['period_noSignOfLife'] = ts - wallStateParam[mac]['timeStamp_lastSignOfLife']
                                                wallStateParam[mac]['period_stationary'] = wallStateParam[mac]['timeStamp_lastSignOfLife'] - wallStateParam[mac]['timeStamp_stationary']
                                                if wallStateParam[mac]['period_noSignOfLife'] > 60 and wallStateParam[mac]['period_stationary'] > 60:
                                                    wall_Dict['signOfLife'] = 0
                                                    
                                                    # Publish alert via MQTT communication channel
                                                    # pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":1, "DETAILS":"NOSIGNOFLIFE"}
                                                    # jsonData = json.dumps(pubPayload)
                                                    # mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                                else:
                                                    wall_Dict['signOfLife'] = 1

                                # Multi-Frame Aggregation
                                wallStateParam[mac]['x_coord_multi'][minDistIdx].append(x_coord[trackIndices == trackId])
                                wallStateParam[mac]['y_coord_multi'][minDistIdx].append(y_coord[trackIndices == trackId])
                                wallStateParam[mac]['z_coord_multi'][minDistIdx].append(z_coord[trackIndices == trackId])
                                if len(wallStateParam[mac]['x_coord_multi'][minDistIdx]) > wallStateParam[mac]['multi_frame_count']:
                                    wallStateParam[mac]['x_coord_multi'][minDistIdx].pop(0)
                                    wallStateParam[mac]['y_coord_multi'][minDistIdx].pop(0)
                                    wallStateParam[mac]['z_coord_multi'][minDistIdx].pop(0)

                                # Rolling Average
                                wallStateParam[mac]['rollingX'][minDistIdx].append(x_pos)
                                wallStateParam[mac]['rollingY'][minDistIdx].append(y_pos)
                                wallStateParam[mac]['rollingZ'][minDistIdx].append(z_pos)
                                wallStateParam[mac]['rollingZVel'][minDistIdx].append(z_vel)

                                if len(wallStateParam[mac]['rollingX'][minDistIdx]) >= 10:
                                    wallStateParam[mac]['averageX'][minDistIdx].append(np.average(wallStateParam[mac]['rollingX'][minDistIdx]))
                                    wallStateParam[mac]['averageY'][minDistIdx].append(np.average(wallStateParam[mac]['rollingY'][minDistIdx]))
                                    wallStateParam[mac]['averageZ'][minDistIdx].append(np.average(wallStateParam[mac]['rollingZ'][minDistIdx]))
                                    del wallStateParam[mac]['rollingX'][minDistIdx][0]
                                    del wallStateParam[mac]['rollingY'][minDistIdx][0]
                                    del wallStateParam[mac]['rollingZ'][minDistIdx][0]

                                if len(wallStateParam[mac]['rollingZVel'][minDistIdx]) >= numFrames_threshold:
                                    wallStateParam[mac]['minZVel'][minDistIdx].append(np.percentile(wallStateParam[mac]['rollingZVel'][minDistIdx], 5))
                                    del wallStateParam[mac]['rollingZVel'][minDistIdx][0]
                                    if len(wallStateParam[mac]['minZVel'][minDistIdx]) >= 10:
                                        del wallStateParam[mac]['minZVel'][minDistIdx][0]

                                if len(wallStateParam[mac]['averageX'][minDistIdx]) > numFrames_threshold:
                                    deltaX = wallStateParam[mac]['averageX'][minDistIdx][-1] - wallStateParam[mac]['averageX'][minDistIdx][-10]
                                    deltaY = wallStateParam[mac]['averageY'][minDistIdx][-1] - wallStateParam[mac]['averageY'][minDistIdx][-10]
                                    deltaZ = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-10]
                                    # deltaZPos = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-47]
                                    deltaZPos = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-numFrames_threshold]
                                    del wallStateParam[mac]['averageX'][minDistIdx][0]
                                    del wallStateParam[mac]['averageY'][minDistIdx][0]
                                    del wallStateParam[mac]['averageZ'][minDistIdx][0]

                                    deltaDisp = np.sqrt(deltaX ** 2 + deltaY ** 2 + deltaZ ** 2)
                                    deltaDist = np.sqrt(deltaX ** 2 + deltaY ** 2)

                                    # Disable posture estimation if number of subjects > 1 or subject's range > 5m, or subject's
                                    # azimuth or elevation angle > 50 degrees.
                                    # if numTracks > 1:
                                    #     wallStateParam[mac]['labelCount'][minDistIdx] = 5
                                    #     wallStateParam[mac]['labelGuess'][minDistIdx] = 5
                                    #     wall_Dict['state'] = 5

                                    # if trackerRange > 10 or np.abs(trackerAzimuth) > 50 or np.abs(trackerElevation) > 40:
                                    #     wallStateParam[mac]['labelCount'][minDistIdx] = 4
                                    #     wallStateParam[mac]['labelGuess'][minDistIdx] = 4

                                    # elif len(x_coord[trackIndices == trackId]) > 10:
                                    # elif numTracks == 1:

                                    # elif deltaDisp > 0.05 and len(x_coord[trackIndices == trackId]) > 5:
                                    if len(x_coord[trackIndices == trackId]) > 5:
                                        x_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['x_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        y_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['y_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_height = np.percentile(np.concatenate(wallStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [99])
                                        z_height = z_height + wallStateParam[mac]['radar_coord'][2]
                                        body_width = np.sqrt(x_dim ** 2 + y_dim ** 2)
                                        # print(z_height, z_dim, body_width)
                                        wall_Dict['bodyHeight'] = z_dim[0]
                                        wall_Dict['bodyWidth'] = body_width[0]

                                        wallStateParam[mac]['rollingHeight'][minDistIdx].append(z_height)

                                        if len(wallStateParam[mac]['rollingHeight'][minDistIdx]) == 10:
                                            wallStateParam[mac]['averageHeight'][minDistIdx].append(np.average(wallStateParam[mac]['rollingHeight'][minDistIdx]))
                                            del(wallStateParam[mac]['rollingHeight'][minDistIdx][0])

                                        # if len(wallStateParam[mac]['averageHeight'][minDistIdx]) == 47:
                                        if len(wallStateParam[mac]['averageHeight'][minDistIdx]) == numFrames_threshold:
                                          # deltaHeight = wallStateParam[mac]['averageHeight'][minDistIdx][-1] - wallStateParam[mac]['averageHeight'][minDistIdx][-47]
                                          deltaHeight = wallStateParam[mac]['averageHeight'][minDistIdx][-1] - wallStateParam[mac]['averageHeight'][minDistIdx][-numFrames_threshold]
                                          del(wallStateParam[mac]['averageHeight'][minDistIdx][0])

                                          if deltaHeight < deltaZHeight_threshold and deltaZPos < deltaZPos_threshold and body_width > bodyWidth_threshold and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < averageHeight_threshold and wallStateParam[mac]['minZVel'][minDistIdx][-1] < minZVel_threshold:
                                          # if deltaHeight < -1 and deltaZPos < -1 and body_width > 1 and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < 0.8: # and z_height < 1.0 and ((body_width) / (z_dim + 0.2)) > 1.0:
                                          # if deltaHeight < -0.8 and deltaZPos < -0.8 and body_width > 0.8 and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < 0.8: # and ((body_width) / (wallStateParam[mac]['averageHeight'][minDistIdx][-1])) > 1.5:
                                            # print('Fall')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 3
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            wall_Dict['state'] = 3

                                            # Publish alert via MQTT communication channel
                                            # pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":1, "DETAILS":"FALL"}
                                            # jsonData = json.dumps(pubPayload)
                                            # mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                          elif deltaDist > 0.3:
                                            # print('Moving')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 0
                                            wall_Dict['state'] = 0

                                            # Adult and Kid Differentiation
                                            if z_height > 1.5 and z_height < 2.0 and body_width < 1.0:
                                                wall_Dict['kidOrAdult'] = 1
                                            elif z_height > 0.4 and z_height < 1.0 and body_width < 0.5:
                                                wall_Dict['kidOrAdult'] = 0

                                          elif body_width > 1 and z_height < 1.5 and ((body_width) / (z_dim + 0.2)) > 1.5:
                                            # print('Laying')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 2
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            wall_Dict['state'] = 2

                                          elif z_dim > 0.5 and body_width > 0.3 and z_height > 0.5 and ((z_dim) / (body_width + 0.0001)) > 1.2:
                                            # print('Upright')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 1
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 1
                                            wall_Dict['state'] = 1

                                          else:
                                            wallStateParam[mac]['labelCount'][minDistIdx] = wallStateParam[mac]['labelGuess'][minDistIdx]
                                            # wall_Dict['state'] = wallStateParam[mac]['label_state'][wallStateParam[mac]['labelCount'][minDistIdx]]
                                            wall_Dict['state'] = wallStateParam[mac]['labelCount'][minDistIdx]

                                # ----------------------------------------------------
                                # ----------------------------------------------------

                            # Tracker position, velocity, and acceleration
                            wall_Dict['posX'] = x_pos
                            wall_Dict['posY'] = y_pos
                            wall_Dict['posZ'] = z_pos
                            wall_Dict['velX'] = x_vel
                            wall_Dict['velY'] = y_vel
                            wall_Dict['velZ'] = z_vel
                            wall_Dict['accX'] = x_acc
                            wall_Dict['accY'] = y_acc
                            wall_Dict['accZ'] = z_acc

                            # Room Occupancy Detection
                            wall_Dict['numSubjects'] = numTracks
                            if numTracks > 0:
                                wall_Dict['roomOccupancy'] = True
                            elif numTracks == 0:
                                wall_Dict['roomOccupancy'] = False

                            # Time Series Data Aggregation                
                            if wallStateParam[mac]['pandasDF'].empty:
                                
                                # Append data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                            elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                                # print(wallStateParam[mac]['pandasDF']['trackIndex'].unique())
                                if len(wallStateParam[mac]['pandasDF']['trackIndex'].unique()) > 0:
                                  
                                  for trackInd in wallStateParam[mac]['pandasDF']['trackIndex'].unique():
                                    
                                    if np.isnan(trackInd):
                                        continue

                                    pandasDF_dum = wallStateParam[mac]['pandasDF'].loc[wallStateParam[mac]['pandasDF']['trackIndex'] == trackInd]

                                    aggregate_dict = {}
                                    aggregate_dict['timeStamp'] = round(pandasDF_dum['timeStamp'].mean(skipna=True),2)
                                    aggregate_dict['numSubjects'] = pandasDF_dum['numSubjects'].mean(skipna=True)
                                    aggregate_dict['roomOccupancy'] = pandasDF_dum['roomOccupancy'].mean(skipna=True)
                                    aggregate_dict['trackIndex'] = int(trackInd)
                                    aggregate_dict['posX'] = pandasDF_dum['posX'].mean(skipna=True)
                                    aggregate_dict['posY'] = pandasDF_dum['posY'].mean(skipna=True)
                                    aggregate_dict['posZ'] = pandasDF_dum['posZ'].mean(skipna=True)
                                    aggregate_dict['velX'] = pandasDF_dum['velX'].mean(skipna=True)
                                    aggregate_dict['velY'] = pandasDF_dum['velY'].mean(skipna=True)
                                    aggregate_dict['velZ'] = pandasDF_dum['velZ'].mean(skipna=True)
                                    aggregate_dict['accX'] = pandasDF_dum['accX'].max(skipna=True)
                                    aggregate_dict['accY'] = pandasDF_dum['accY'].max(skipna=True)
                                    aggregate_dict['accZ'] = pandasDF_dum['accZ'].max(skipna=True)
                                    aggregate_dict['bodyHeight'] = pandasDF_dum['bodyHeight'].mean(skipna=True)
                                    aggregate_dict['bodyWidth'] = pandasDF_dum['bodyWidth'].mean(skipna=True)

                                    if not pandasDF_dum['state'].mode(dropna=True).empty:
                                        aggregate_dict['state'] = pandasDF_dum['state'].mode(dropna=True).iloc[0]
                                    else:
                                        aggregate_dict['state'] = np.nan
                                    aggregate_dict['kidOrAdult'] = pandasDF_dum['kidOrAdult'].mean(skipna=True)
                                    aggregate_dict['signOfLife'] = pandasDF_dum['signOfLife'].mean(skipna=True)
                                    aggregate_dict['pointCloudDetected'] = pandasDF_dum['pointCloudDetected'].mean(skipna=True)

                                    # if aggregate_dict['state'].dropna().empty:
                                    # print(aggregate_dict)
                                    if math.isnan(aggregate_dict['state']):
                                        aggregate_dict['state'] = None
                                    elif pandasDF_dum['state'].isin([3]).sum() > 0:
                                        aggregate_dict['state'] = 'Fall'
                                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                                    elif aggregate_dict['state'] != 4:
                                        aggregate_dict['state'] = wallStateParam[mac]['label_state'][int(aggregate_dict['state'])]
                                    else:
                                        aggregate_dict['state'] = None

                                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                                    if math.isnan(aggregate_dict['kidOrAdult']):
                                        aggregate_dict['kidOrAdult'] = None
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                                        aggregate_dict['kidOrAdult'] = 'Kid'
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                                        aggregate_dict['kidOrAdult'] = 'Adult'

                                    # aggregate_dict = aggregate_dict.to_dict('r')
                                    # if aggregate_dict:
                                    # print("YYYYYYYYY")
                                    # aggregate_dict = aggregate_dict[0]
                                    if not math.isnan(aggregate_dict['numSubjects']):
                                        aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                                    if not math.isnan(aggregate_dict['roomOccupancy']):
                                        aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                                    if not math.isnan(aggregate_dict['signOfLife']):
                                      # aggregate_dict['signOfLife'] = bool(round(aggregate_dict['signOfLife']))
                                      if aggregate_dict['signOfLife'] > 0:
                                        aggregate_dict['signOfLife'] = 1
                                      elif aggregate_dict['signOfLife'] == 0:
                                        aggregate_dict['signOfLife'] = 0
                                    if not math.isnan(aggregate_dict['pointCloudDetected']):
                                      if aggregate_dict['pointCloudDetected'] > 0:
                                        aggregate_dict['pointCloudDetected'] = 1
                                      elif aggregate_dict['pointCloudDetected'] == 0:
                                        aggregate_dict['pointCloudDetected'] = 0

                                    for key, value in aggregate_dict.items():
                                        if str(value)[0:3] == 'nan':
                                            aggregate_dict[key] = None

                                    # print(aggregate_dict['state'])
                                    dict_copy = copy.deepcopy(aggregate_dict)
                                    my_list.append(dict_copy)
                                    # print(json_string)

                                # Update the new data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                                wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                            else:
            
                                # Append data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                                # print(wallStateParam)

                        # Remove unused trackers' information and parameters
                        trackerInvalidIdx = np.arange(len(wallStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[wallStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            wallStateParam[mac]['x_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['y_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['z_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingX'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingY'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingZ'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingZVel'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['minZVel'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingHeight'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageX'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageY'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageZ'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageHeight'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['labelCount'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['labelGuess'].pop(trackerInvalidIdx[Idx])

                        wallStateParam[mac]['trackPos'] = wallStateParam[mac]['trackPos'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackVelocity'] = wallStateParam[mac]['trackVelocity'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackIDs'] = wallStateParam[mac]['trackIDs'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackerInvalid'] = wallStateParam[mac]['trackerInvalid'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackerInvalid'] = wallStateParam[mac]['trackerInvalid'] + 1

                  else:
                    
                    wall_Dict = {}
                    wall_Dict['timeStamp'] = ts

                    # Point Cloud Detected ?
                    if 'pointCloud' in outputDict:
                      if len(outputDict['pointCloud']) > 0:
                        wall_Dict['pointCloudDetected'] = 1
                      else:
                        wall_Dict['pointCloudDetected'] = 0                    

                    # Time Series Data Aggregation 
                    if "pandasDF" in wallStateParam[mac]:
                        if wallStateParam[mac]['pandasDF'].empty:
                            # Append data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                        elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                            aggregate_dict = {}
                            aggregate_dict['timeStamp'] = round(wallStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                            aggregate_dict['numSubjects'] = 0
                            aggregate_dict['roomOccupancy'] = False
                            aggregate_dict['trackIndex'] = None
                            aggregate_dict['posX'] = None
                            aggregate_dict['posY'] = None
                            aggregate_dict['posZ'] = None
                            aggregate_dict['velX'] = None
                            aggregate_dict['velY'] = None
                            aggregate_dict['velZ'] = None
                            aggregate_dict['accX'] = None
                            aggregate_dict['accY'] = None
                            aggregate_dict['accZ'] = None
                            aggregate_dict['bodyHeight'] = None
                            aggregate_dict['bodyWidth'] = None
                            aggregate_dict['state'] = None
                            aggregate_dict['kidOrAdult'] = None
                            aggregate_dict['signOfLife'] = None
                            aggregate_dict['pointCloudDetected'] = wallStateParam[mac]['pandasDF']['pointCloudDetected'].mean(skipna=True)

                            if not math.isnan(aggregate_dict['pointCloudDetected']):
                              if aggregate_dict['pointCloudDetected'] > 0:
                                aggregate_dict['pointCloudDetected'] = 1
                              elif aggregate_dict['pointCloudDetected'] == 0:
                                aggregate_dict['pointCloudDetected'] = 0
                            else:
                              aggregate_dict['pointCloudDetected'] = None

                            # print(aggregate_dict['state'])
                            dict_copy = copy.deepcopy(aggregate_dict)
                            my_list.append(dict_copy)
                            # print(json_string)

                            # Update the new data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                            wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                        else:
                            # Append data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                     

                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    wallStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']

                # Time Series Data Aggregation 
                # if "pandasDF" in wallStateParam[mac]:
                #     if wallStateParam[mac]['pandasDF'].empty:
                #         # Append data frame
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                #     elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                #         aggregate_dict = {}
                #         aggregate_dict['timeStamp'] = round(wallStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                #         aggregate_dict['numSubjects'] = wallStateParam[mac]['pandasDF']['numSubjects'].mean(skipna=True)
                #         aggregate_dict['roomOccupancy'] = wallStateParam[mac]['pandasDF']['roomOccupancy'].mean(skipna=True)
                #         aggregate_dict['posX'] = wallStateParam[mac]['pandasDF']['posX'].mean(skipna=True)
                #         aggregate_dict['posY'] = wallStateParam[mac]['pandasDF']['posY'].mean(skipna=True)
                #         aggregate_dict['posZ'] = wallStateParam[mac]['pandasDF']['posZ'].mean(skipna=True)
                #         aggregate_dict['velX'] = wallStateParam[mac]['pandasDF']['velX'].mean(skipna=True)
                #         aggregate_dict['velY'] = wallStateParam[mac]['pandasDF']['velY'].mean(skipna=True)
                #         aggregate_dict['velZ'] = wallStateParam[mac]['pandasDF']['velZ'].mean(skipna=True)
                #         aggregate_dict['accX'] = wallStateParam[mac]['pandasDF']['accX'].max(skipna=True)
                #         aggregate_dict['accY'] = wallStateParam[mac]['pandasDF']['accY'].max(skipna=True)
                #         aggregate_dict['accZ'] = wallStateParam[mac]['pandasDF']['accZ'].max(skipna=True)
                #         if not wallStateParam[mac]['pandasDF']['state'].mode(dropna=True).empty:
                #             aggregate_dict['state'] = wallStateParam[mac]['pandasDF']['state'].mode(dropna=True).iloc[0]
                #         else:
                #             aggregate_dict['state'] = np.nan
                #         aggregate_dict['kidOrAdult'] = wallStateParam[mac]['pandasDF']['kidOrAdult'].mean(skipna=True)
 
                #         # if aggregate_dict['state'].dropna().empty:
                #         # print(aggregate_dict)
                #         if math.isnan(aggregate_dict['state']):
                #             aggregate_dict['state'] = None
                #         elif wallStateParam[mac]['pandasDF']['state'].isin([3]).sum() > 0:
                #             aggregate_dict['state'] = 'Fall'
                #         # elif aggregate_dict['state'].isin([4]).sum() == 0:
                #         elif aggregate_dict['state'] != 4:
                #             aggregate_dict['state'] = wallStateParam[mac]['label_state'][
                #                 int(aggregate_dict['state'])]
                #         else:
                #             aggregate_dict['state'] = None

                #         # if aggregate_dict['kidOrAdult'].dropna().empty:
                #         if math.isnan(aggregate_dict['kidOrAdult']):
                #             aggregate_dict['kidOrAdult'] = None
                #         # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                #         elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                #             aggregate_dict['kidOrAdult'] = 'Kid'
                #         # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                #         elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                #             aggregate_dict['kidOrAdult'] = 'Adult'

                #         # aggregate_dict = aggregate_dict.to_dict('r')
                #         # if aggregate_dict:
                #             # print("YYYYYYYYY")
                #             # aggregate_dict = aggregate_dict[0]
                #         if not math.isnan(aggregate_dict['numSubjects']):
                #             aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                #         if not math.isnan(aggregate_dict['roomOccupancy']):
                #             aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                #         for key, value in aggregate_dict.items():
                #             if str(value)[0:3] == 'nan':
                #                 aggregate_dict[key] = None

                #         # print(aggregate_dict['state'])
                #         dict_copy = copy.deepcopy(aggregate_dict)
                #         my_list.append(dict_copy)
                #         # print(json_string)

                #         # Update the new data frame
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                #     else:
                #         # Append data frame
                #         wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                # print(wallStateParam)
    
            # --------------------------------- Ceil-Mounted Radar Tracking and Posture Analysis -------------------------------
            # ------------------------------------------------------------------------------------------------------------------

            elif radarType == 'ceil':

                # global ceilStateParam

                if mac not in ceilStateParam:
                    ceilStateParam[mac] = {}
                    ceilStateParam[mac]['timeNow'] = 0
                    ceilStateParam[mac]['multi_frame_count'] = 1
                    ceilStateParam[mac]['label_state'] = ['Moving', 'Upright', 'Laying', 'Fall', 'None', 'Social']

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                ceilStateParam[mac]['radar_coord'] = radar_coord

                # Radar Rotation about y-axis, +ve Anti-Clockwise
                rotYRadian = rotYDegree * np.pi / 180  # Angle in Radian
                rotYMat = np.asarray([[np.cos(rotYRadian), 0, np.sin(rotYRadian)], [0, 1, 0],
                                      [-np.sin(rotYRadian), 0, np.cos(rotYRadian)]])  # Rotation Matrix
                ceilStateParam[mac]['rotYMat'] = rotYMat

                deltaT = ts - ceilStateParam[mac]['timeNow']
                ceilStateParam[mac]['timeNow'] = ts

                # Time-Interval Thresholding for Robust Analytics with Data Packets Drop
                if deltaT > 5:
                    # Parameters Re-Initialization
                    ceilStateParam[mac]['x_coord_multi'] = []
                    ceilStateParam[mac]['y_coord_multi'] = []
                    ceilStateParam[mac]['z_coord_multi'] = []
                    ceilStateParam[mac]['rollingX'] = []
                    ceilStateParam[mac]['rollingY'] = []
                    ceilStateParam[mac]['rollingZ'] = []
                    ceilStateParam[mac]['averageX'] = []
                    ceilStateParam[mac]['averageY'] = []
                    ceilStateParam[mac]['averageZ'] = []
                    ceilStateParam[mac]['labelCount'] = []
                    ceilStateParam[mac]['labelGuess'] = []
                    ceilStateParam[mac]['trackPos'] = np.zeros((0, 3))  # tracker position
                    ceilStateParam[mac]['trackVelocity'] = np.zeros((0, 3))  # tracker velocity
                    ceilStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    ceilStateParam[mac]['previous_pointClouds'] = np.zeros((0, 7))  # previous point clouds
                    ceilStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    ceilStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp', 'trackIndex', 'numSubjects', 'roomOccupancy',
                                                                            'posX', 'posY', 'posZ', 'velX', 'velY', 'velZ', 'accX', 'accY', 'accZ', 
                                                                            'bodyHeight', 'bodyWidth', 'state', 'kidOrAdult'])

                # print(outputDict)
                if outputDict is not None:
                  if "numDetectedTracks" in outputDict:
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()

                    # Decode 3D People Counting Target List TLV
                    # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                    # 3D Struct format
                    # uint32_t     tid;     /*! @brief   tracking ID */
                    # float        posX;    /*! @brief   Detected target X coordinate, in m */
                    # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                    # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                    # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                    # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                    # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                    # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                    # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                    # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                    # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                    # float        g;
                    # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                    trackData = outputDict['trackData']
                    # trackHeight = outputDict['trackHeight']

                    # if numTracks == 1:

                        # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                    #     trackId = trackData[0, 0]
                    #     x_pos = trackData[0, 1]
                    #     y_pos = trackData[0, 2]
                    #     z_pos = trackData[0, 3]
                    #     x_vel = trackData[0, 4]
                    #     y_vel = trackData[0, 5]
                    #     z_vel = trackData[0, 6]
                    #     x_acc = trackData[0, 7]
                    #     y_acc = trackData[0, 8]
                    #     z_acc = trackData[0, 9]

                        # Tracker polar coordinates
                    #     trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                    #     trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                    #     trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                    #     trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                        # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                        # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                        # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                        # trackerElevationVelocity
                        # print(trackerRange, trackerAzimuth)

                        # Tracker coordinates and velocity vector transformation
                    #     [x_pos, dum, z_pos] = np.matmul(rotYMat, [x_pos, 1, z_pos])
                    #     [x_vel, dum, z_vel] = np.matmul(rotYMat, [x_vel, 1, z_vel])
                    #     [x_acc, dum, z_acc] = np.matmul(rotYMat, [x_acc, 1, z_acc])
                    #     x_pos = x_pos + ceilStateParam[mac]['radar_coord'][0]
                    #     z_pos = z_pos + ceilStateParam[mac]['radar_coord'][1]

                        # Tracker velocity (normalized) direction
                        # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                        # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                        # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                    #     ceil_Dict['posX'] = x_pos
                    #     ceil_Dict['posY'] = z_pos
                    #     ceil_Dict['posZ'] = -y_pos
                    #     ceil_Dict['velX'] = x_vel
                    #     ceil_Dict['velY'] = z_vel
                    #     ceil_Dict['velZ'] = -y_vel
                    #     ceil_Dict['accX'] = x_acc
                    #     ceil_Dict['accY'] = z_acc
                    #     ceil_Dict['accZ'] = -y_acc

                    # if dataOk and len(detObj["x"]) > 1:
                    if len(ceilStateParam[mac]['previous_pointClouds']) > 0 and "trackIndexes" in outputDict:
                      trackIndices = outputDict['trackIndexes']

                      if numTracks > 0 and len(ceilStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(ceilStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        ceilStateParam[mac]['previous_pointClouds'][:, 6] = trackIndices
                        snr = ceilStateParam[mac]['previous_pointClouds'][:, 4]
                        ceilStateParam[mac]['previous_pointClouds'] = ceilStateParam[mac]['previous_pointClouds'][snr > 7, :]
                        trackIndices = trackIndices[snr > 7]
                        # colorMap_pointClouds = np.zeros((len(trackIndices),3)) + 0.8
                        x_coord = ceilStateParam[mac]['previous_pointClouds'][:, 0]
                        y_coord = ceilStateParam[mac]['previous_pointClouds'][:, 1]
                        z_coord = ceilStateParam[mac]['previous_pointClouds'][:, 2]
                        v_coord = ceilStateParam[mac]['previous_pointClouds'][:, 3]
                        points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Geometric Transformation
                        points = np.matmul(rotYMat, np.transpose(points))
                        points = np.transpose(points)
                        points[:, 0] = points[:, 0] + ceilStateParam[mac]['radar_coord'][0]
                        points[:, 2] = points[:, 2] + ceilStateParam[mac]['radar_coord'][2]

                        x_coord = points[:, 0]
                        y_coord = points[:, 1]
                        z_coord = points[:, 2]

                        # Read and draw trackers' information
                        for trackIdx in range(numTracks):

                            # Time Stamp
                            ceil_Dict = {}
                            ceil_Dict['timeStamp'] = ts

                            # Track Index
                            trackId = trackData[trackIdx, 0]
                            ceil_Dict['trackIndex'] = trackId

                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]
                            x_acc = trackData[trackIdx, 7]
                            y_acc = trackData[trackIdx, 8]
                            z_acc = trackData[trackIdx, 9]

                            # Tracker polar coordinates
                            trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                            trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Tracker coordinates and velocity vector transformation
                            [x_pos, dum, z_pos] = np.matmul(rotYMat, [x_pos, 1, z_pos])
                            [x_vel, dum, z_vel] = np.matmul(rotYMat, [x_vel, 1, z_vel])
                            x_pos = x_pos + ceilStateParam[mac]['radar_coord'][0]
                            z_pos = z_pos + ceilStateParam[mac]['radar_coord'][2]

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos, y_pos, z_pos]], (len(trackPos), 1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # -------------------------------- Posture Estimation ----------------------------------------------
                            # --------------------------------------------------------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(ceilStateParam[mac]['trackPos']) == 0 or np.sum(ceilStateParam[mac]['trackIDs'] == trackId) == 0:
                                # trackPos = np.concatenate((trackPos, [[x_pos,y_pos,z_pos]]), axis=0)
                                ceilStateParam[mac]['trackIDs'] = np.concatenate((ceilStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                ceilStateParam[mac]['trackPos'] = np.concatenate((ceilStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                ceilStateParam[mac]['trackVelocity'] = np.concatenate((ceilStateParam[mac]['trackVelocity'], [[x_vel, y_vel, z_vel]]), axis=0)
                                ceilStateParam[mac]['trackerInvalid'] = np.concatenate((ceilStateParam[mac]['trackerInvalid'], [0]), axis=0)

                                # Append Parameters for positional change detection and dimensional analysis
                                ceilStateParam[mac]['rollingX'].append([])
                                ceilStateParam[mac]['rollingY'].append([])
                                ceilStateParam[mac]['rollingZ'].append([])
                                ceilStateParam[mac]['averageX'].append([])
                                ceilStateParam[mac]['averageY'].append([])
                                ceilStateParam[mac]['averageZ'].append([])
                                ceilStateParam[mac]['x_coord_multi'].append([])
                                ceilStateParam[mac]['y_coord_multi'].append([])
                                ceilStateParam[mac]['z_coord_multi'].append([])
                                ceilStateParam[mac]['labelCount'].append(4)
                                ceilStateParam[mac]['labelGuess'].append(4)

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(ceilStateParam[mac]['trackIDs']))[ceilStateParam[mac]['trackIDs'] == trackId][0]

                                # Update tracker information
                                ceilStateParam[mac]['trackerInvalid'][minDistIdx] = ceilStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                ceilStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                ceilStateParam[mac]['trackVelocity'][minDistIdx] = [x_vel, y_vel, z_vel]

                                # Multi-Frame Aggregation
                                ceilStateParam[mac]['x_coord_multi'][minDistIdx].append(x_coord[trackIndices == trackId])
                                ceilStateParam[mac]['y_coord_multi'][minDistIdx].append(y_coord[trackIndices == trackId])
                                ceilStateParam[mac]['z_coord_multi'][minDistIdx].append(z_coord[trackIndices == trackId])
                                if len(ceilStateParam[mac]['x_coord_multi'][minDistIdx]) > ceilStateParam[mac]['multi_frame_count']:
                                    ceilStateParam[mac]['x_coord_multi'][minDistIdx].pop(0)
                                    ceilStateParam[mac]['y_coord_multi'][minDistIdx].pop(0)
                                    ceilStateParam[mac]['z_coord_multi'][minDistIdx].pop(0)

                                # Rolling Average
                                ceilStateParam[mac]['rollingX'][minDistIdx].append(x_pos)
                                ceilStateParam[mac]['rollingY'][minDistIdx].append(y_pos)
                                ceilStateParam[mac]['rollingZ'][minDistIdx].append(z_pos)

                                if len(ceilStateParam[mac]['rollingX'][minDistIdx]) >= 5:
                                    ceilStateParam[mac]['averageX'][minDistIdx].append(np.average(ceilStateParam[mac]['rollingX'][minDistIdx]))
                                    ceilStateParam[mac]['averageY'][minDistIdx].append(np.average(ceilStateParam[mac]['rollingY'][minDistIdx]))
                                    ceilStateParam[mac]['averageZ'][minDistIdx].append(np.average(ceilStateParam[mac]['rollingZ'][minDistIdx]))
                                    del ceilStateParam[mac]['rollingX'][minDistIdx][0]
                                    del ceilStateParam[mac]['rollingY'][minDistIdx][0]
                                    del ceilStateParam[mac]['rollingZ'][minDistIdx][0]

                                if len(ceilStateParam[mac]['averageX'][minDistIdx]) > 10:
                                    deltaX = ceilStateParam[mac]['averageX'][minDistIdx][-1] - ceilStateParam[mac]['averageX'][minDistIdx][-5]
                                    deltaY = ceilStateParam[mac]['averageY'][minDistIdx][-1] - ceilStateParam[mac]['averageY'][minDistIdx][-5]
                                    deltaZ = ceilStateParam[mac]['averageZ'][minDistIdx][-1] - ceilStateParam[mac]['averageZ'][minDistIdx][-5]
                                    del ceilStateParam[mac]['averageX'][minDistIdx][0]
                                    del ceilStateParam[mac]['averageY'][minDistIdx][0]
                                    del ceilStateParam[mac]['averageZ'][minDistIdx][0]

                                    deltaDisp = np.sqrt(deltaX ** 2 + deltaY ** 2 + deltaZ ** 2)
                                    deltaDist = np.sqrt(deltaX ** 2 + deltaZ ** 2)

                                    # Disable posture estimation if number of subjects > 1 or subject's range > 5m, or subject's
                                    # azimuth or elevation angle > 50 degrees.
                                    # if numTracks > 1:
                                    #     ceilStateParam[mac]['labelCount'][minDistIdx] = 5
                                    #     ceilStateParam[mac]['labelGuess'][minDistIdx] = 5
                                    #     ceil_Dict['state'] = 5

                                    if trackerRange > 5 or np.abs(trackerAzimuth) > 50 or np.abs(trackerElevation) > 40:
                                        ceilStateParam[mac]['labelCount'][minDistIdx] = 4
                                        ceilStateParam[mac]['labelGuess'][minDistIdx] = 4

                                    # elif len(x_coord[trackIndices == trackId]) > 10:
                                    # elif numTracks == 1:

                                    # elif deltaDisp > 0.1 and len(x_coord[trackIndices == trackId]) > 10:
                                    elif len(x_coord[trackIndices == trackId]) > 10:

                                        x_dim = np.diff(np.percentile(np.concatenate(ceilStateParam[mac]['x_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        y_dim = np.diff(np.percentile(np.concatenate(ceilStateParam[mac]['y_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_dim = np.diff(np.percentile(np.concatenate(ceilStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        y_height = np.percentile(np.concatenate(ceilStateParam[mac]['y_coord_multi'][minDistIdx][:], axis=0), [1])
                                        y_height = ceilStateParam[mac]['radar_coord'][2] - y_height
                                        body_width = np.sqrt(x_dim ** 2 + z_dim ** 2)
                                        # print(y_height, y_dim, body_width)
                                        ceil_Dict['bodyHeight'] = y_height[0]
                                        ceil_Dict['bodyWidth'] = body_width[0]

                                        if deltaY > 0.35 and body_width > 0.5 and y_height < 1.0 and ((body_width) / (y_height + 0.2)) > 1.0:
                                            # print("Fall")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 3
                                            ceilStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            ceil_Dict['state'] = 3

                                            # Publish alert via MQTT communication channel
                                            # pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":2, "DETAILS":"FALL"}
                                            # jsonData = json.dumps(pubPayload)
                                            # mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                        elif deltaDist > 0.3:
                                            # print("Moving")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 0
                                            ceil_Dict['state'] = 0

                                            # Adult and Kid Differentiation
                                            if y_height > 1.5 and y_height < 2.0 and body_width < 1.0:
                                                ceil_Dict['kidOrAdult'] = 1

                                            elif y_height > 0.4 and y_height < 1.0 and body_width < 0.5:
                                                ceil_Dict['kidOrAdult'] = 0

                                        elif body_width > 0.5 and y_height < 1.1 and ((body_width) / (y_height + 0.2)) > 1.8:
                                            # print("Laying")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 2
                                            ceilStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            ceil_Dict['state'] = 2

                                        elif body_width > 0.2 and y_height > 0.5 and ((y_height) / (body_width + 0.0001)) > 1.2:
                                            # print("Upright")
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = 1
                                            ceilStateParam[mac]['labelGuess'][minDistIdx] = 1
                                            ceil_Dict['state'] = 1

                                        else:
                                            ceilStateParam[mac]['labelCount'][minDistIdx] = ceilStateParam[mac]['labelGuess'][minDistIdx]
                                            # ceil_Dict['state'] = ceilStateParam[mac]['label_state'][ceilStateParam[mac]['labelCount'][minDistIdx]]
                                            ceil_Dict['state'] = ceilStateParam[mac]['labelCount'][minDistIdx]

                                # ----------------------------------------------------------------------------------------------
                                # ----------------------------------------------------------------------------------------------

                            # Tracker position, velocity, and acceleration
                            ceil_Dict['posX'] = x_pos
                            ceil_Dict['posY'] = z_pos
                            ceil_Dict['posZ'] = -y_pos
                            ceil_Dict['velX'] = x_vel
                            ceil_Dict['velY'] = z_vel
                            ceil_Dict['velZ'] = -y_vel
                            ceil_Dict['accX'] = x_acc
                            ceil_Dict['accY'] = z_acc
                            ceil_Dict['accZ'] = -y_acc

                            # Room Occupancy Detection
                            ceil_Dict['numSubjects'] = numTracks
                            if numTracks > 0:
                                ceil_Dict['roomOccupancy'] = True
                            elif numTracks == 0:
                                ceil_Dict['roomOccupancy'] = False

                            # Time Series Data Aggregation
                            if ceilStateParam[mac]['pandasDF'].empty:
                                
                                # Append data frame
                                ceilStateParam[mac]['pandasDF'] = pd.concat(ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict]), ignore_index=True)

                            elif (ceil_Dict['timeStamp'] - ceilStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                                if len(ceilStateParam[mac]['pandasDF']['trackIndex'].unique()) > 0:
                                  
                                  for trackInd in ceilStateParam[mac]['pandasDF']['trackIndex'].unique():
                                    
                                    if np.isnan(trackInd):
                                        continue

                                    pandasDF_dum = ceilStateParam[mac]['pandasDF'].loc[ceilStateParam[mac]['pandasDF']['trackIndex'] == trackInd]

                                    aggregate_dict = {}
                                    aggregate_dict['timeStamp'] = round(pandasDF_dum['timeStamp'].mean(skipna=True),2)
                                    aggregate_dict['numSubjects'] = pandasDF_dum['numSubjects'].mean(skipna=True)
                                    aggregate_dict['roomOccupancy'] = pandasDF_dum['roomOccupancy'].mean(skipna=True)
                                    aggregate_dict['trackIndex'] = int(trackInd)
                                    aggregate_dict['posX'] = pandasDF_dum['posX'].mean(skipna=True)
                                    aggregate_dict['posY'] = pandasDF_dum['posY'].mean(skipna=True)
                                    aggregate_dict['posZ'] = pandasDF_dum['posZ'].mean(skipna=True)
                                    aggregate_dict['velX'] = pandasDF_dum['velX'].mean(skipna=True)
                                    aggregate_dict['velY'] = pandasDF_dum['velY'].mean(skipna=True)
                                    aggregate_dict['velZ'] = pandasDF_dum['velZ'].mean(skipna=True)
                                    aggregate_dict['accX'] = pandasDF_dum['accX'].max(skipna=True)
                                    aggregate_dict['accY'] = pandasDF_dum['accY'].max(skipna=True)
                                    aggregate_dict['accZ'] = pandasDF_dum['accZ'].max(skipna=True)
                                    aggregate_dict['bodyHeight'] = pandasDF_dum['bodyHeight'].mean(skipna=True)
                                    aggregate_dict['bodyWidth'] = pandasDF_dum['bodyWidth'].mean(skipna=True)

                                    if not pandasDF_dum['state'].mode(dropna=True).empty:
                                        aggregate_dict['state'] = pandasDF_dum['state'].mode(dropna=True).iloc[0]
                                    else:
                                        aggregate_dict['state'] = np.nan
                                    aggregate_dict['kidOrAdult'] = pandasDF_dum['kidOrAdult'].mean(skipna=True)

                                    # if aggregate_dict['state'].dropna().empty:
                                    # print(aggregate_dict)
                                    if math.isnan(aggregate_dict['state']):
                                        aggregate_dict['state'] = None
                                    elif pandasDF_dum['state'].isin([3]).sum() > 0:
                                        aggregate_dict['state'] = 'Fall'
                                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                                    elif aggregate_dict['state'] != 4:
                                        aggregate_dict['state'] = ceilStateParam[mac]['label_state'][int(aggregate_dict['state'])]
                                    else:
                                        aggregate_dict['state'] = None

                                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                                    if math.isnan(aggregate_dict['kidOrAdult']):
                                        aggregate_dict['kidOrAdult'] = None
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                                        aggregate_dict['kidOrAdult'] = 'Kid'
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                                        aggregate_dict['kidOrAdult'] = 'Adult'

                                    # aggregate_dict = aggregate_dict.to_dict('r')
                                    # if aggregate_dict:
                                    # print("YYYYYYYYY")
                                    # aggregate_dict = aggregate_dict[0]
                                    if not math.isnan(aggregate_dict['numSubjects']):
                                        aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                                    if not math.isnan(aggregate_dict['roomOccupancy']):
                                        aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                                    for key, value in aggregate_dict.items():
                                        if str(value)[0:3] == 'nan':
                                            aggregate_dict[key] = None

                                    print(aggregate_dict['state'])
                                    dict_copy = copy.deepcopy(aggregate_dict)
                                    my_list.append(dict_copy)
                                    # print(json_string)

                                # Update the new data frame
                                ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)
                                ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].iloc[-1:,:]

                            else:
                    
                                # Append data frame
                                ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)


                        # Remove unused tracker information and parameters
                        trackerInvalidIdx = np.arange(len(ceilStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[ceilStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            ceilStateParam[mac]['x_coord_multi'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['y_coord_multi'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['z_coord_multi'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['rollingX'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['rollingY'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['rollingZ'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['averageX'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['averageY'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['averageZ'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['labelCount'].pop(trackerInvalidIdx[Idx])
                            ceilStateParam[mac]['labelGuess'].pop(trackerInvalidIdx[Idx])

                        ceilStateParam[mac]['trackPos'] = ceilStateParam[mac]['trackPos'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackVelocity'] = ceilStateParam[mac]['trackVelocity'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackIDs'] = ceilStateParam[mac]['trackIDs'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackerInvalid'] = ceilStateParam[mac]['trackerInvalid'][ceilStateParam[mac]['trackerInvalid'] == 0]
                        ceilStateParam[mac]['trackerInvalid'] = ceilStateParam[mac]['trackerInvalid'] + 1

                  else:
                    
                    ceil_Dict = {}
                    ceil_Dict['timeStamp'] = ts
                    
                    # Time Series Data Aggregation 
                    if "pandasDF" in ceilStateParam[mac]:
                        if ceilStateParam[mac]['pandasDF'].empty:
                            # Append data frame
                            ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)

                        elif (ceil_Dict['timeStamp'] - ceilStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                            aggregate_dict = {}
                            aggregate_dict['timeStamp'] = round(ceilStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                            aggregate_dict['numSubjects'] = 0
                            aggregate_dict['roomOccupancy'] = False
                            aggregate_dict['trackIndex'] = None
                            aggregate_dict['posX'] = None
                            aggregate_dict['posY'] = None
                            aggregate_dict['posZ'] = None
                            aggregate_dict['velX'] = None
                            aggregate_dict['velY'] = None
                            aggregate_dict['velZ'] = None
                            aggregate_dict['accX'] = None
                            aggregate_dict['accY'] = None
                            aggregate_dict['accZ'] = None
                            aggregate_dict['bodyHeight'] = None
                            aggregate_dict['bodyWidth'] = None
                            aggregate_dict['state'] = None
                            aggregate_dict['kidOrAdult'] = None

                            # print(aggregate_dict['state'])
                            dict_copy = copy.deepcopy(aggregate_dict)
                            my_list.append(dict_copy)
                            # print(json_string)

                            # Update the new data frame
                            ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)
                            ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].iloc[-1:,:]

                        else:
                            # Append data frame
                            ceilStateParam[mac]['pandasDF'] = pd.concat([ceilStateParam[mac]['pandasDF'], pd.DataFrame([ceil_Dict])], ignore_index=True)


                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    ceilStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']

                # Time Series Data Aggregation
                # if ceilStateParam[mac]['pandasDF'].empty:
                    # Append data frame
                #     ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].append(ceil_Dict, ignore_index=True)

                # elif (ceil_Dict['timeStamp'] - ceilStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:
                    # aggregate_dict = ceilStateParam[mac]['pandasDF'].agg({'timeStamp':'mean',
                    #                                                'numSubjects': 'mean',
                    #                                                'roomOccupancy': 'mean',
                    #                                                'posX':'mean', 'posY':'mean', 'posZ':'mean',
                    #                                                'velX':'mean', 'velY':'mean', 'velZ':'mean',
                    #                                                'accX':'max', 'accY':'max', 'accZ':'max',
                    #                                                'state': lambda x: pd.Series.mode(x, dropna=True),
                    #                                                'kidOrAdult': 'mean'})

                    # if aggregate_dict['state'].dropna().empty:
                    #     aggregate_dict['state'] = None
                    # elif ceilStateParam[mac]['pandasDF']['state'].isin([3]).sum() > 0:
                    #     aggregate_dict['state'] = 'Fall'
                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                    #     aggregate_dict['state'] = ceilStateParam[mac]['label_state'][int(aggregate_dict['state'].iloc[0])]
                    # else:
                    #     aggregate_dict['state'] = None

                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                    #     aggregate_dict['kidOrAdult'] = None
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                    #     aggregate_dict['kidOrAdult'] = 'Kid'
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                    #     aggregate_dict['kidOrAdult'] = 'Adult'

                    # aggregate_dict = aggregate_dict.to_dict('r')
                    # if aggregate_dict:
                    #     aggregate_dict = aggregate_dict[0]
                    #     for key, value in aggregate_dict.items():
                    #         if str(value)[0:3] == 'nan':
                    #             aggregate_dict[key] = None
                    #     # aggregate_dict['timeStamp'] = str(dt.fromtimestamp(float(aggregate_dict['timeStamp']), tz))[:23]
                    #     aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                    #     aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                    #     # json_string = json.dumps(aggregate_dict, indent=4)
                        
                    # else:
                    #     aggregate_dict = {}
                    #     aggregate_dict['timeStamp'] = ceilStateParam[mac]['pandasDF']['timeStamp'].agg('mean')
                    #     aggregate_dict['numSubjects'] = 0
                    #     aggregate_dict['roomOccupancy'] = False

                    # aggregate_dict = {}
                    # aggregate_dict['timeStamp'] = round(ceilStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                    # aggregate_dict['numSubjects'] = ceilStateParam[mac]['pandasDF']['numSubjects'].mean(skipna=True)
                    # aggregate_dict['roomOccupancy'] = ceilStateParam[mac]['pandasDF']['roomOccupancy'].mean(skipna=True)
                    # aggregate_dict['posX'] = ceilStateParam[mac]['pandasDF']['posX'].mean(skipna=True)
                    # aggregate_dict['posY'] = ceilStateParam[mac]['pandasDF']['posY'].mean(skipna=True)
                    # aggregate_dict['posZ'] = ceilStateParam[mac]['pandasDF']['posZ'].mean(skipna=True)
                    # aggregate_dict['velX'] = ceilStateParam[mac]['pandasDF']['velX'].mean(skipna=True)
                    # aggregate_dict['velY'] = ceilStateParam[mac]['pandasDF']['velY'].mean(skipna=True)
                    # aggregate_dict['velZ'] = ceilStateParam[mac]['pandasDF']['velZ'].mean(skipna=True)
                    # aggregate_dict['accX'] = ceilStateParam[mac]['pandasDF']['accX'].max(skipna=True)
                    # aggregate_dict['accY'] = ceilStateParam[mac]['pandasDF']['accY'].max(skipna=True)
                    # aggregate_dict['accZ'] = ceilStateParam[mac]['pandasDF']['accZ'].max(skipna=True)
                    # if not ceilStateParam[mac]['pandasDF']['state'].mode(dropna=True).empty:
                    #     aggregate_dict['state'] = ceilStateParam[mac]['pandasDF']['state'].mode(dropna=True).iloc[0]
                    # else:
                    #     aggregate_dict['state'] = np.nan
                    # aggregate_dict['kidOrAdult'] = ceilStateParam[mac]['pandasDF']['kidOrAdult'].mean(skipna=True)

                    # if aggregate_dict['state'].dropna().empty:
                    # print(aggregate_dict)
                    # if math.isnan(aggregate_dict['state']):
                    #     aggregate_dict['state'] = None
                    # elif ceilStateParam[mac]['pandasDF']['state'].isin([3]).sum() > 0:
                    #     aggregate_dict['state'] = 'Fall'
                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                    # elif aggregate_dict['state'] != 4:
                    #     aggregate_dict['state'] = ceilStateParam[mac]['label_state'][int(aggregate_dict['state'])]
                    # else:
                    #     aggregate_dict['state'] = None

                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                    # if math.isnan(aggregate_dict['kidOrAdult']):
                    #     aggregate_dict['kidOrAdult'] = None
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                    # elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                    #     aggregate_dict['kidOrAdult'] = 'Kid'
                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                    # elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                    #     aggregate_dict['kidOrAdult'] = 'Adult'

                    # aggregate_dict = aggregate_dict.to_dict('r')
                    # if aggregate_dict:
                        # print("YYYYYYYYY")
                        # aggregate_dict = aggregate_dict[0]
                    # if not math.isnan(aggregate_dict['numSubjects']):
                    #     aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                    # if not math.isnan(aggregate_dict['roomOccupancy']):
                    #     aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                    # for key, value in aggregate_dict.items():
                    #     if str(value)[0:3] == 'nan':
                    #         aggregate_dict[key] = None

                    # print(aggregate_dict['state'])
                    # dict_copy = copy.deepcopy(aggregate_dict)
                    # my_list.append(dict_copy)
                    # print(json_string)

                    # Update the new data frame
                    # ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].append(ceil_Dict, ignore_index=True)
                    # ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].iloc[-1:,:]

                # else:
                    # Append data frame
                    # ceilStateParam[mac]['pandasDF'] = ceilStateParam[mac]['pandasDF'].append(ceil_Dict, ignore_index=True)

            # --------------------------------- Radar Tracking and Vital Sign Detection ----------------------------------------
            # ------------------------------------------------------------------------------------------------------------------

            elif radarType == 'vital':

                # global vitalStateParam

                if mac not in vitalStateParam:
                    vitalStateParam[mac] = {}
                    vitalStateParam[mac]['timeNow'] = 0
                    vitalStateParam[mac]['label_state'] = ['Out of Bed', 'In Bed', 'Imminent Bed Exit']

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                vitalStateParam[mac]['radar_coord'] = radar_coord

                # Radar Time Stamp
                # deltaT = outputDict['timeStamp'] - vitalStateParam[mac]['timeNow']
                # vitalStateParam[mac]['timeNow'] = outputDict['timeStamp']
                # vital_dict = {}
                # vital_dict['timeStamp'] = outputDict['timeStamp']
                deltaT = ts - vitalStateParam[mac]['timeNow']
                vitalStateParam[mac]['timeNow'] = ts
                vital_dict = {}
                vital_dict['timeStamp'] = ts

                # Parameters Re-Initialization if Time Interval between Consecutive Data Frames Larger than Certain Threshold
                # For Robust Analytics with Data Frames / Packets Drop
                if deltaT > 5:
                    vitalStateParam[mac]['x0'] = np.nan
                    vitalStateParam[mac]['y0'] = np.nan
                    vitalStateParam[mac]['z0'] = np.nan
                    vitalStateParam[mac]['periodStationary'] = 0
                    vitalStateParam[mac]['prevTimeStationary'] = 0
                    vitalStateParam[mac]['prevBreathRate'] = 0
                    vitalStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    vitalStateParam[mac]['trackPos'] = np.zeros((0, 3))
                    vitalStateParam[mac]['label_list'] = []
                    vitalStateParam[mac]['rollingVelY'] = []
                    vitalStateParam[mac]['rollingHeight'] = []
                    vitalStateParam[mac]['previous_pointClouds'] = []  # previous point clouds
                    vitalStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    vitalStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp','bedOccupancy','breathRate','heartRate','inBedMoving','signOfLife','pointCloudDetected'])

                # Vital Sign Data Extraction
                # numTracks = 0
                # print("============================\n", outputDict,"\n------------------------------\n",vitalStateParam, "\n==============================")
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    if len(outputDict['pointCloud']) > 0:
                      vital_dict['pointCloudDetected'] = 1
                    else:
                      vital_dict['pointCloudDetected'] = 0 

                  if "numDetectedTracks" in outputDict:
                    print("+++++++++++++++++++++")
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()
                    # print(count_subjectStationary)
                    # print(vitalStateParam[mac]['periodStationary'])
                    
                    if len(vitalStateParam[mac]['previous_pointClouds']) > 0 and "trackIndexes" in outputDict:
                     trackIndices = outputDict['trackIndexes']

                     if numTracks > 0 and len(vitalStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(vitalStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                      if ('vitals' in outputDict) and vitalStateParam[mac]['periodStationary'] > periodStationary_threshold:  # and count_subjectStationary > 100:
                        vitalsDict = outputDict['vitals']
                        # if count_vitalSign == 0:
                        #     Breathsignal = np.array(vitalsDict['breathWaveform'])
                        #     Heartbeatsignal = np.array(vitalsDict['heartWaveform'])
                        #     count_vitalSign += 1
                        # else:
                        #     Breathsignal = np.concatenate((Breathsignal, np.array(vitalsDict['breathWaveform'])), axis=0)
                        #     Heartbeatsignal = np.concatenate((Heartbeatsignal, np.array(vitalsDict['heartWaveform'])), axis=0)
                        #     count_vitalSign += 1

                        # if count_vitalSign == 17:
                        #     Breathsignal = Breathsignal[15:]
                        #     Heartbeatsignal = Heartbeatsignal[15:]
                        #     count_vitalSign = 16

                        curBreathRate = float(vitalsDict["breathRate"])
                        curHeartRate = float(vitalsDict["heartRate"])

                        if vitalStateParam[mac]['prevBreathRate'] > 0:
                            if curBreathRate - vitalStateParam[mac]['prevBreathRate'] > 1:
                                curBreathRate = vitalStateParam[mac]['prevBreathRate'] + np.random.uniform(0, 0.5, 1)[0]
                            elif vitalStateParam[mac]['prevBreathRate'] - curBreathRate > 1:
                                curBreathRate = vitalStateParam[mac]['prevBreathRate'] - np.random.uniform(0, 0.5, 1)[0]

                        # if curBreathRate > 25:
                            # curBreathRate = None
                        # elif curBreathRate < 6:
                            # curBreathRate = None

                        # if curHeartRate > 200:
                            # curHeartRate = None
                        # elif curHeartRate < 30:
                            # curHeartRate = None

                        # if breathRate_MA!=0 and curBreathRate != None:
                        #     if curBreathRate > 3*breathRate_MA or curBreathRate < 0.3*breathRate_MA:
                        #         curBreathRate = None
                        #     else:
                        #         breathRate_MA = (breathRate_MA + curBreathRate)/2
                        # else:
                        #     breathRate_MA = curBreathRate
                            
                        # if heartRate_MA!=0 and curHeartRate != None:
                        #     if curHeartRate > 3*heartRate_MA or curHeartRate < 0.3*heartRate_MA:
                        #         curHeartRate = None
                        #     else:
                        #         heartRate_MA = (heartRate_MA + curHeartRate)/2     
                        # else:
                        #     heartRate_MA = curHeartRate                          

                        vital_dict['breathRate'] = curBreathRate
                        vital_dict['heartRate'] = curHeartRate
                        vitalStateParam[mac]['prevBreathRate'] = curBreathRate
                        # print("\n*******************\nvital_dict: ", vital_dict)

                      elif vitalStateParam[mac]['periodStationary'] <= periodStationary_threshold:  # count_subjectStationary <= 100:
                        # print("\n*******************\nvital_dict: X", )
                        # count_vitalSign = 0
                        vitalStateParam[mac]['prevBreathRate'] = 0
                        # vital_dict['breathRate'] = []
                        # vital_dict['heartRate'] = []

                      # if dataOk and len(detObj["x"]) > 1:
                      if numTracks > 0 and len(vitalStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(vitalStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Sign of Life
                        vital_dict['signOfLife'] = 1

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        vitalStateParam[mac]['previous_pointClouds'][:, 6] = trackIndices
                        # snr = vitalStateParam[mac]['previous_pointClouds'][:, 4]
                        # vitalStateParam[mac]['previous_pointClouds'] = vitalStateParam[mac]['previous_pointClouds'][snr > 7, :]
                        # trackIndices = trackIndices[snr > 7]
                        # x_coord = vitalStateParam[mac]['previous_pointClouds'][:, 0]
                        y_coord = vitalStateParam[mac]['previous_pointClouds'][:, 1]
                        # z_coord = vitalStateParam[mac]['previous_pointClouds'][:, 2]
                        v_coord = vitalStateParam[mac]['previous_pointClouds'][:, 3]
                        # points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Decode 3D People Counting Target List TLV
                        # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                        # 3D Struct format
                        # uint32_t     tid;     /*! @brief   tracking ID */
                        # float        posX;    /*! @brief   Detected target X coordinate, in m */
                        # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                        # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                        # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                        # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                        # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                        # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                        # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                        # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                        # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                        # float        g;
                        # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                        trackData = outputDict['trackData']

                        for trackIdx in range(numTracks):
                           
                            print("number of tracks = ", numTracks)
                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]

                            # Tracker polar coordinates
                            # trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2) # tracker range projected onto the x-y plane
                            # trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            # trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            # trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos,y_pos,z_pos]], (len(trackPos),1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # ----------------- Bed Occupancy Detection and Stationary / Moving Subject Analysis ---------------
                            # --------------------------------------------------------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(vitalStateParam[mac]['trackPos']) == 0 or np.sum(vitalStateParam[mac]['trackIDs'] == trackId) == 0:
                                vitalStateParam[mac]['trackPos'] = np.concatenate((vitalStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                vitalStateParam[mac]['trackIDs'] = np.concatenate((vitalStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                # trackPos = np.concatenate((trackPos, [[x_pos, y_pos, z_pos]]), axis=0)
                                # trackVelocity = np.concatenate((trackVelocity, [[x_vel, y_vel, z_vel]]), axis=0)
                                vitalStateParam[mac]['trackerInvalid'] = np.concatenate((vitalStateParam[mac]['trackerInvalid'], [0]), axis=0)
                                vitalStateParam[mac]['rollingVelY'].append([])
                                vitalStateParam[mac]['rollingHeight'].append([])

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(vitalStateParam[mac]['trackIDs']))[vitalStateParam[mac]['trackIDs'] == trackId][0]
                                vitalStateParam[mac]['trackerInvalid'][minDistIdx] = vitalStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                vitalStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                # trackVelocity[minDistIdx] = [x_vel, y_vel, z_vel]

                                if math.isnan(vitalStateParam[mac]['x0']):
                                    distanceMoved = 10 # Arbitrary large value
                                else:
                                    distanceMoved = np.abs(vitalStateParam[mac]['x0'] - x_pos) + np.abs(vitalStateParam[mac]['y0'] - y_pos) + np.abs(vitalStateParam[mac]['z0'] - z_pos)
                                    
                                vitalStateParam[mac]['x0'] = x_pos
                                vitalStateParam[mac]['y0'] = y_pos
                                vitalStateParam[mac]['z0'] = z_pos

                                # Rolling tracker velocity and height
                                y_height = np.percentile(y_coord, [1])
                                y_height = vitalStateParam[mac]['radar_coord'][1] - y_height
                                vitalStateParam[mac]['rollingVelY'][minDistIdx].append(y_vel)
                                vitalStateParam[mac]['rollingHeight'][minDistIdx].append(y_height)

                                # State of the subject
                                # print(np.linalg.norm([x_vel, y_vel, z_vel]))
                                # if np.average(vitalStateParam[mac]['rollingVelY'][minDistIdx]) < -0.3 and np.average(vitalStateParam[mac]['rollingHeight'][minDistIdx]) > 1.1 and \
                                    # len(vitalStateParam[mac]['rollingHeight'][minDistIdx]) == 5 and np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5:
                                    # label_list.append(3)
                                    # count_subjectStationary = 0
                                    # periodStationary = 0
                                    # vital_dict['bedOccupancy'] = 1
                                    # vitalStateParam[mac]['periodStationary'] = 0
                                    # vitalStateParam[mac]['label_list'].append(2)

                                # elif np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5 and np.linalg.norm([x_vel, y_vel, z_vel]) <= 0.3:
                                if len(v_coord[trackIndices == trackId]) > 0:
                                  # if np.abs(x_pos) < 0.6 and np.abs(z_pos) < 0.6 and np.percentile(np.abs(v_coord[trackIndices == trackId]), [99]) <= 1:
                                  if np.abs(x_pos) < xPos_threshold and np.abs(z_pos) < zPos_threshold and distanceMoved < distanceMoved_threshold:
                                    # if np.abs(x_pos) < 0.8 and np.abs(z_pos) < 0.8 and np.percentile(v_coord, [99]) <= 0.3:
                                    # print("In Bed, Subject Stationary")
                                    vital_dict['bedOccupancy'] = 1
                                    # label_list.append(0)
                                    # count_subjectStationary += 1
                                    if vitalStateParam[mac]['prevTimeStationary'] == 0:
                                        vitalStateParam[mac]['prevTimeStationary'] = ts
                                    deltaTime = ts - vitalStateParam[mac]['prevTimeStationary']
                                    vitalStateParam[mac]['periodStationary'] = vitalStateParam[mac]['periodStationary'] + deltaTime
                                    vitalStateParam[mac]['prevTimeStationary'] = ts
                                    # print(vitalStateParam[mac]['periodStationary'])
                                    vitalStateParam[mac]['label_list'].append(1)

                                  # elif np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5 and np.linalg.norm([x_vel, y_vel, z_vel]) > 0.3:
                                  # elif np.abs(x_pos) < 0.6 and np.abs(z_pos) < 0.6 and np.percentile(np.abs(v_coord[trackIndices == trackId]), [99]) > 1:
                                  elif np.abs(x_pos) < xPos_threshold and np.abs(z_pos) < zPos_threshold:
                                    # elif np.abs(x_pos) < 0.8 and np.abs(z_pos) < 0.8 and np.percentile(v_coord, [99]) > 0.3:
                                    # print("In Bed, Subject Moving")
                                    vital_dict['bedOccupancy'] = 1
                                    vital_dict['inBedMoving'] = 1
                                    # label_list.append(1)
                                    # count_subjectStationary = 0
                                    vitalStateParam[mac]['periodStationary'] = 0
                                    vitalStateParam[mac]['label_list'].append(1)

                                  elif np.abs(x_pos) > 1.0 or np.abs(z_pos) > 1.0:
                                    # print("Out of Bed")
                                    vital_dict['bedOccupancy'] = 0
                                    # label_list.append(2)
                                    # count_subjectStationary = 0
                                    vitalStateParam[mac]['periodStationary'] = 0
                                    vitalStateParam[mac]['label_list'].append(0)

                                  if len(vitalStateParam[mac]['rollingHeight'][minDistIdx]) > 4:
                                    del vitalStateParam[mac]['rollingHeight'][minDistIdx][0]
                                    del vitalStateParam[mac]['rollingVelY'][minDistIdx][0]

                                elif np.abs(x_pos) < 0.5:
                                    vital_dict['bedOccupancy'] = 1

                                elif np.abs(x_pos) > 1.0:
                                    vital_dict['bedOccupancy'] = 0

                            # --------------------------------------------------------------------------------------------------
                            # --------------------------------------------------------------------------------------------------

                        # Remove unused tracker information and parameters
                        trackerInvalidIdx = np.arange(len(vitalStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[vitalStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            rollingVelY.pop(trackerInvalidIdx[Idx])
                            rollingHeight.pop(trackerInvalidIdx[Idx])
                        vitalStateParam[mac]['trackPos']  = vitalStateParam[mac]['trackPos'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackIDs'] = vitalStateParam[mac]['trackIDs'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackerInvalid'] = vitalStateParam[mac]['trackerInvalid'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackerInvalid'] = vitalStateParam[mac]['trackerInvalid'] + 1

                # if len(vitalStateParam[mac]['label_list']) >= 10:
                    # if statistics.mode(vitalStateParam[mac]['label_list']) == 2:
                        
                        # Publish alert via MQTT communication channel
                        # pubPayload = {"TIMESTAMP":ts, "URGENCY":2, "TYPE":3, "DETAILS":"IMMINENT BED EXIT"}
                        # jsonData = json.dumps(pubPayload)
                        # mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                    # vitalStateParam[mac]['label_list'] = []

                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    vitalStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']
                # time.sleep(0.01)  # Sampling frequency of 30 Hz
                
                # print(vitalStateParam[mac]['pandasDF'])
                # Time Series Data Aggregation
                
                if vitalStateParam[mac]['pandasDF'].empty:
                    # Append data frame
                    vitalStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp','bedOccupancy','breathRate','heartRate','inBedMoving','signOfLife','pointCloudDetected'])
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)

                elif (vital_dict['timeStamp'] - vitalStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:
                    # aggregate_dict = vitalStateParam[mac]['pandasDF'].agg({'timeStamp': ['mean'], 'bedOccupancy': 'mean',
                    #                                                        'breathRate': 'mean', 'heartRate': 'mean'})

                    # print(vitalStateParam[mac]['pandasDF'])
                    # aggregate_dict = aggregate_dict.to_dict('r')
                    # aggregate_dict = aggregate_dict[0]
                    # if str(aggregate_dict['bedOccupancy']) != 'nan':
                    #     for key, value in aggregate_dict.items():
                    #         if str(value)[0:3] == 'nan':
                    #             aggregate_dict[key] = None
                    #     # aggregate_dict['timeStamp'] = str(dt.fromtimestamp(float(aggregate_dict['timeStamp']), tz))[:23]
                    #     if aggregate_dict['bedOccupancy'] is not None:
                    #         aggregate_dict['bedOccupancy'] = bool(round(aggregate_dict['bedOccupancy']))
                    #     # json_string = json.dumps(aggregate_dict, indent=4)
                        
                    # else:
                    #     aggregate_dict = {}
                    #     aggregate_dict['timeStamp'] = vitalStateParam[mac]['pandasDF']['timeStamp'].agg('mean')
                    #     aggregate_dict['numSubjects'] = 0
                    #     aggregate_dict['bedOccupancy'] = False
                    #     # json_string = '{}'

                    aggregate_dict = {}
                    aggregate_dict['timeStamp'] = round(vitalStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                    aggregate_dict['bedOccupancy'] = vitalStateParam[mac]['pandasDF']['bedOccupancy'].mean(skipna=True)
                    aggregate_dict['breathRate'] = vitalStateParam[mac]['pandasDF']['breathRate'].mean(skipna=True)
                    aggregate_dict['heartRate'] = vitalStateParam[mac]['pandasDF']['heartRate'].mean(skipna=True)
                    aggregate_dict['inBedMoving'] = vitalStateParam[mac]['pandasDF']['inBedMoving'].mean(skipna=True)
                    aggregate_dict['signOfLife'] = vitalStateParam[mac]['pandasDF']['signOfLife'].mean(skipna=True)
                    aggregate_dict['pointCloudDetected'] = vitalStateParam[mac]['pandasDF']['pointCloudDetected'].mean(skipna=True)

                    if not math.isnan(aggregate_dict['bedOccupancy']):
                        aggregate_dict['bedOccupancy'] = bool(round(aggregate_dict['bedOccupancy']))
                    if not math.isnan(aggregate_dict['inBedMoving']):
                        aggregate_dict['inBedMoving'] = bool(round(aggregate_dict['inBedMoving']))
                    if not math.isnan(aggregate_dict['signOfLife']):
                        aggregate_dict['signOfLife'] = bool(round(aggregate_dict['signOfLife']))
                    if not math.isnan(aggregate_dict['pointCloudDetected']):
                        if aggregate_dict['pointCloudDetected'] > 0:
                            aggregate_dict['pointCloudDetected'] = 1
                        elif aggregate_dict['pointCloudDetected'] == 0:
                            aggregate_dict['pointCloudDetected'] = 0
                    else:
                        aggregate_dict['pointCloudDetected'] = None

                    for key, value in aggregate_dict.items():
                        if str(value)[0:3] == 'nan':
                            aggregate_dict[key] = None

                    dict_copy = copy.deepcopy(aggregate_dict)
                    my_list.append(dict_copy)
                    # print("JSON: ", json_string)

                    # Update the new data frame
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)
                    vitalStateParam[mac]['pandasDF'] = vitalStateParam[mac]['pandasDF'].iloc[-1:, :]
                else:
                    # Append data frame
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)

                # Write key-value dictionary to JSON file
                # json_string = json.dumps(vital_dict, indent=4)
                # json.dump(json_string, outputFile)
                # print(json_string)

            # ------------------------------------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------------------------------------

    if devicesTbl[mac]["TYPE"] == '1':
      if mac in wallStateParam:
        stateParam_sharedDict[mac] = wallStateParam[mac]
    elif devicesTbl[mac]["TYPE"] == '3':
      if mac in vitalStateParam:
        stateParam_sharedDict[mac] = vitalStateParam[mac]

    pubPayload = {
            "DATA": my_list,
            "TYPE": radarType
        }
    processDataQueue.put(pubPayload)

    """
    try: 
        print("my_list: ", my_list)
        pubPayload = {
            "DATA": my_list
        }
        op = len(pubPayload["DATA"])
        if len(pubPayload["DATA"]) > 0:
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            print(f"on message {op}", radarType)
        
            if radarType == 'wall':
                pubPayload["TYPE"]="WALL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/"+mac+"/DATA/WALL/JSON", jsonData)
                print(result)
            elif radarType == 'ceil':
                pubPayload["TYPE"]="CEIL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/CEIL/JSON", jsonData)
                print(result)
            elif radarType == 'vital':
                pubPayload["TYPE"]="VITAL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/VITAL/JSON", jsonData)
                print(result)
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")              
            time.sleep(0.1)
            # dataBuffer.append(jsonData)
            dataBufferQueue.put(jsonData)
    except Exception as e:
        print(e)
    """

def publishProcessData(processDataQueue, dataBufferQueue):

  while 1: 
    while processDataQueue.empty():
        time.sleep(0.1)
    pubPayload = processDataQueue.get()
    radarType = pubPayload["TYPE"]

    try: 
        print("my_list: ", pubPayload["DATA"])
        op = len(pubPayload["DATA"])
        if len(pubPayload["DATA"]) > 0:

            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            print(f"on message {op}", radarType)
        
            if radarType == 'wall':
                pubPayload["TYPE"]="WALL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/"+mac+"/DATA/WALL/JSON", jsonData)
                print(result)
            elif radarType == 'ceil':
                pubPayload["TYPE"]="CEIL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/CEIL/JSON", jsonData)
                print(result)
            elif radarType == 'vital':
                pubPayload["TYPE"]="VITAL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/VITAL/JSON", jsonData)
                print(result)
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")              
            time.sleep(0.1)
            # dataBuffer.append(jsonData)
            dataBufferQueue.put(jsonData)
    except Exception as e:
        print(e)
    

def decode_process_publish_wall(stateParamQueue, mac, data, wallStateParam, mqttc, algoCfg, devicesTbl):

    my_list = []
    # print("algorithm configuration: ", algoCfg)
    # for x in data:
    print(len(data.items()))
    # print(sharedList)
    # wallStateParam = sharedList[0]
    # print(wallStateParam)
    for ts_str, byteAD in data.items():
        print("parsing data")
        try:
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        if ts == 0:
            continue

        # if len(byteAD) > 52:
        if len(byteAD) > 0:
            # Error happens occasionally when decoding the raw data frame,
            # may require error analysis in future to find out the actual cause.
            try:
                outputDict = parseStandardFrame(byteAD)
            except:
                outputDict = None
                continue
            print(mac)
            # print(byteAD)
            # print(outputDict)
            # --------------------------------- Wall-Mounted Radar Tracking and Posture Analysis -------------------------------
            # ------------------------------------------------------------------------------------------------------------------
            DEVICE = devicesTbl[mac]
            if DEVICE["TYPE"] == '1':
                radarType = 'wall'
            elif DEVICE["TYPE"] == '2':
                radarType = 'ceil'
            elif DEVICE["TYPE"] == '3':
                radarType = 'vital'
            xShift = DEVICE["DEPLOY_X"]
            yShift = DEVICE["DEPLOY_Y"]
            zShift = DEVICE["DEPLOY_Z"] 
            rotXDegree = DEVICE["ROT_X"]
            rotYDegree = DEVICE["ROT_Y"]
            rotZDegree = DEVICE["ROT_Z"]

            if "fall_deltaZHeight_" + mac in algoCfg["DATA"]:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight_"+mac]
            else:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight"]

            if "fall_deltaZPos_" + mac in algoCfg["DATA"]:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos_"+mac]
            else:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos"]

            if "fall_bodyWidth_" + mac in algoCfg["DATA"]:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth_"+mac]
            else:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth"]

            if "fall_averageHeight_" + mac in algoCfg["DATA"]:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight_"+mac]
            else:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight"]

            if "fall_minZVel_" + mac in algoCfg["DATA"]:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel_"+mac]
            else:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel"]

            if "fall_numFrames_" + mac in algoCfg["DATA"]:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames_"+mac])
            else:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames"])

            if "vital_periodStationary_" + mac in algoCfg["DATA"]:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary_"+mac]
            else:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary"]

            if "vital_distanceMoved_" + mac in algoCfg["DATA"]:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved_"+mac]
            else:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved"]

            if "vital_xPos_" + mac in algoCfg["DATA"]:
                xPos_threshold = algoCfg["DATA"]["vital_xPos_"+mac]
            else:
                xPos_threshold = algoCfg["DATA"]["vital_xPos"]

            if "vital_zPos_" + mac in algoCfg["DATA"]:
                zPos_threshold = algoCfg["DATA"]["vital_zPos_"+mac]
            else:
                zPos_threshold = algoCfg["DATA"]["vital_zPos"]

            if "aggregatePeriod_" + mac in algoCfg["DATA"]:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod_"+mac]
            else:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod"]

            if radarType == 'wall':
                # global wallStateParam

                if mac not in wallStateParam:
                    wallStateParam[mac] = {}
                    wallStateParam[mac]['timeNow'] = 0
                    wallStateParam[mac]['multi_frame_count'] = 2
                    wallStateParam[mac]['label_state'] = ['Moving', 'Upright', 'Laying', 'Fall', 'None', 'Social']

                # Read Radar Setup from Database
                # xShift, yShift, zShift, rotXDegree, rotYDegree, rotZDegree = readRadarSetup(mac)

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                wallStateParam[mac]['radar_coord'] = radar_coord

                # Radar Elevation Angle of Rotation, +ve Anti-Clockwise
                # rotXDegree = DEVICE["ROT_X"]
                elevRadian = rotXDegree * np.pi / 180  # Angle in Radian
                rotXMat = np.asarray([[1, 0, 0], \
                                      [0, np.cos(elevRadian), -np.sin(elevRadian)], \
                                      [0, np.sin(elevRadian), np.cos(elevRadian)]])  # Rotation Matrix
                wallStateParam[mac]['rotXMat'] = rotXMat

                # Radar Rotation about y-axis, +ve Anti-Clockwise
                # rotYDegree = DEVICE["ROT_Y"]
                rotYRadian = rotYDegree * np.pi / 180  # Angle in Radian
                rotYMat = np.asarray([[np.cos(rotYRadian), 0, np.sin(rotYRadian)], [0, 1, 0],
                                      [-np.sin(rotYRadian), 0, np.cos(rotYRadian)]])  # Rotation Matrix
                wallStateParam[mac]['rotYMat'] = rotYMat

                # Radar Azimuth Angle of Rotation, +ve Anti-Clockwise
                # rotZDegree = DEVICE["ROT_Z"]
                azimuthRadian = rotZDegree * np.pi / 180  # Angle in Radian
                rotZMat = np.asarray([[np.cos(azimuthRadian), -np.sin(azimuthRadian), 0], \
                                      [np.sin(azimuthRadian), np.cos(azimuthRadian), 0], \
                                      [0, 0, 1]])  # Rotation Matrix
                wallStateParam[mac]['rotZMat'] = rotZMat

                # Radar Time Stamp
                deltaT = ts - wallStateParam[mac]['timeNow']
                wallStateParam[mac]['timeNow'] = ts

                # Parameters Re-Initialization if Time Interval between Consecutive Data Frames Larger than Certain Threshold
                # For Robust Analytics with Data Frames / Packets Drop

                # print(deltaT)
                if deltaT > 100:
                    wallStateParam[mac]['x0'] = np.nan
                    wallStateParam[mac]['y0'] = np.nan
                    wallStateParam[mac]['z0'] = np.nan
                    wallStateParam[mac]['timeStamp_stationary'] = np.nan
                    wallStateParam[mac]['period_stationary'] = np.nan
                    wallStateParam[mac]['timeStamp_lastSignOfLife'] = np.nan
                    wallStateParam[mac]['period_noSignOfLife'] = np.nan
                    wallStateParam[mac]['x_coord_multi'] = []
                    wallStateParam[mac]['y_coord_multi'] = []
                    wallStateParam[mac]['z_coord_multi'] = []
                    wallStateParam[mac]['rollingX'] = []
                    wallStateParam[mac]['rollingY'] = []
                    wallStateParam[mac]['rollingZ'] = []
                    wallStateParam[mac]['rollingZVel'] = []
                    wallStateParam[mac]['minZVel'] = []
                    wallStateParam[mac]['rollingHeight'] = []
                    wallStateParam[mac]['averageX'] = []
                    wallStateParam[mac]['averageY'] = []
                    wallStateParam[mac]['averageZ'] = []
                    wallStateParam[mac]['averageHeight'] = []
                    wallStateParam[mac]['labelCount'] = []
                    wallStateParam[mac]['labelGuess'] = []
                    wallStateParam[mac]['trackPos'] = np.zeros((0, 3))  # tracker position
                    wallStateParam[mac]['trackVelocity'] = np.zeros((0, 3))  # tracker velocity
                    wallStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    wallStateParam[mac]['previous_pointClouds'] = np.zeros((0, 7))  # previous point clouds
                    wallStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    wallStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp', 'trackIndex', 'numSubjects', 'roomOccupancy',
                                                                            'posX', 'posY', 'posZ', 'velX', 'velY', 'velZ', 'accX', 'accY', 'accZ', 
                                                                            'bodyHeight', 'bodyWidth', 'state', 'kidOrAdult', 'signOfLife', 'pointCloudDetected'])

                # Read parsed data from radar output dictionary
                # Radar Trackers' Data Extraction
                if outputDict is not None:
                  if 'numDetectedTracks' in outputDict:
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()

                    # Decode 3D People Counting Target List TLV
                    # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                    # 3D Struct format
                    # uint32_t     tid;     /*! @brief   tracking ID */
                    # float        posX;    /*! @brief   Detected target X coordinate, in m */
                    # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                    # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                    # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                    # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                    # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                    # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                    # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                    # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                    # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                    # float        g;
                    # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                    trackData = outputDict['trackData']

                    # if numTracks == 1:

                    #     # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                    #     trackId = trackData[0, 0]
                    #     x_pos = trackData[0, 1]
                    #     y_pos = trackData[0, 2]
                    #     z_pos = trackData[0, 3]
                    #     x_vel = trackData[0, 4]
                    #     y_vel = trackData[0, 5]
                    #     z_vel = trackData[0, 6]
                    #     x_acc = trackData[0, 7]
                    #     y_acc = trackData[0, 8]
                    #     z_acc = trackData[0, 9]

                    #     # Tracker polar coordinates
                    #     trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                    #     trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                    #     trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                    #     trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                        # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                        # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                        # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                        # trackerElevationVelocity
                        # print(trackerRange, trackerAzimuth)

                    #     # Rotation of tracker's position and velocity coordinates
                    #     [x_pos, y_pos, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_pos, y_pos, 1])
                    #     [x_vel, y_vel, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_vel, y_vel, 1])
                    #     [x_acc, y_acc, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_acc, y_acc, 1])
                    #     [dum, y_pos, z_pos] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_pos, z_pos])
                    #     [dum, y_vel, z_vel] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_vel, z_vel])
                    #     [dum, y_acc, z_acc] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_acc, z_acc])
                    #     [x_pos, dum, z_pos] = np.matmul(wallStateParam[mac]['rotYMat'], [x_pos, 1, z_pos])
                    #     [x_vel, dum, z_vel] = np.matmul(wallStateParam[mac]['rotYMat'], [x_vel, 1, z_vel])
                    #     [x_acc, dum, z_acc] = np.matmul(wallStateParam[mac]['rotYMat'], [x_acc, 1, z_acc])

                    #     # Horizontal shifting of tracker's position coordinates
                    #     x_pos = x_pos + wallStateParam[mac]['radar_coord'][0]
                    #     y_pos = y_pos + wallStateParam[mac]['radar_coord'][1]
                        # z_pos = z_pos + wallStateParam[mac]['radar_coord'][2]

                        # Tracker velocity (normalized) direction
                        # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                        # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                        # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                    #     wall_Dict['posX'] = x_pos
                    #     wall_Dict['posY'] = y_pos
                    #     wall_Dict['posZ'] = z_pos
                    #     wall_Dict['velX'] = x_vel
                    #     wall_Dict['velY'] = y_vel
                    #     wall_Dict['velZ'] = z_vel
                    #     wall_Dict['accX'] = x_acc
                    #     wall_Dict['accY'] = y_acc
                    #     wall_Dict['accZ'] = z_acc

                    # Read parsed data from radar output dictionary
                    # Radar Point Clouds + Trackers' Data Extraction and Processing
                    if len(wallStateParam[mac]['previous_pointClouds']) >= 0 and 'trackIndexes' in outputDict:
                      trackIndices = outputDict['trackIndexes']

                      if numTracks > 0 and len(wallStateParam[mac]['previous_pointClouds']) >= 0 and \
                        len(wallStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        wallStateParam[mac]['previous_pointClouds'][:,6] = trackIndices
                        snr = wallStateParam[mac]['previous_pointClouds'][:,4]
                        wallStateParam[mac]['previous_pointClouds'] = wallStateParam[mac]['previous_pointClouds'][snr > 7,:]
                        trackIndices = trackIndices[snr > 7]
                        x_coord = wallStateParam[mac]['previous_pointClouds'][:,0]
                        y_coord = wallStateParam[mac]['previous_pointClouds'][:,1]
                        z_coord = wallStateParam[mac]['previous_pointClouds'][:,2]
                        v_coord = wallStateParam[mac]['previous_pointClouds'][:,3]
                        points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Radar Point Clouds Rotation about the Z axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotZMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 0:2] = points_dum[:, 0:2]

                        # Radar Point Clouds Rotation about the X axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotXMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 1:] = points_dum[:, 1:]

                        # Radar Point Clouds Rotation about the Y axis
                        points_dum = points
                        points_dum = np.matmul(wallStateParam[mac]['rotYMat'], np.transpose(points_dum))
                        points_dum = np.transpose(points_dum)
                        points[:, 0] = points_dum[:, 0]
                        points[:, 2] = points_dum[:, 2]

                        # Shifting of Radar Point Clouds' Coordinates
                        points[:, 0] = points[:, 0] + wallStateParam[mac]['radar_coord'][0]
                        points[:, 1] = points[:, 1] + wallStateParam[mac]['radar_coord'][1]
                        # points[:, 2] = points[:, 2] + wallStateParam[mac]['radar_coord'][2]
                       
                        x_coord = points[:, 0]
                        y_coord = points[:, 1]
                        z_coord = points[:, 2]

                        # Process individual tracker's data for Posture Analytics
                        for trackIdx in range(numTracks):

                            print("number of tracks = ", numTracks)

                            # Time Stamp
                            wall_Dict = {}
                            wall_Dict['timeStamp'] = ts

                            # Point Cloud Detected ?
                            if 'pointCloud' in outputDict:
                              if len(outputDict['pointCloud']) > 0:
                                wall_Dict['pointCloudDetected'] = 1
                              else:
                                wall_Dict['pointCloudDetected'] = 0 

                            # Track Index
                            trackId = trackData[trackIdx, 0]
                            wall_Dict['trackIndex'] = trackId
                            # if np.isnan(trackId):
                            #     continue

                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]
                            x_acc = trackData[trackIdx, 7]
                            y_acc = trackData[trackIdx, 8]
                            z_acc = trackData[trackIdx, 9]

                            # Tracker polar coordinates
                            trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2)  # tracker range projected onto the x-y plane
                            trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Rotation of tracker's position and velocity coordinates
                            [x_pos, y_pos, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_pos, y_pos, 1])
                            [x_vel, y_vel, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_vel, y_vel, 1])
                            [x_acc, y_acc, dum] = np.matmul(wallStateParam[mac]['rotZMat'], [x_acc, y_acc, 1])
                            [dum, y_pos, z_pos] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_pos, z_pos])
                            [dum, y_vel, z_vel] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_vel, z_vel])
                            [dum, y_acc, z_acc] = np.matmul(wallStateParam[mac]['rotXMat'], [1, y_acc, z_acc])
                            [x_pos, dum, z_pos] = np.matmul(wallStateParam[mac]['rotYMat'], [x_pos, 1, z_pos])
                            [x_vel, dum, z_vel] = np.matmul(wallStateParam[mac]['rotYMat'], [x_vel, 1, z_vel])
                            [x_acc, dum, z_acc] = np.matmul(wallStateParam[mac]['rotYMat'], [x_acc, 1, z_acc])

                            # Horizontal shifting of tracker's position coordinates
                            x_pos = x_pos + wallStateParam[mac]['radar_coord'][0]
                            y_pos = y_pos + wallStateParam[mac]['radar_coord'][1]
                            # z_pos = z_pos + wallStateParam[mac]['radar_coord'][2]

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos, y_pos, z_pos]], (len(trackPos), 1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # ---------------- Posture Estimation ----------------
                            # ----------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(wallStateParam[mac]['trackPos']) == 0 or np.sum(wallStateParam[mac]['trackIDs'] == trackId) == 0:
                                wallStateParam[mac]['trackIDs'] = np.concatenate((wallStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                wallStateParam[mac]['trackPos'] = np.concatenate((wallStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                wallStateParam[mac]['trackVelocity'] = np.concatenate((wallStateParam[mac]['trackVelocity'], [[x_vel, y_vel, z_vel]]), axis=0)
                                wallStateParam[mac]['trackerInvalid'] = np.concatenate((wallStateParam[mac]['trackerInvalid'], [0]), axis=0)

                                # Append Parameters for positional change detection and dimensional analysis for posture analytics
                                wallStateParam[mac]['rollingX'].append([])
                                wallStateParam[mac]['rollingY'].append([])
                                wallStateParam[mac]['rollingZ'].append([])
                                wallStateParam[mac]['rollingZVel'].append([])
                                wallStateParam[mac]['minZVel'].append([])
                                wallStateParam[mac]['rollingHeight'].append([])
                                wallStateParam[mac]['averageX'].append([])
                                wallStateParam[mac]['averageY'].append([])
                                wallStateParam[mac]['averageZ'].append([])
                                wallStateParam[mac]['averageHeight'].append([])
                                wallStateParam[mac]['x_coord_multi'].append([])
                                wallStateParam[mac]['y_coord_multi'].append([])
                                wallStateParam[mac]['z_coord_multi'].append([])
                                wallStateParam[mac]['labelCount'].append(4)
                                wallStateParam[mac]['labelGuess'].append(4)

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(wallStateParam[mac]['trackIDs']))[wallStateParam[mac]['trackIDs'] == trackId][0]

                                # Update tracker information
                                wallStateParam[mac]['trackerInvalid'][minDistIdx] = wallStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                wallStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                wallStateParam[mac]['trackVelocity'][minDistIdx] = [x_vel, y_vel, z_vel]

                                # Sign Of life
                                if numTracks == 1:
                                    if math.isnan(wallStateParam[mac]['x0']):
                                        wallStateParam[mac]['x0'] = x_pos
                                        wallStateParam[mac]['y0'] = y_pos
                                        wallStateParam[mac]['z0'] = z_pos
                                    else:
                                        distanceMoved = np.abs(wallStateParam[mac]['x0'] - x_pos) + np.abs(wallStateParam[mac]['y0'] - y_pos) + np.abs(wallStateParam[mac]['z0'] - z_pos)
                                        wallStateParam[mac]['x0'] = x_pos
                                        wallStateParam[mac]['y0'] = y_pos
                                        wallStateParam[mac]['z0'] = z_pos
                                        if distanceMoved > 0.1 or math.isnan(wallStateParam[mac]['timeStamp_stationary']):
                                            wallStateParam[mac]['timeStamp_stationary'] = ts
                                        else:
                                            
                                            if len(x_coord[trackIndices == trackId]) > 0 or math.isnan(wallStateParam[mac]['timeStamp_lastSignOfLife']):
                                                wallStateParam[mac]['timeStamp_lastSignOfLife'] = ts
                                            else:
                                                wallStateParam[mac]['period_noSignOfLife'] = ts - wallStateParam[mac]['timeStamp_lastSignOfLife']
                                                wallStateParam[mac]['period_stationary'] = wallStateParam[mac]['timeStamp_lastSignOfLife'] - wallStateParam[mac]['timeStamp_stationary']
                                                if wallStateParam[mac]['period_noSignOfLife'] > 60 and wallStateParam[mac]['period_stationary'] > 60:
                                                    wall_Dict['signOfLife'] = 0
                                                    
                                                    # Publish alert via MQTT communication channel
                                                    # pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":1, "DETAILS":"NOSIGNOFLIFE"}
                                                    # jsonData = json.dumps(pubPayload)
                                                    # mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                                else:
                                                    wall_Dict['signOfLife'] = 1

                                # Multi-Frame Aggregation
                                wallStateParam[mac]['x_coord_multi'][minDistIdx].append(x_coord[trackIndices == trackId])
                                wallStateParam[mac]['y_coord_multi'][minDistIdx].append(y_coord[trackIndices == trackId])
                                wallStateParam[mac]['z_coord_multi'][minDistIdx].append(z_coord[trackIndices == trackId])
                                if len(wallStateParam[mac]['x_coord_multi'][minDistIdx]) > wallStateParam[mac]['multi_frame_count']:
                                    wallStateParam[mac]['x_coord_multi'][minDistIdx].pop(0)
                                    wallStateParam[mac]['y_coord_multi'][minDistIdx].pop(0)
                                    wallStateParam[mac]['z_coord_multi'][minDistIdx].pop(0)

                                # Rolling Average
                                wallStateParam[mac]['rollingX'][minDistIdx].append(x_pos)
                                wallStateParam[mac]['rollingY'][minDistIdx].append(y_pos)
                                wallStateParam[mac]['rollingZ'][minDistIdx].append(z_pos)
                                wallStateParam[mac]['rollingZVel'][minDistIdx].append(z_vel)

                                if len(wallStateParam[mac]['rollingX'][minDistIdx]) >= 10:
                                    wallStateParam[mac]['averageX'][minDistIdx].append(np.average(wallStateParam[mac]['rollingX'][minDistIdx]))
                                    wallStateParam[mac]['averageY'][minDistIdx].append(np.average(wallStateParam[mac]['rollingY'][minDistIdx]))
                                    wallStateParam[mac]['averageZ'][minDistIdx].append(np.average(wallStateParam[mac]['rollingZ'][minDistIdx]))
                                    del wallStateParam[mac]['rollingX'][minDistIdx][0]
                                    del wallStateParam[mac]['rollingY'][minDistIdx][0]
                                    del wallStateParam[mac]['rollingZ'][minDistIdx][0]

                                if len(wallStateParam[mac]['rollingZVel'][minDistIdx]) >= numFrames_threshold:
                                    wallStateParam[mac]['minZVel'][minDistIdx].append(np.percentile(wallStateParam[mac]['rollingZVel'][minDistIdx], 5))
                                    del wallStateParam[mac]['rollingZVel'][minDistIdx][0]
                                    if len(wallStateParam[mac]['minZVel'][minDistIdx]) >= 10:
                                        del wallStateParam[mac]['minZVel'][minDistIdx][0]

                                if len(wallStateParam[mac]['averageX'][minDistIdx]) > numFrames_threshold:
                                    deltaX = wallStateParam[mac]['averageX'][minDistIdx][-1] - wallStateParam[mac]['averageX'][minDistIdx][-10]
                                    deltaY = wallStateParam[mac]['averageY'][minDistIdx][-1] - wallStateParam[mac]['averageY'][minDistIdx][-10]
                                    deltaZ = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-10]
                                    # deltaZPos = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-47]
                                    deltaZPos = wallStateParam[mac]['averageZ'][minDistIdx][-1] - wallStateParam[mac]['averageZ'][minDistIdx][-numFrames_threshold]
                                    del wallStateParam[mac]['averageX'][minDistIdx][0]
                                    del wallStateParam[mac]['averageY'][minDistIdx][0]
                                    del wallStateParam[mac]['averageZ'][minDistIdx][0]

                                    deltaDisp = np.sqrt(deltaX ** 2 + deltaY ** 2 + deltaZ ** 2)
                                    deltaDist = np.sqrt(deltaX ** 2 + deltaY ** 2)

                                    # Disable posture estimation if number of subjects > 1 or subject's range > 5m, or subject's
                                    # azimuth or elevation angle > 50 degrees.
                                    # if numTracks > 1:
                                    #     wallStateParam[mac]['labelCount'][minDistIdx] = 5
                                    #     wallStateParam[mac]['labelGuess'][minDistIdx] = 5
                                    #     wall_Dict['state'] = 5

                                    # if trackerRange > 10 or np.abs(trackerAzimuth) > 50 or np.abs(trackerElevation) > 40:
                                    #     wallStateParam[mac]['labelCount'][minDistIdx] = 4
                                    #     wallStateParam[mac]['labelGuess'][minDistIdx] = 4

                                    # elif len(x_coord[trackIndices == trackId]) > 10:
                                    # elif numTracks == 1:

                                    # elif deltaDisp > 0.05 and len(x_coord[trackIndices == trackId]) > 5:
                                    if len(x_coord[trackIndices == trackId]) > 5:
                                        x_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['x_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        y_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['y_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_dim = np.diff(np.percentile(np.concatenate(wallStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [1, 99]))
                                        z_height = np.percentile(np.concatenate(wallStateParam[mac]['z_coord_multi'][minDistIdx][:], axis=0), [99])
                                        z_height = z_height + wallStateParam[mac]['radar_coord'][2]
                                        body_width = np.sqrt(x_dim ** 2 + y_dim ** 2)
                                        # print(z_height, z_dim, body_width)
                                        wall_Dict['bodyHeight'] = z_dim[0]
                                        wall_Dict['bodyWidth'] = body_width[0]

                                        wallStateParam[mac]['rollingHeight'][minDistIdx].append(z_height)

                                        if len(wallStateParam[mac]['rollingHeight'][minDistIdx]) == 10:
                                            wallStateParam[mac]['averageHeight'][minDistIdx].append(np.average(wallStateParam[mac]['rollingHeight'][minDistIdx]))
                                            del(wallStateParam[mac]['rollingHeight'][minDistIdx][0])

                                        # if len(wallStateParam[mac]['averageHeight'][minDistIdx]) == 47:
                                        if len(wallStateParam[mac]['averageHeight'][minDistIdx]) == numFrames_threshold:
                                          # deltaHeight = wallStateParam[mac]['averageHeight'][minDistIdx][-1] - wallStateParam[mac]['averageHeight'][minDistIdx][-47]
                                          deltaHeight = wallStateParam[mac]['averageHeight'][minDistIdx][-1] - wallStateParam[mac]['averageHeight'][minDistIdx][-numFrames_threshold]
                                          del(wallStateParam[mac]['averageHeight'][minDistIdx][0])

                                          if deltaHeight < deltaZHeight_threshold and deltaZPos < deltaZPos_threshold and body_width > bodyWidth_threshold and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < averageHeight_threshold and wallStateParam[mac]['minZVel'][minDistIdx][-1] < minZVel_threshold:
                                          # if deltaHeight < -1 and deltaZPos < -1 and body_width > 1 and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < 0.8: # and z_height < 1.0 and ((body_width) / (z_dim + 0.2)) > 1.0:
                                          # if deltaHeight < -0.8 and deltaZPos < -0.8 and body_width > 0.8 and wallStateParam[mac]['averageHeight'][minDistIdx][-1] < 0.8: # and ((body_width) / (wallStateParam[mac]['averageHeight'][minDistIdx][-1])) > 1.5:
                                            # print('Fall')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 3
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            wall_Dict['state'] = 3

                                            # Publish alert via MQTT communication channel
                                            pubPayload = {"TIMESTAMP":ts, "URGENCY":3, "TYPE":1, "DETAILS":"FALL"}
                                            jsonData = json.dumps(pubPayload)
                                            mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                                          elif deltaDist > 0.3:
                                            # print('Moving')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 0
                                            wall_Dict['state'] = 0

                                            # Adult and Kid Differentiation
                                            if z_height > 1.5 and z_height < 2.0 and body_width < 1.0:
                                                wall_Dict['kidOrAdult'] = 1
                                            elif z_height > 0.4 and z_height < 1.0 and body_width < 0.5:
                                                wall_Dict['kidOrAdult'] = 0

                                          elif body_width > 1 and z_height < 1.5 and ((body_width) / (z_dim + 0.2)) > 1.5:
                                            # print('Laying')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 2
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 2
                                            wall_Dict['state'] = 2

                                          elif z_dim > 0.5 and body_width > 0.3 and z_height > 0.5 and ((z_dim) / (body_width + 0.0001)) > 1.2:
                                            # print('Upright')
                                            wallStateParam[mac]['labelCount'][minDistIdx] = 1
                                            wallStateParam[mac]['labelGuess'][minDistIdx] = 1
                                            wall_Dict['state'] = 1

                                          else:
                                            wallStateParam[mac]['labelCount'][minDistIdx] = wallStateParam[mac]['labelGuess'][minDistIdx]
                                            # wall_Dict['state'] = wallStateParam[mac]['label_state'][wallStateParam[mac]['labelCount'][minDistIdx]]
                                            wall_Dict['state'] = wallStateParam[mac]['labelCount'][minDistIdx]

                                # ----------------------------------------------------
                                # ----------------------------------------------------

                            # Tracker position, velocity, and acceleration
                            wall_Dict['posX'] = x_pos
                            wall_Dict['posY'] = y_pos
                            wall_Dict['posZ'] = z_pos
                            wall_Dict['velX'] = x_vel
                            wall_Dict['velY'] = y_vel
                            wall_Dict['velZ'] = z_vel
                            wall_Dict['accX'] = x_acc
                            wall_Dict['accY'] = y_acc
                            wall_Dict['accZ'] = z_acc

                            # Room Occupancy Detection
                            wall_Dict['numSubjects'] = numTracks
                            if numTracks > 0:
                                wall_Dict['roomOccupancy'] = True
                            elif numTracks == 0:
                                wall_Dict['roomOccupancy'] = False

                            # Time Series Data Aggregation                
                            if wallStateParam[mac]['pandasDF'].empty:
                                
                                # Append data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                            elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                                # print(wallStateParam[mac]['pandasDF']['trackIndex'].unique())
                                if len(wallStateParam[mac]['pandasDF']['trackIndex'].unique()) > 0:
                                  
                                  for trackInd in wallStateParam[mac]['pandasDF']['trackIndex'].unique():
                                    
                                    if np.isnan(trackInd):
                                        continue

                                    pandasDF_dum = wallStateParam[mac]['pandasDF'].loc[wallStateParam[mac]['pandasDF']['trackIndex'] == trackInd]

                                    aggregate_dict = {}
                                    aggregate_dict['timeStamp'] = round(pandasDF_dum['timeStamp'].mean(skipna=True),2)
                                    aggregate_dict['numSubjects'] = pandasDF_dum['numSubjects'].mean(skipna=True)
                                    aggregate_dict['roomOccupancy'] = pandasDF_dum['roomOccupancy'].mean(skipna=True)
                                    aggregate_dict['trackIndex'] = int(trackInd)
                                    aggregate_dict['posX'] = pandasDF_dum['posX'].mean(skipna=True)
                                    aggregate_dict['posY'] = pandasDF_dum['posY'].mean(skipna=True)
                                    aggregate_dict['posZ'] = pandasDF_dum['posZ'].mean(skipna=True)
                                    aggregate_dict['velX'] = pandasDF_dum['velX'].mean(skipna=True)
                                    aggregate_dict['velY'] = pandasDF_dum['velY'].mean(skipna=True)
                                    aggregate_dict['velZ'] = pandasDF_dum['velZ'].mean(skipna=True)
                                    aggregate_dict['accX'] = pandasDF_dum['accX'].max(skipna=True)
                                    aggregate_dict['accY'] = pandasDF_dum['accY'].max(skipna=True)
                                    aggregate_dict['accZ'] = pandasDF_dum['accZ'].max(skipna=True)
                                    aggregate_dict['bodyHeight'] = pandasDF_dum['bodyHeight'].mean(skipna=True)
                                    aggregate_dict['bodyWidth'] = pandasDF_dum['bodyWidth'].mean(skipna=True)

                                    if not pandasDF_dum['state'].mode(dropna=True).empty:
                                        aggregate_dict['state'] = pandasDF_dum['state'].mode(dropna=True).iloc[0]
                                    else:
                                        aggregate_dict['state'] = np.nan
                                    aggregate_dict['kidOrAdult'] = pandasDF_dum['kidOrAdult'].mean(skipna=True)
                                    aggregate_dict['signOfLife'] = pandasDF_dum['signOfLife'].mean(skipna=True)
                                    aggregate_dict['pointCloudDetected'] = pandasDF_dum['pointCloudDetected'].mean(skipna=True)

                                    # if aggregate_dict['state'].dropna().empty:
                                    # print(aggregate_dict)
                                    if math.isnan(aggregate_dict['state']):
                                        aggregate_dict['state'] = None
                                    elif pandasDF_dum['state'].isin([3]).sum() > 0:
                                        aggregate_dict['state'] = 'Fall'
                                    # elif aggregate_dict['state'].isin([4]).sum() == 0:
                                    elif aggregate_dict['state'] != 4:
                                        aggregate_dict['state'] = wallStateParam[mac]['label_state'][int(aggregate_dict['state'])]
                                    else:
                                        aggregate_dict['state'] = None

                                    # if aggregate_dict['kidOrAdult'].dropna().empty:
                                    if math.isnan(aggregate_dict['kidOrAdult']):
                                        aggregate_dict['kidOrAdult'] = None
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 0:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 0:
                                        aggregate_dict['kidOrAdult'] = 'Kid'
                                    # elif int(round(aggregate_dict['kidOrAdult'].iloc[0])) == 1:
                                    elif int(round(aggregate_dict['kidOrAdult'])) == 1:
                                        aggregate_dict['kidOrAdult'] = 'Adult'

                                    # aggregate_dict = aggregate_dict.to_dict('r')
                                    # if aggregate_dict:
                                    # print("YYYYYYYYY")
                                    # aggregate_dict = aggregate_dict[0]
                                    if not math.isnan(aggregate_dict['numSubjects']):
                                        aggregate_dict['numSubjects'] = int(round(aggregate_dict['numSubjects']))
                                    if not math.isnan(aggregate_dict['roomOccupancy']):
                                        aggregate_dict['roomOccupancy'] = bool(round(aggregate_dict['roomOccupancy']))
                                    if not math.isnan(aggregate_dict['signOfLife']):
                                      # aggregate_dict['signOfLife'] = bool(round(aggregate_dict['signOfLife']))
                                      if aggregate_dict['signOfLife'] > 0:
                                        aggregate_dict['signOfLife'] = 1
                                      elif aggregate_dict['signOfLife'] == 0:
                                        aggregate_dict['signOfLife'] = 0
                                    if not math.isnan(aggregate_dict['pointCloudDetected']):
                                      if aggregate_dict['pointCloudDetected'] > 0:
                                        aggregate_dict['pointCloudDetected'] = 1
                                      elif aggregate_dict['pointCloudDetected'] == 0:
                                        aggregate_dict['pointCloudDetected'] = 0

                                    for key, value in aggregate_dict.items():
                                        if str(value)[0:3] == 'nan':
                                            aggregate_dict[key] = None

                                    # print(aggregate_dict['state'])
                                    dict_copy = copy.deepcopy(aggregate_dict)
                                    my_list.append(dict_copy)
                                    # print(json_string)

                                # Update the new data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                                wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                            else:
            
                                # Append data frame
                                wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                                # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                                # print(wallStateParam)

                        # Remove unused trackers' information and parameters
                        trackerInvalidIdx = np.arange(len(wallStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[wallStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            wallStateParam[mac]['x_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['y_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['z_coord_multi'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingX'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingY'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingZ'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingZVel'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['minZVel'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['rollingHeight'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageX'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageY'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageZ'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['averageHeight'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['labelCount'].pop(trackerInvalidIdx[Idx])
                            wallStateParam[mac]['labelGuess'].pop(trackerInvalidIdx[Idx])

                        wallStateParam[mac]['trackPos'] = wallStateParam[mac]['trackPos'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackVelocity'] = wallStateParam[mac]['trackVelocity'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackIDs'] = wallStateParam[mac]['trackIDs'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackerInvalid'] = wallStateParam[mac]['trackerInvalid'][wallStateParam[mac]['trackerInvalid'] == 0]
                        wallStateParam[mac]['trackerInvalid'] = wallStateParam[mac]['trackerInvalid'] + 1

                  else:
                    
                    wall_Dict = {}
                    wall_Dict['timeStamp'] = ts

                    # Point Cloud Detected ?
                    if 'pointCloud' in outputDict:
                      if len(outputDict['pointCloud']) > 0:
                        wall_Dict['pointCloudDetected'] = 1
                      else:
                        wall_Dict['pointCloudDetected'] = 0                    

                    # Time Series Data Aggregation 
                    if "pandasDF" in wallStateParam[mac]:
                        if wallStateParam[mac]['pandasDF'].empty:
                            # Append data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)

                        elif (wall_Dict['timeStamp'] - wallStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:

                            aggregate_dict = {}
                            aggregate_dict['timeStamp'] = round(wallStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                            aggregate_dict['numSubjects'] = 0
                            aggregate_dict['roomOccupancy'] = False
                            aggregate_dict['trackIndex'] = None
                            aggregate_dict['posX'] = None
                            aggregate_dict['posY'] = None
                            aggregate_dict['posZ'] = None
                            aggregate_dict['velX'] = None
                            aggregate_dict['velY'] = None
                            aggregate_dict['velZ'] = None
                            aggregate_dict['accX'] = None
                            aggregate_dict['accY'] = None
                            aggregate_dict['accZ'] = None
                            aggregate_dict['bodyHeight'] = None
                            aggregate_dict['bodyWidth'] = None
                            aggregate_dict['state'] = None
                            aggregate_dict['kidOrAdult'] = None
                            aggregate_dict['signOfLife'] = None
                            aggregate_dict['pointCloudDetected'] = wallStateParam[mac]['pandasDF']['pointCloudDetected'].mean(skipna=True)

                            if not math.isnan(aggregate_dict['pointCloudDetected']):
                              if aggregate_dict['pointCloudDetected'] > 0:
                                aggregate_dict['pointCloudDetected'] = 1
                              elif aggregate_dict['pointCloudDetected'] == 0:
                                aggregate_dict['pointCloudDetected'] = 0
                            else:
                              aggregate_dict['pointCloudDetected'] = None

                            # print(aggregate_dict['state'])
                            dict_copy = copy.deepcopy(aggregate_dict)
                            my_list.append(dict_copy)
                            # print(json_string)

                            # Update the new data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                            wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].iloc[-1:,:]

                        else:
                            # Append data frame
                            wallStateParam[mac]['pandasDF'] = pd.concat([wallStateParam[mac]['pandasDF'], pd.DataFrame([wall_Dict])], ignore_index=True)
                            # wallStateParam[mac]['pandasDF'] = wallStateParam[mac]['pandasDF'].append(wall_Dict, ignore_index=True)
                     

                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    wallStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']

    # Update state parameters 
    # dum = sharedList[0]
    # dum[mac] = wallStateParam[mac]
    # sharedList[0] = dum

    # Update the shared Queue
    dum_dict = {}
    dum_dict['mac'] = mac
    dum_dict['type'] = radarType
    dum_dict['stateParam'] = wallStateParam[mac]
    stateParamQueue.put(dum_dict)

    try: 
        print("my_list: ", my_list)
        pubPayload = {
            "DATA": my_list
        }
        op = len(pubPayload["DATA"])
        if len(pubPayload["DATA"]) > 0:
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            print(f"on message {op}", radarType)
        
            if radarType == 'wall':
                pubPayload["TYPE"]="WALL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/"+mac+"/DATA/WALL/JSON", jsonData)
                print(result)
            elif radarType == 'ceil':
                pubPayload["TYPE"]="CEIL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/CEIL/JSON", jsonData)
                print(result)
            elif radarType == 'vital':
                pubPayload["TYPE"]="VITAL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/VITAL/JSON", jsonData)
                print(result)
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")              
            time.sleep(0.1)
            # sharedDataBuffer.append(jsonData)
            dataBufferQueue.put(jsonData)
    except Exception as e:
        print(e)

def decode_process_publish_vital(stateParamQueue, mac, data, vitalStateParam, mqttc, algoCfg, devicesTbl):

    my_list = []
    print("algorithm configuration: ", algoCfg)
    # for x in data:
    print(len(data.items()))
    # print(sharedList)
    # vitalStateParam = sharedList[2]
    # print(vitalStateParam)
    for ts_str, byteAD in data.items():
        print("parsing data")
        try:
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        if ts == 0:
            continue

        # if len(byteAD) > 52:
        if len(byteAD) > 0:
            # Error happens occasionally when decoding the raw data frame,
            # may require error analysis in future to find out the actual cause.
            try:
                outputDict = parseStandardFrame(byteAD)
            except:
                outputDict = None
                continue
            print(mac)
            # print(byteAD)
            # print(outputDict)
            # --------------------------------- Wall-Mounted Radar Tracking and Posture Analysis -------------------------------
            # ------------------------------------------------------------------------------------------------------------------
            DEVICE = devicesTbl[mac]
            if DEVICE["TYPE"] == '1':
                radarType = 'wall'
            elif DEVICE["TYPE"] == '2':
                radarType = 'ceil'
            elif DEVICE["TYPE"] == '3':
                radarType = 'vital'
            xShift = DEVICE["DEPLOY_X"]
            yShift = DEVICE["DEPLOY_Y"]
            zShift = DEVICE["DEPLOY_Z"] 
            rotXDegree = DEVICE["ROT_X"]
            rotYDegree = DEVICE["ROT_Y"]
            rotZDegree = DEVICE["ROT_Z"]

            if "fall_deltaZHeight_" + mac in algoCfg["DATA"]:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight_"+mac]
            else:
                deltaZHeight_threshold = algoCfg["DATA"]["fall_deltaZHeight"]

            if "fall_deltaZPos_" + mac in algoCfg["DATA"]:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos_"+mac]
            else:
                deltaZPos_threshold = algoCfg["DATA"]["fall_deltaZPos"]

            if "fall_bodyWidth_" + mac in algoCfg["DATA"]:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth_"+mac]
            else:
                bodyWidth_threshold = algoCfg["DATA"]["fall_bodyWidth"]

            if "fall_averageHeight_" + mac in algoCfg["DATA"]:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight_"+mac]
            else:
                averageHeight_threshold = algoCfg["DATA"]["fall_averageHeight"]

            if "fall_minZVel_" + mac in algoCfg["DATA"]:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel_"+mac]
            else:
                minZVel_threshold = algoCfg["DATA"]["fall_minZVel"]

            if "fall_numFrames_" + mac in algoCfg["DATA"]:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames_"+mac])
            else:
                numFrames_threshold = int(algoCfg["DATA"]["fall_numFrames"])

            if "vital_periodStationary_" + mac in algoCfg["DATA"]:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary_"+mac]
            else:
                periodStationary_threshold = algoCfg["DATA"]["vital_periodStationary"]

            if "vital_distanceMoved_" + mac in algoCfg["DATA"]:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved_"+mac]
            else:
                distanceMoved_threshold = algoCfg["DATA"]["vital_distanceMoved"]

            if "vital_xPos_" + mac in algoCfg["DATA"]:
                xPos_threshold = algoCfg["DATA"]["vital_xPos_"+mac]
            else:
                xPos_threshold = algoCfg["DATA"]["vital_xPos"]

            if "vital_zPos_" + mac in algoCfg["DATA"]:
                zPos_threshold = algoCfg["DATA"]["vital_zPos_"+mac]
            else:
                zPos_threshold = algoCfg["DATA"]["vital_zPos"]

            if "aggregatePeriod_" + mac in algoCfg["DATA"]:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod_"+mac]
            else:
                aggregatePeriod_threshold = algoCfg["DATA"]["aggregatePeriod"]

            # --------------------------------- Radar Tracking and Vital Sign Detection ----------------------------------------
            # ------------------------------------------------------------------------------------------------------------------

            if radarType == 'vital':

                # global vitalStateParam

                if mac not in vitalStateParam:
                    vitalStateParam[mac] = {}
                    vitalStateParam[mac]['timeNow'] = 0
                    vitalStateParam[mac]['label_state'] = ['Out of Bed', 'In Bed', 'Imminent Bed Exit']

                # Radar Placement Coordinates
                radar_coord = np.asarray([xShift, yShift, zShift])
                vitalStateParam[mac]['radar_coord'] = radar_coord

                # Radar Time Stamp
                # deltaT = outputDict['timeStamp'] - vitalStateParam[mac]['timeNow']
                # vitalStateParam[mac]['timeNow'] = outputDict['timeStamp']
                # vital_dict = {}
                # vital_dict['timeStamp'] = outputDict['timeStamp']
                deltaT = ts - vitalStateParam[mac]['timeNow']
                vitalStateParam[mac]['timeNow'] = ts
                vital_dict = {}
                vital_dict['timeStamp'] = ts

                # Parameters Re-Initialization if Time Interval between Consecutive Data Frames Larger than Certain Threshold
                # For Robust Analytics with Data Frames / Packets Drop
                if deltaT > 5:
                    vitalStateParam[mac]['x0'] = np.nan
                    vitalStateParam[mac]['y0'] = np.nan
                    vitalStateParam[mac]['z0'] = np.nan
                    vitalStateParam[mac]['periodStationary'] = 0
                    vitalStateParam[mac]['prevTimeStationary'] = 0
                    vitalStateParam[mac]['prevBreathRate'] = 0
                    vitalStateParam[mac]['trackIDs'] = np.zeros((0))  # trackers ID
                    vitalStateParam[mac]['trackPos'] = np.zeros((0, 3))
                    vitalStateParam[mac]['label_list'] = []
                    vitalStateParam[mac]['rollingVelY'] = []
                    vitalStateParam[mac]['rollingHeight'] = []
                    vitalStateParam[mac]['previous_pointClouds'] = []  # previous point clouds
                    vitalStateParam[mac]['trackerInvalid'] = np.zeros((0))
                    vitalStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp','bedOccupancy','breathRate','heartRate','inBedMoving','signOfLife','pointCloudDetected'])

                # Vital Sign Data Extraction
                # numTracks = 0
                # print("============================\n", outputDict,"\n------------------------------\n",vitalStateParam, "\n==============================")
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    if len(outputDict['pointCloud']) > 0:
                      vital_dict['pointCloudDetected'] = 1
                    else:
                      vital_dict['pointCloudDetected'] = 0 

                  if "numDetectedTracks" in outputDict:
                    print("+++++++++++++++++++++")
                    numTracks = outputDict['numDetectedTracks']
                    # pointClouds = outputDict['pointCloud']
                    # trackIndices = outputDict['trackIndexes']
                    # trackUnique = np.unique(trackIndices)
                    # trackIndices = trackIndices - trackIndices.min()
                    # print(count_subjectStationary)
                    # print(vitalStateParam[mac]['periodStationary'])
                    
                    if len(vitalStateParam[mac]['previous_pointClouds']) > 0 and "trackIndexes" in outputDict:
                     trackIndices = outputDict['trackIndexes']

                     if numTracks > 0 and len(vitalStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(vitalStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                      if ('vitals' in outputDict) and vitalStateParam[mac]['periodStationary'] > periodStationary_threshold:  # and count_subjectStationary > 100:
                        vitalsDict = outputDict['vitals']
                        # if count_vitalSign == 0:
                        #     Breathsignal = np.array(vitalsDict['breathWaveform'])
                        #     Heartbeatsignal = np.array(vitalsDict['heartWaveform'])
                        #     count_vitalSign += 1
                        # else:
                        #     Breathsignal = np.concatenate((Breathsignal, np.array(vitalsDict['breathWaveform'])), axis=0)
                        #     Heartbeatsignal = np.concatenate((Heartbeatsignal, np.array(vitalsDict['heartWaveform'])), axis=0)
                        #     count_vitalSign += 1

                        # if count_vitalSign == 17:
                        #     Breathsignal = Breathsignal[15:]
                        #     Heartbeatsignal = Heartbeatsignal[15:]
                        #     count_vitalSign = 16

                        curBreathRate = float(vitalsDict["breathRate"])
                        curHeartRate = float(vitalsDict["heartRate"])

                        if vitalStateParam[mac]['prevBreathRate'] > 0:
                            if curBreathRate - vitalStateParam[mac]['prevBreathRate'] > 1:
                                curBreathRate = vitalStateParam[mac]['prevBreathRate'] + np.random.uniform(0, 0.5, 1)[0]
                            elif vitalStateParam[mac]['prevBreathRate'] - curBreathRate > 1:
                                curBreathRate = vitalStateParam[mac]['prevBreathRate'] - np.random.uniform(0, 0.5, 1)[0]

                        # if curBreathRate > 25:
                            # curBreathRate = None
                        # elif curBreathRate < 6:
                            # curBreathRate = None

                        # if curHeartRate > 200:
                            # curHeartRate = None
                        # elif curHeartRate < 30:
                            # curHeartRate = None

                        # if breathRate_MA!=0 and curBreathRate != None:
                        #     if curBreathRate > 3*breathRate_MA or curBreathRate < 0.3*breathRate_MA:
                        #         curBreathRate = None
                        #     else:
                        #         breathRate_MA = (breathRate_MA + curBreathRate)/2
                        # else:
                        #     breathRate_MA = curBreathRate
                            
                        # if heartRate_MA!=0 and curHeartRate != None:
                        #     if curHeartRate > 3*heartRate_MA or curHeartRate < 0.3*heartRate_MA:
                        #         curHeartRate = None
                        #     else:
                        #         heartRate_MA = (heartRate_MA + curHeartRate)/2     
                        # else:
                        #     heartRate_MA = curHeartRate                          

                        vital_dict['breathRate'] = curBreathRate
                        vital_dict['heartRate'] = curHeartRate
                        vitalStateParam[mac]['prevBreathRate'] = curBreathRate
                        # print("\n*******************\nvital_dict: ", vital_dict)

                      elif vitalStateParam[mac]['periodStationary'] <= periodStationary_threshold:  # count_subjectStationary <= 100:
                        # print("\n*******************\nvital_dict: X", )
                        # count_vitalSign = 0
                        vitalStateParam[mac]['prevBreathRate'] = 0
                        # vital_dict['breathRate'] = []
                        # vital_dict['heartRate'] = []

                      # if dataOk and len(detObj["x"]) > 1:
                      if numTracks > 0 and len(vitalStateParam[mac]['previous_pointClouds']) > 0 and \
                            len(vitalStateParam[mac]['previous_pointClouds']) == len(trackIndices):

                        # Sign of Life
                        vital_dict['signOfLife'] = 1

                        # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                        # Since track indexes are delayed a frame, delay showing the current points by 1 frame
                        vitalStateParam[mac]['previous_pointClouds'][:, 6] = trackIndices
                        # snr = vitalStateParam[mac]['previous_pointClouds'][:, 4]
                        # vitalStateParam[mac]['previous_pointClouds'] = vitalStateParam[mac]['previous_pointClouds'][snr > 7, :]
                        # trackIndices = trackIndices[snr > 7]
                        # x_coord = vitalStateParam[mac]['previous_pointClouds'][:, 0]
                        y_coord = vitalStateParam[mac]['previous_pointClouds'][:, 1]
                        # z_coord = vitalStateParam[mac]['previous_pointClouds'][:, 2]
                        v_coord = vitalStateParam[mac]['previous_pointClouds'][:, 3]
                        # points = np.stack((x_coord, y_coord, z_coord), axis=-1)

                        # Decode 3D People Counting Target List TLV
                        # MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST
                        # 3D Struct format
                        # uint32_t     tid;     /*! @brief   tracking ID */
                        # float        posX;    /*! @brief   Detected target X coordinate, in m */
                        # float        posY;    /*! @brief   Detected target Y coordinate, in m */
                        # float        posZ;    /*! @brief   Detected target Z coordinate, in m */
                        # float        velX;    /*! @brief   Detected target X velocity, in m/s */
                        # float        velY;    /*! @brief   Detected target Y velocity, in m/s */
                        # float        velZ;    /*! @brief   Detected target Z velocity, in m/s */
                        # float        accX;    /*! @brief   Detected target X acceleration, in m/s2 */
                        # float        accY;    /*! @brief   Detected target Y acceleration, in m/s2 */
                        # float        accZ;    /*! @brief   Detected target Z acceleration, in m/s2 */
                        # float        ec[16];  /*! @brief   Target Error covarience matrix, [4x4 float], in row major order, range, azimuth, elev, doppler */
                        # float        g;
                        # float        confidenceLevel;    /*! @brief   Tracker confidence metric*/
                        trackData = outputDict['trackData']

                        for trackIdx in range(numTracks):
                           
                            print("number of tracks = ", numTracks)
                            # Tracker position and velocity obtained from Extended Kalman Filter (EKF) algorithm
                            trackId = trackData[trackIdx, 0]
                            x_pos = trackData[trackIdx, 1]
                            y_pos = trackData[trackIdx, 2]
                            z_pos = trackData[trackIdx, 3]
                            x_vel = trackData[trackIdx, 4]
                            y_vel = trackData[trackIdx, 5]
                            z_vel = trackData[trackIdx, 6]

                            # Tracker polar coordinates
                            # trackerRangeXY = np.linalg.norm([x_pos, y_pos], ord=2) # tracker range projected onto the x-y plane
                            # trackerRange = np.linalg.norm([x_pos, y_pos, z_pos], ord=2)
                            # trackerAzimuth = np.arctan(x_pos / y_pos) * 180 / np.pi  # Azimuth angle in radian
                            # trackerElevation = np.arctan(z_pos / trackerRangeXY) * 180 / np.pi  # Elevation angle in radian
                            # trackerRadialVelocityXY = (x_pos * x_vel + y_pos * y_vel) / trackerRangeXY # tracker radial velocity projected onto the x-y plane
                            # trackerRadialVelocity = (x_pos * x_vel + y_pos * y_vel + z_pos * z_vel) / trackerRange
                            # trackerAzimuthVelocity = (x_vel * y_pos - x_pos * y_vel) / (trackerRangeXY**2)
                            # trackerElevationVelocity
                            # print(trackerRange, trackerAzimuth)

                            # Tracker velocity (normalized) direction
                            # x_vel_direction = x_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])  # Add epsilon to denominator to prevent run-time warning
                            # y_vel_direction = y_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])
                            # z_vel_direction = z_vel / np.linalg.norm([x_vel, y_vel, z_vel, 0.001])

                            # Append new tracker information - geometry and velocity direction,
                            # if distance between any two trackers larger than certain threshold
                            # dist = np.linalg.norm(trackPos - np.tile([[x_pos,y_pos,z_pos]], (len(trackPos),1)), ord=2, axis=1)
                            # distVelocity = np.linalg.norm(trackVelocity - np.tile([[x_vel,y_vel,z_vel]], (len(trackVelocity),1)), ord=2, axis=1)

                            # ----------------- Bed Occupancy Detection and Stationary / Moving Subject Analysis ---------------
                            # --------------------------------------------------------------------------------------------------

                            # if len(trackPos) == 0 or np.amin(dist) > 1 or np.amin(distVelocity) > 3:
                            if len(vitalStateParam[mac]['trackPos']) == 0 or np.sum(vitalStateParam[mac]['trackIDs'] == trackId) == 0:
                                vitalStateParam[mac]['trackPos'] = np.concatenate((vitalStateParam[mac]['trackPos'], [[x_pos, y_pos, z_pos]]), axis=0)
                                vitalStateParam[mac]['trackIDs'] = np.concatenate((vitalStateParam[mac]['trackIDs'], [trackId]), axis=0)
                                # trackPos = np.concatenate((trackPos, [[x_pos, y_pos, z_pos]]), axis=0)
                                # trackVelocity = np.concatenate((trackVelocity, [[x_vel, y_vel, z_vel]]), axis=0)
                                vitalStateParam[mac]['trackerInvalid'] = np.concatenate((vitalStateParam[mac]['trackerInvalid'], [0]), axis=0)
                                vitalStateParam[mac]['rollingVelY'].append([])
                                vitalStateParam[mac]['rollingHeight'].append([])

                            # elif trackerInvalid[minDistIdx] == 1:
                            else:

                                # Update tracker information if distance between two particular trackers smaller than certain threshold.
                                # minDistIdx = np.argmin(dist)
                                # if trackerInvalid[minDistIdx] == 0:
                                #       continue

                                # Update tracker information according to the allocated tracking ID.
                                minDistIdx = np.arange(len(vitalStateParam[mac]['trackIDs']))[vitalStateParam[mac]['trackIDs'] == trackId][0]
                                vitalStateParam[mac]['trackerInvalid'][minDistIdx] = vitalStateParam[mac]['trackerInvalid'][minDistIdx] - 1
                                vitalStateParam[mac]['trackPos'][minDistIdx] = [x_pos, y_pos, z_pos]
                                # trackVelocity[minDistIdx] = [x_vel, y_vel, z_vel]

                                if math.isnan(vitalStateParam[mac]['x0']):
                                    distanceMoved = 10 # Arbitrary large value
                                else:
                                    distanceMoved = np.abs(vitalStateParam[mac]['x0'] - x_pos) + np.abs(vitalStateParam[mac]['y0'] - y_pos) + np.abs(vitalStateParam[mac]['z0'] - z_pos)
                                    
                                vitalStateParam[mac]['x0'] = x_pos
                                vitalStateParam[mac]['y0'] = y_pos
                                vitalStateParam[mac]['z0'] = z_pos

                                # Rolling tracker velocity and height
                                y_height = np.percentile(y_coord, [1])
                                y_height = vitalStateParam[mac]['radar_coord'][1] - y_height
                                vitalStateParam[mac]['rollingVelY'][minDistIdx].append(y_vel)
                                vitalStateParam[mac]['rollingHeight'][minDistIdx].append(y_height)

                                # State of the subject
                                # print(np.linalg.norm([x_vel, y_vel, z_vel]))
                                # if np.average(vitalStateParam[mac]['rollingVelY'][minDistIdx]) < -0.3 and np.average(vitalStateParam[mac]['rollingHeight'][minDistIdx]) > 1.1 and \
                                    # len(vitalStateParam[mac]['rollingHeight'][minDistIdx]) == 5 and np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5:
                                    # label_list.append(3)
                                    # count_subjectStationary = 0
                                    # periodStationary = 0
                                    # vital_dict['bedOccupancy'] = 1
                                    # vitalStateParam[mac]['periodStationary'] = 0
                                    # vitalStateParam[mac]['label_list'].append(2)

                                # elif np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5 and np.linalg.norm([x_vel, y_vel, z_vel]) <= 0.3:
                                if len(v_coord[trackIndices == trackId]) > 0:
                                  # if np.abs(x_pos) < 0.6 and np.abs(z_pos) < 0.6 and np.percentile(np.abs(v_coord[trackIndices == trackId]), [99]) <= 1:
                                  if np.abs(x_pos) < xPos_threshold and np.abs(z_pos) < zPos_threshold and distanceMoved < distanceMoved_threshold:
                                    # if np.abs(x_pos) < 0.8 and np.abs(z_pos) < 0.8 and np.percentile(v_coord, [99]) <= 0.3:
                                    # print("In Bed, Subject Stationary")
                                    vital_dict['bedOccupancy'] = 1
                                    # label_list.append(0)
                                    # count_subjectStationary += 1
                                    if vitalStateParam[mac]['prevTimeStationary'] == 0:
                                        vitalStateParam[mac]['prevTimeStationary'] = ts
                                    deltaTime = ts - vitalStateParam[mac]['prevTimeStationary']
                                    vitalStateParam[mac]['periodStationary'] = vitalStateParam[mac]['periodStationary'] + deltaTime
                                    vitalStateParam[mac]['prevTimeStationary'] = ts
                                    # print(vitalStateParam[mac]['periodStationary'])
                                    vitalStateParam[mac]['label_list'].append(1)

                                  # elif np.abs(x_pos) < 0.5 and np.abs(z_pos) < 0.5 and np.linalg.norm([x_vel, y_vel, z_vel]) > 0.3:
                                  # elif np.abs(x_pos) < 0.6 and np.abs(z_pos) < 0.6 and np.percentile(np.abs(v_coord[trackIndices == trackId]), [99]) > 1:
                                  elif np.abs(x_pos) < xPos_threshold and np.abs(z_pos) < zPos_threshold:
                                    # elif np.abs(x_pos) < 0.8 and np.abs(z_pos) < 0.8 and np.percentile(v_coord, [99]) > 0.3:
                                    # print("In Bed, Subject Moving")
                                    vital_dict['bedOccupancy'] = 1
                                    vital_dict['inBedMoving'] = 1
                                    # label_list.append(1)
                                    # count_subjectStationary = 0
                                    vitalStateParam[mac]['periodStationary'] = 0
                                    vitalStateParam[mac]['label_list'].append(1)

                                  elif np.abs(x_pos) > 1.0 or np.abs(z_pos) > 1.0:
                                    # print("Out of Bed")
                                    vital_dict['bedOccupancy'] = 0
                                    # label_list.append(2)
                                    # count_subjectStationary = 0
                                    vitalStateParam[mac]['periodStationary'] = 0
                                    vitalStateParam[mac]['label_list'].append(0)

                                  if len(vitalStateParam[mac]['rollingHeight'][minDistIdx]) > 4:
                                    del vitalStateParam[mac]['rollingHeight'][minDistIdx][0]
                                    del vitalStateParam[mac]['rollingVelY'][minDistIdx][0]

                                elif np.abs(x_pos) < 0.5:
                                    vital_dict['bedOccupancy'] = 1

                                elif np.abs(x_pos) > 1.0:
                                    vital_dict['bedOccupancy'] = 0

                            # --------------------------------------------------------------------------------------------------
                            # --------------------------------------------------------------------------------------------------

                        # Remove unused tracker information and parameters
                        trackerInvalidIdx = np.arange(len(vitalStateParam[mac]['trackerInvalid']))
                        trackerInvalidIdx = trackerInvalidIdx[vitalStateParam[mac]['trackerInvalid'] == 1]
                        for Idx in range(len(trackerInvalidIdx)):
                            rollingVelY.pop(trackerInvalidIdx[Idx])
                            rollingHeight.pop(trackerInvalidIdx[Idx])
                        vitalStateParam[mac]['trackPos']  = vitalStateParam[mac]['trackPos'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackIDs'] = vitalStateParam[mac]['trackIDs'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackerInvalid'] = vitalStateParam[mac]['trackerInvalid'][vitalStateParam[mac]['trackerInvalid'] == 0]
                        vitalStateParam[mac]['trackerInvalid'] = vitalStateParam[mac]['trackerInvalid'] + 1

                if len(vitalStateParam[mac]['label_list']) >= 10:
                    if statistics.mode(vitalStateParam[mac]['label_list']) == 2:
                        
                        # Publish alert via MQTT communication channel
                        pubPayload = {"TIMESTAMP":ts, "URGENCY":2, "TYPE":3, "DETAILS":"IMMINENT BED EXIT"}
                        jsonData = json.dumps(pubPayload)
                        mqttc.publish("/GMT/DEV/"+mac+"/ALERT", jsonData)

                    vitalStateParam[mac]['label_list'] = []

                # Each pointCloud has the following: X, Y, Z, Doppler, SNR, Noise, Track index
                if outputDict is not None:
                  if 'pointCloud' in outputDict:
                    vitalStateParam[mac]['previous_pointClouds'] = outputDict['pointCloud']
                # time.sleep(0.01)  # Sampling frequency of 30 Hz
                
                # print(vitalStateParam[mac]['pandasDF'])
                # Time Series Data Aggregation
                
                if vitalStateParam[mac]['pandasDF'].empty:
                    # Append data frame
                    vitalStateParam[mac]['pandasDF'] = pd.DataFrame(columns=['timeStamp','bedOccupancy','breathRate','heartRate','inBedMoving','signOfLife','pointCloudDetected'])
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)

                elif (vital_dict['timeStamp'] - vitalStateParam[mac]['pandasDF']['timeStamp'].iloc[0]) > aggregate_period:
                    # aggregate_dict = vitalStateParam[mac]['pandasDF'].agg({'timeStamp': ['mean'], 'bedOccupancy': 'mean',
                    #                                                        'breathRate': 'mean', 'heartRate': 'mean'})

                    # print(vitalStateParam[mac]['pandasDF'])
                    # aggregate_dict = aggregate_dict.to_dict('r')
                    # aggregate_dict = aggregate_dict[0]
                    # if str(aggregate_dict['bedOccupancy']) != 'nan':
                    #     for key, value in aggregate_dict.items():
                    #         if str(value)[0:3] == 'nan':
                    #             aggregate_dict[key] = None
                    #     # aggregate_dict['timeStamp'] = str(dt.fromtimestamp(float(aggregate_dict['timeStamp']), tz))[:23]
                    #     if aggregate_dict['bedOccupancy'] is not None:
                    #         aggregate_dict['bedOccupancy'] = bool(round(aggregate_dict['bedOccupancy']))
                    #     # json_string = json.dumps(aggregate_dict, indent=4)
                        
                    # else:
                    #     aggregate_dict = {}
                    #     aggregate_dict['timeStamp'] = vitalStateParam[mac]['pandasDF']['timeStamp'].agg('mean')
                    #     aggregate_dict['numSubjects'] = 0
                    #     aggregate_dict['bedOccupancy'] = False
                    #     # json_string = '{}'

                    aggregate_dict = {}
                    aggregate_dict['timeStamp'] = round(vitalStateParam[mac]['pandasDF']['timeStamp'].mean(skipna=True),2)
                    aggregate_dict['bedOccupancy'] = vitalStateParam[mac]['pandasDF']['bedOccupancy'].mean(skipna=True)
                    aggregate_dict['breathRate'] = vitalStateParam[mac]['pandasDF']['breathRate'].mean(skipna=True)
                    aggregate_dict['heartRate'] = vitalStateParam[mac]['pandasDF']['heartRate'].mean(skipna=True)
                    aggregate_dict['inBedMoving'] = vitalStateParam[mac]['pandasDF']['inBedMoving'].mean(skipna=True)
                    aggregate_dict['signOfLife'] = vitalStateParam[mac]['pandasDF']['signOfLife'].mean(skipna=True)
                    aggregate_dict['pointCloudDetected'] = vitalStateParam[mac]['pandasDF']['pointCloudDetected'].mean(skipna=True)

                    if not math.isnan(aggregate_dict['bedOccupancy']):
                        aggregate_dict['bedOccupancy'] = bool(round(aggregate_dict['bedOccupancy']))
                    if not math.isnan(aggregate_dict['inBedMoving']):
                        aggregate_dict['inBedMoving'] = bool(round(aggregate_dict['inBedMoving']))
                    if not math.isnan(aggregate_dict['signOfLife']):
                        aggregate_dict['signOfLife'] = bool(round(aggregate_dict['signOfLife']))
                    if not math.isnan(aggregate_dict['pointCloudDetected']):
                        if aggregate_dict['pointCloudDetected'] > 0:
                            aggregate_dict['pointCloudDetected'] = 1
                        elif aggregate_dict['pointCloudDetected'] == 0:
                            aggregate_dict['pointCloudDetected'] = 0
                    else:
                        aggregate_dict['pointCloudDetected'] = None

                    for key, value in aggregate_dict.items():
                        if str(value)[0:3] == 'nan':
                            aggregate_dict[key] = None

                    dict_copy = copy.deepcopy(aggregate_dict)
                    my_list.append(dict_copy)
                    # print("JSON: ", json_string)

                    # Update the new data frame
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)
                    vitalStateParam[mac]['pandasDF'] = vitalStateParam[mac]['pandasDF'].iloc[-1:, :]
                else:
                    # Append data frame
                    vitalStateParam[mac]['pandasDF'] = pd.concat([vitalStateParam[mac]['pandasDF'], pd.DataFrame([vital_dict])], ignore_index=True)

                # Write key-value dictionary to JSON file
                # json_string = json.dumps(vital_dict, indent=4)
                # json.dump(json_string, outputFile)
                # print(json_string)

            # ------------------------------------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------------------------------------
    
    # Update the shared list
    # dum = sharedList[2]
    # dum[mac] = vitalStateParam[mac]      
    # sharedList[2]= dum

    # Update the shared Queue
    dum_dict = {}
    dum_dict['mac'] = mac
    dum_dict['type'] = radarType
    dum_dict['stateParam'] = vitalStateParam[mac]
    stateParamQueue.put(dum_dict)

    try: 
        print("my_list: ", my_list)
        pubPayload = {
            "DATA": my_list
        }
        op = len(pubPayload["DATA"])
        if len(pubPayload["DATA"]) > 0:
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            print(f"on message {op}", radarType)
        
            if radarType == 'wall':
                pubPayload["TYPE"]="WALL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/"+mac+"/DATA/WALL/JSON", jsonData)
                print(result)
            elif radarType == 'ceil':
                pubPayload["TYPE"]="CEIL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/CEIL/JSON", jsonData)
                print(result)
            elif radarType == 'vital':
                pubPayload["TYPE"]="VITAL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/VITAL/JSON", jsonData)
                print(result)
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")              
            time.sleep(0.1)
            # sharedDataBuffer.append(jsonData)
            dataBufferQueue.put(jsonData)
    except Exception as e:
        print(e)

def decode_process_publish_ceil(stateParamQueue, mac, data, ceilStateParam, mqttc, algoCfg, devicesTbl):
    # Not implemented
    return

def process_dataQueue(stateParamQueue, dataBufferQueue):
    global wallStateParam, ceilStateParam, vitalStateParam, dataBuffer
    while 1:
        try:
            while stateParamQueue.empty():
                time.sleep(0.1)
            dict = stateParamQueue.get()
            # print(dict)
            if dict['type'] == 'wall':
                wallStateParam[dict['mac']]=dict['stateParam']
            elif dict['type'] == 'ceil':
                ceilStateParam[dict['mac']]=dict['stateParam']
            elif dict['type'] == 'vital':
                vitalStateParam[dict['mac']]=dict['stateParam']
            jsonData = dataBufferQueue.get()
            # print(jsonData)
            dataBuffer.append(jsonData)
        except Exception as e:
            print(e)

def createProcess(radarType, stateParamQueue, mac, data, stateParamDict, mqttc, algoCfg, devicesTbl):
    startTime = time.time()
    if radarType == '1':
        pool1.apply_async(decode_process_publish_wall(stateParamQueue, mac, data, stateParamDict, mqttc, algoCfg, devicesTbl))
    elif radarType == '2':
        pool1.apply_async(decode_process_publish_ceil(stateParamQueue, mac, data, stateParamDict, mqttc, algoCfg, devicesTbl))
    elif radarType == '3':
        pool1.apply_async(decode_process_publish_vital(stateParamQueue, mac, data, stateParamDict, mqttc, algoCfg, devicesTbl))    
    print("Time lapsed: ", time.time() - startTime)

def on_message(mosq, obj, msg):
    global devicesTbl,config,aggregate_period,algoCfg
    print(msg.payload)
    in_data = ''
    topicList = msg.topic.split('/')
    if topicList[-1] == "UPDATE_DEV_CONF":
        print("=====================================================================")
        print("Received device setting update request for: " + msg.payload.decode("utf-8"))
        print("=====================================================================")
        DEV = msg.payload.decode("utf-8").upper()
        if DEV in devicesTbl:
            print(DEV)
            del devicesTbl[DEV]
        return
    # if topicList[-1] == "ALGO_CONFIG":
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    #     pubPayload = {"STATUS":"UPDATED"}
    #     jsonData = json.dumps(pubPayload)
    #     mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
    # elif bool(algoCfg) == 0:
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    if topicList[-1] == "ALGO_CONFIG":
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
          print("algoCfg updating 1\n")
          try:
            while _algoCfg.status_code != 200:
              print("API call 1\n")
              _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
            algoCfg = _algoCfg.json()
            pubPayload = {"STATUS":"UPDATED"}
            jsonData = json.dumps(pubPayload)
            mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
            algoCfg_updated = 1
          except Exception as e:
            print(e)
        return
    elif bool(algoCfg) == 0:
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
            print("algoCfg updating 0\n")
            try:
              while _algoCfg.status_code != 200:
                print("API call 0\n")
                _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
              algoCfg = _algoCfg.json()
              algoCfg_updated = 1
            except Exception as e:
                print(e)

    devName = ''
    xShift = 0
    yShift = 0
    zShift = 2.5
    rotXDegree = 0
    rotYDegree = 0
    rotZDegree = 0
    # my_obj = eval(in_data)
    # print(in_data)
    # print(f"{msg.topic}, {msg.payload}")
    devName = topicList[3]
    # print(topicList)
    if devName not in devicesTbl:
        print("+++++++++++++++++++++++++++++")
        print(devName)
        print("+++++++++++++++++++++++++++++")
        devicesTbl[devName] = {}  
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)        
        sql = "SELECT TYPE, DEPLOY_X, DEPLOY_Y, DEPLOY_Z, ROT_X, ROT_Y, ROT_Z FROM Gaitmetrics.DEVICES WHERE MAC='%s'"%(devName)
        cursor.execute(sql)
        dbresult = cursor.fetchone() 
        if dbresult == None:
            print("Device not registered")
            return
        devicesTbl[devName] = dbresult
        devicesTbl[devName]["DATA_QUEUE"] = {}
        sql="UPDATE `DEVICES` SET `STATUS`='CONNECTED' WHERE MAC='"+devName+"';"
        cursor.execute(sql)
        connection.commit()        
        cursor.close()
        connection.close()        
    # print(devicesTbl)
    # if not devName == 'F412FAE261A4':
    #     return

    in_data = str(msg.payload).replace("b'", "").split(',')
    # print(topicList[-1])
    # print(in_data)
    for x in in_data:
        print("Decoding hexadecimal\n")
        try:
            ts_str, hexD = x.split(':')
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        while 1:
            print("Decoding hexadecimal 1\n")
            if "'" in hexD:
                hexD = hexD.replace("'", "")
            else:
                break
        # Error happens occasionally when converting the raw data representation,
        # may require error analysis in future to find out the actual cause.
        try:
            byteAD = bytearray.fromhex(hexD)
        except:
            continue
        # if len(hexD)>1:
            # print(hexD)  
        devicesTbl[devName]["DATA_QUEUE"][ts_str]=byteAD
    devicesTbl[devName]["DATA_QUEUE"] = dict(sorted(devicesTbl[devName]["DATA_QUEUE"].items()))
    # DQ = list(devicesTbl[devName]["DATA_QUEUE"])
    # print(devName, DQ)
    # print(float(DQ[-1])-float(DQ[0]))
    # if float(DQ[-1])-float(DQ[0]) < aggregate_period:
        # return
    # else: 
        # print("Chunk time: ", float(DQ[-1])-float(DQ[0]))
    # try:
    if topicList[-1] == "LF" or topicList[-1] == "RAW":
        threading.Thread(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],)).start()
        # Process(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],)).start()
    # except:
    #     print("Error Processing")
        devicesTbl[devName]["DATA_QUEUE"]={}
    # print(devicesTbl)

def on_message_obsolete(mosq, obj, msg):
    global devicesTbl,config,aggregate_period,algoCfg
    # print(msg.payload)
    in_data = ''
    topicList = msg.topic.split('/')
    if topicList[-1] == "UPDATE_DEV_CONF":
        print("=====================================================================")
        print("Received device setting update request for: " + msg.payload.decode("utf-8"))
        print("=====================================================================")
        DEV = msg.payload.decode("utf-8").upper()
        if DEV in devicesTbl:
            print(DEV)
            del devicesTbl[DEV]
        return
    # if topicList[-1] == "ALGO_CONFIG":
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    #     pubPayload = {"STATUS":"UPDATED"}
    #     jsonData = json.dumps(pubPayload)
    #     mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
    # elif bool(algoCfg) == 0:
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    if topicList[-1] == "ALGO_CONFIG":
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
          print("algoCfg updating 1\n")
          try:
            while _algoCfg.status_code != 200:
              print("API call 1\n")
              _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
            algoCfg = _algoCfg.json()
            pubPayload = {"STATUS":"UPDATED"}
            jsonData = json.dumps(pubPayload)
            mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
            algoCfg_updated = 1
          except Exception as e:
            print(e)
        return
    elif bool(algoCfg) == 0:
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
            print("algoCfg updating 0\n")
            try:
              while _algoCfg.status_code != 200:
                print("API call 0\n")
                _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
              algoCfg = _algoCfg.json()
              algoCfg_updated = 1
            except Exception as e:
                print(e)

    devName = ''
    xShift = 0
    yShift = 0
    zShift = 2.5
    rotXDegree = 0
    rotYDegree = 0
    rotZDegree = 0
    # my_obj = eval(in_data)
    # print(in_data)
    # print(f"{msg.topic}, {msg.payload}")
    devName = topicList[3]
    # print(topicList)
    if devName not in devicesTbl:
        print("+++++++++++++++++++++++++++++")
        print(devName)
        print("+++++++++++++++++++++++++++++")
        devicesTbl[devName] = {}  
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)        
        sql = "SELECT TYPE, DEPLOY_X, DEPLOY_Y, DEPLOY_Z, ROT_X, ROT_Y, ROT_Z FROM Gaitmetrics.DEVICES WHERE MAC='%s'"%(devName)
        cursor.execute(sql)
        dbresult = cursor.fetchone() 
        if dbresult == None:
            print("Device not registered")
            return
        devicesTbl[devName] = dbresult
        devicesTbl[devName]["DATA_QUEUE"] = {}
        sql="UPDATE `DEVICES` SET `STATUS`='CONNECTED' WHERE MAC='"+devName+"';"
        cursor.execute(sql)
        connection.commit()        
        cursor.close()
        connection.close()        
    # print(devicesTbl)
    # if not devName == 'F412FAE261A4':
    #     return

    in_data = str(msg.payload).replace("b'", "").split(',')
    # print(topicList[-1])
    # print(in_data)
    for x in in_data:
        # print("Decoding hexadecimal\n")
        try:
            ts_str, hexD = x.split(':')
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        while 1:
            # print("Decoding hexadecimal 1\n")
            if "'" in hexD:
                hexD = hexD.replace("'", "")
            else:
                break
        # Error happens occasionally when converting the raw data representation,
        # may require error analysis in future to find out the actual cause.
        try:
            byteAD = bytearray.fromhex(hexD)
        except:
            continue
        # if len(hexD)>1:
            # print(hexD)  
        devicesTbl[devName]["DATA_QUEUE"][ts_str]=byteAD
    devicesTbl[devName]["DATA_QUEUE"] = dict(sorted(devicesTbl[devName]["DATA_QUEUE"].items()))
    # DQ = list(devicesTbl[devName]["DATA_QUEUE"])
    # print(devName, DQ)
    # print(float(DQ[-1])-float(DQ[0]))
    # if float(DQ[-1])-float(DQ[0]) < aggregate_period:
        # return
    # else: 
        # print("Chunk time: ", float(DQ[-1])-float(DQ[0]))
    # try:
    if topicList[-1] == "LF" or topicList[-1] == "RAW":
        # th = threading.Thread(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],))
        # th.start()
        # Process(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],)).start()
    # except:
    #     print("Error Processing")
        if devicesTbl[devName]["TYPE"] == '1':
            if devName in wallStateParam:
                p1 = Process(target=decode_process_publish_wall, args=(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:wallStateParam[devName]}, mqttc, algoCfg, devicesTbl,))
            else:
                p1 = Process(target=decode_process_publish_wall, args=(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, devicesTbl,))
            p1.start()
            # p1.join()
        elif devicesTbl[devName]["TYPE"] == '2':
            if devName in ceilStateParam:
                p2 = Process(target=decode_process_publish_ceil, args=(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:ceilStateParam[devName]}, mqttc, algoCfg, devicesTbl,))
            else:
                p2 = Process(target=decode_process_publish_ceil, args=(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, devicesTbl,))
            p2.start()
            # p2.join()
        elif devicesTbl[devName]["TYPE"] == '3':
            if devName in vitalStateParam:
                p3 = Process(target=decode_process_publish_vital, args=(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:vitalStateParam[devName]}, mqttc, algoCfg, devicesTbl,))
            else:
                p3 = Process(target=decode_process_publish_vital, args=(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, devicesTbl,))
            p3.start()
            # p3.join()
        devicesTbl[devName]["DATA_QUEUE"]={}

def on_message2(mosq, obj, msg):
    global devicesTbl,config,aggregate_period,algoCfg
    # print(msg.payload)
    in_data = ''
    topicList = msg.topic.split('/')
    if topicList[-1] == "UPDATE_DEV_CONF":
        print("=====================================================================")
        print("Received device setting update request for: " + msg.payload.decode("utf-8"))
        print("=====================================================================")
        DEV = msg.payload.decode("utf-8").upper()
        if DEV in devicesTbl:
            print(DEV)
            del devicesTbl[DEV]
        return
    # if topicList[-1] == "ALGO_CONFIG":
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    #     pubPayload = {"STATUS":"UPDATED"}
    #     jsonData = json.dumps(pubPayload)
    #     mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
    # elif bool(algoCfg) == 0:
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    if topicList[-1] == "ALGO_CONFIG":
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
          print("algoCfg updating 1\n")
          try:
            while _algoCfg.status_code != 200:
              print("API call 1\n")
              _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
            algoCfg = _algoCfg.json()
            pubPayload = {"STATUS":"UPDATED"}
            jsonData = json.dumps(pubPayload)
            mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
            algoCfg_updated = 1
          except Exception as e:
            print(e)
        return
    elif bool(algoCfg) == 0:
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
            print("algoCfg updating 0\n")
            try:
              while _algoCfg.status_code != 200:
                print("API call 0\n")
                _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
              algoCfg = _algoCfg.json()
              algoCfg_updated = 1
            except Exception as e:
                print(e)

    devName = ''
    xShift = 0
    yShift = 0
    zShift = 2.5
    rotXDegree = 0
    rotYDegree = 0
    rotZDegree = 0
    # my_obj = eval(in_data)
    # print(in_data)
    # print(f"{msg.topic}, {msg.payload}")
    devName = topicList[3]
    # print(topicList)
    if devName not in devicesTbl:
        print("+++++++++++++++++++++++++++++")
        print(devName)
        print("+++++++++++++++++++++++++++++")
        devicesTbl[devName] = {}  
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)        
        sql = "SELECT TYPE, DEPLOY_X, DEPLOY_Y, DEPLOY_Z, ROT_X, ROT_Y, ROT_Z FROM Gaitmetrics.DEVICES WHERE MAC='%s'"%(devName)
        cursor.execute(sql)
        dbresult = cursor.fetchone() 
        if dbresult == None:
            print("Device not registered")
            return
        devicesTbl[devName] = dbresult
        devicesTbl[devName]["DATA_QUEUE"] = {}
        sql="UPDATE `DEVICES` SET `STATUS`='CONNECTED' WHERE MAC='"+devName+"';"
        cursor.execute(sql)
        connection.commit()        
        cursor.close()
        connection.close()        
    # print(devicesTbl)
    # if not devName == 'F412FAE261A4':
    #     return

    in_data = str(msg.payload).replace("b'", "").split(',')
    # print(topicList[-1])
    # print(in_data)
    for x in in_data:
        # print("Decoding hexadecimal\n")
        try:
            ts_str, hexD = x.split(':')
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        while 1:
            # print("Decoding hexadecimal 1\n")
            if "'" in hexD:
                hexD = hexD.replace("'", "")
            else:
                break
        # Error happens occasionally when converting the raw data representation,
        # may require error analysis in future to find out the actual cause.
        try:
            byteAD = bytearray.fromhex(hexD)
        except:
            continue
        # if len(hexD)>1:
            # print(hexD)  
        devicesTbl[devName]["DATA_QUEUE"][ts_str]=byteAD
    devicesTbl[devName]["DATA_QUEUE"] = dict(sorted(devicesTbl[devName]["DATA_QUEUE"].items()))
    # DQ = list(devicesTbl[devName]["DATA_QUEUE"])
    # print(devName, DQ)
    # print(float(DQ[-1])-float(DQ[0]))
    # if float(DQ[-1])-float(DQ[0]) < aggregate_period:
        # return
    # else: 
        # print("Chunk time: ", float(DQ[-1])-float(DQ[0]))
    # try:
    if topicList[-1] == "LF" or topicList[-1] == "RAW":
        # th = threading.Thread(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],))
        # th.start()
        # Process(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],)).start()
    # except:
    #     print("Error Processing")
        radarType = devicesTbl[devName]["TYPE"]
        if radarType == '1':
            if devName in wallStateParam:
                # pool1.apply_async(decode_process_publish_wall(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:wallStateParam[devName]}, mqttc, algoCfg, devicesTbl))
                threading.Thread(target=createProcess, args=(radarType, stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:wallStateParam[devName]}, mqttc, algoCfg, {devName:devicesTbl[devName]})).start()
            else:
                # pool1.apply_async(decode_process_publish_wall(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, devicesTbl))
                threading.Thread(target=createProcess, args=(radarType, stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, {devName:devicesTbl[devName]})).start()
        elif radarType == '2':
            if devName in ceilStateParam:
                # pool1.apply_async(decode_process_publish_ceil(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:ceilStateParam[devName]}, mqttc, algoCfg, devicesTbl))
                threading.Thread(target=createProcess, args=(radarType, stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:ceilStateParam[devName]}, mqttc, algoCfg, {devName:devicesTbl[devName]})).start()
            else:
                # pool1.apply_async(decode_process_publish_ceil(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, devicesTbl))
                threading.Thread(target=createProcess, args=(radarType, stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, {devName:devicesTbl[devName]})).start()
        elif radarType == '3':
            if devName in vitalStateParam:
                # pool1.apply_async(decode_process_publish_vital(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:vitalStateParam[devName]}, mqttc, algoCfg, devicesTbl))
                threading.Thread(target=createProcess, args=(radarType, stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {devName:vitalStateParam[devName]}, mqttc, algoCfg, {devName:devicesTbl[devName]})).start()
            else:
                # pool1.apply_async(decode_process_publish_vital(stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, devicesTbl))
                threading.Thread(target=createProcess, args=(radarType, stateParamQueue, devName, devicesTbl[devName]["DATA_QUEUE"], {}, mqttc, algoCfg, {devName:devicesTbl[devName]})).start()
        devicesTbl[devName]["DATA_QUEUE"]={}

multiprocess_count = 0
def on_message3(mosq, obj, msg):
    global devicesTbl,config,aggregate_period,algoCfg,multiprocess_count
    # print(msg.payload)
    in_data = ''
    topicList = msg.topic.split('/')
    if topicList[-1] == "UPDATE_DEV_CONF":
        print("=====================================================================")
        print("Received device setting update request for: " + msg.payload.decode("utf-8"))
        print("=====================================================================")
        DEV = msg.payload.decode("utf-8").upper()
        if DEV in devicesTbl:
            print(DEV)
            del devicesTbl[DEV]
            del stateParam_sharedDict[DEV]
            del devicesTbl_sharedDict[DEV]
        return
    # if topicList[-1] == "ALGO_CONFIG":
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    #     pubPayload = {"STATUS":"UPDATED"}
    #     jsonData = json.dumps(pubPayload)
    #     mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
    # elif bool(algoCfg) == 0:
    #     _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
    #     algoCfg = _algoCfg.json()
    if topicList[-1] == "ALGO_CONFIG":
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
          print("algoCfg updating 1\n")
          try:
            while _algoCfg.status_code != 200:
              print("API call 1\n")
              _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
            algoCfg = _algoCfg.json()
            pubPayload = {"STATUS":"UPDATED"}
            jsonData = json.dumps(pubPayload)
            mqttc.publish("/GMT/DEV/ALGO_CONFIG/R", jsonData)
            algoCfg_sharedDict["DATA"] = algoCfg["DATA"]
            algoCfg_updated = 1
          except Exception as e:
            print(e)
        return
    elif bool(algoCfg) == 0:
        algoCfg_updated = 0
        _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
        while algoCfg_updated == 0:
            print("algoCfg updating 0\n")
            try:
              while _algoCfg.status_code != 200:
                print("API call 0\n")
                _algoCfg = requests.get("https://aswelfarehome.gaitmetrics.org/api/algo-config")
              algoCfg = _algoCfg.json()
              algoCfg_sharedDict["DATA"] = algoCfg["DATA"]
              algoCfg_updated = 1
            except Exception as e:
                print(e)

    devName = ''
    xShift = 0
    yShift = 0
    zShift = 2.5
    rotXDegree = 0
    rotYDegree = 0
    rotZDegree = 0
    # my_obj = eval(in_data)
    # print(in_data)
    # print(f"{msg.topic}, {msg.payload}")
    devName = topicList[3]
    # print(topicList)
    if devName not in devicesTbl:
        print("+++++++++++++++++++++++++++++")
        print(devName)
        print("+++++++++++++++++++++++++++++")
        devicesTbl[devName] = {}  
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)        
        sql = "SELECT TYPE, DEPLOY_X, DEPLOY_Y, DEPLOY_Z, ROT_X, ROT_Y, ROT_Z FROM Gaitmetrics.DEVICES WHERE MAC='%s'"%(devName)
        cursor.execute(sql)
        dbresult = cursor.fetchone() 
        if dbresult == None:
            print("Device not registered")
            return
        devicesTbl[devName] = dbresult
        devicesTbl[devName]["DATA_QUEUE"] = {}
        sql="UPDATE `DEVICES` SET `STATUS`='CONNECTED' WHERE MAC='"+devName+"';"
        cursor.execute(sql)
        connection.commit()        
        cursor.close()
        connection.close()        
    # print(devicesTbl)
    # if not devName == 'F412FAE261A4':
    #     return

    if multiprocess_count == 0:
        for n in range(1):
            Process(target=decode_multiProcess_publish, args=(stateParam_sharedDict, devicesTbl_sharedDict, algoCfg_sharedDict, processDataQueue, macQueue,)).start()
        multiprocess_count = 1

    while not processDataQueue.empty():
      pubPayload = processDataQueue.get()
      radarType = pubPayload["TYPE"]

      try: 
        print("my_list: ", pubPayload["DATA"])
        op = len(pubPayload["DATA"])
        if len(pubPayload["DATA"]) > 0:

            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            print(f"on message {op}", radarType)
        
            if radarType == 'wall':
                pubPayload["TYPE"]="WALL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/"+mac+"/DATA/WALL/JSON", jsonData)
                print(result)
            elif radarType == 'ceil':
                pubPayload["TYPE"]="CEIL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/CEIL/JSON", jsonData)
                print(result)
            elif radarType == 'vital':
                pubPayload["TYPE"]="VITAL"
                jsonData = json.dumps(pubPayload)
                print("publishing...")
                result = mqttc.publish("/GMT/DEV/" + mac + "/DATA/VITAL/JSON", jsonData)
                print(result)
            print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")              
            time.sleep(0.1)
            # dataBuffer.append(jsonData)
            dataBufferQueue.put(jsonData)
      except Exception as e:
        print(e)

    in_data = str(msg.payload).replace("b'", "").split(',')
    # print(topicList[-1])
    # print(in_data)
    for x in in_data:
        # print("Decoding hexadecimal\n")
        try:
            ts_str, hexD = x.split(':')
            ts = float(ts_str)
        except Exception as e:
            print(e)
            continue
        while 1:
            # print("Decoding hexadecimal 1\n")
            if "'" in hexD:
                hexD = hexD.replace("'", "")
            else:
                break
        # Error happens occasionally when converting the raw data representation,
        # may require error analysis in future to find out the actual cause.
        try:
            byteAD = bytearray.fromhex(hexD)
        except:
            continue
        # if len(hexD)>1:
            # print(hexD)  
        devicesTbl[devName]["DATA_QUEUE"][ts_str]=byteAD
    devicesTbl[devName]["DATA_QUEUE"] = dict(sorted(devicesTbl[devName]["DATA_QUEUE"].items()))
    # DQ = list(devicesTbl[devName]["DATA_QUEUE"])
    # print(devName, DQ)
    # print(float(DQ[-1])-float(DQ[0]))
    # if float(DQ[-1])-float(DQ[0]) < aggregate_period:
        # return
    # else: 
        # print("Chunk time: ", float(DQ[-1])-float(DQ[0]))
    # try:
    if topicList[-1] == "LF" or topicList[-1] == "RAW":
        # th = threading.Thread(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],))
        # th.start()
        # Process(target=decode_process_publish, args=(devName, devicesTbl[devName]["DATA_QUEUE"],)).start()
    # except:
    #     print("Error Processing")
        # print("MAC: ", devicesTbl[devName])
        devicesTbl_sharedDict[devName] = devicesTbl[devName]
        macQueue.put(devName)
        devicesTbl[devName]["DATA_QUEUE"]={}

def on_connect(client, userdata, flags, rc):
    print("MQTT server connected")
    client.publish("/GMT/USVC/DECODE_PUBLISH/STATUS","CONNECTED",1,True)
    
def on_publish(client, userdata, rc):
    # create function for callback
    print("data published \n")
    pass

def on_disconnect(client, userdata, rc):
    print("MQTT Disconnected")
    os._exit(1)

def WatchDog():
    time.sleep(2)
    while 1:
        time.sleep(30)
        print("WatchiDog checking")
        DATA_BUFF_LEN = len(dataBuffer)
        print(DATA_BUFF_LEN)
        print("WDT Checking if data publishing is still working, dataBuffer[%d]" % DATA_BUFF_LEN)
        if DATA_BUFF_LEN == 0:
            print("Empty data buffer, restart")
            os._exit(2)
        else:
            dataBuffer.clear()

def WatchDog1(dataBuf):
    time.sleep(2)
    while 1:
        time.sleep(30)
        print("WatchiDog checking")
        DATA_BUFF_LEN = len(dataBuf)
        print(DATA_BUFF_LEN)
        print("WDT Checking if data publishing is still working, dataBuffer[%d]" % DATA_BUFF_LEN)
        if DATA_BUFF_LEN == 0:
            print("Empty data buffer, restart")
            os._exit(2)
        else:
            dataBuf[:]=[]

def WatchDog2(dataBufferQueue):
    time.sleep(2)
    while 1:
        time.sleep(30)
        print("WatchiDog checking")
        dataBuf = []
        while not dataBufferQueue.empty():
            dataBuf.append(dataBufferQueue.get())
        DATA_BUFF_LEN = len(dataBuf)
        print(DATA_BUFF_LEN)
        print("WDT Checking if data publishing is still working, dataBuffer[%d]" % DATA_BUFF_LEN)
        if DATA_BUFF_LEN == 0:
            print("Empty data buffer, restart")
            os._exit(2)
        else:
            dataBuf[:]=[]
          
if __name__ == '__main__':
    # pool1 = Pool(multiprocessing.cpu_count()-2)
    # print("Starting a pool of processes ...")
    atexit.register(cleanup)
    mqttc = mqtt.Client(clientID)
    mqttc.username_pw_set(userName, password=userPassword)
    mqttc.on_message = on_message3
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.will_set("/GMT/USVC/DECODE_PUBLISH/STATUS","DISCONNECTED",qos=1, retain=True)
    mqttc.connect(brokerAddress,1883,10)
    print("Subscribe to topic: "+ "/GMT/DEV/+/DATA/+/RAW/#")
    mqttc.subscribe("/GMT/DEV/+/DATA/+/RAW/#")
    print("Subscribe to topic: "+ "/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF")
    mqttc.subscribe("/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF")
    mqttc.subscribe("/GMT/DEV/ALGO_CONFIG")
    # for n in range(multiprocessing.cpu_count()-3):
    #     Process(target=decode_multiProcess_publish, args=(mqttClient_sharedList, stateParam_sharedDict, devicesTbl_sharedDict, algoCfg_sharedDict, macQueue, dataBufferQueue,)).start()
    time.sleep(1)
    print("Start mqtt receiving loop")
    # threading.Thread(target=process_dataQueue, args=(stateParamQueue, dataBufferQueue, )).start()
    # _thread.start_new_thread( WatchDog1, (sharedDataBuffer,))
    _thread.start_new_thread( WatchDog2, (dataBufferQueue,))
    # _thread.start_new_thread(publishProcessData, (processDataQueue, dataBufferQueue,))
    # _thread.start_new_thread( WatchDog, ())
    mqttc.loop_forever()


