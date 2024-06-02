from sqlite3 import Timestamp, connect
import time
from datetime import datetime, timedelta
# import redis
from typing import List, Dict
from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import mysql.connector
import json
from blueprint import blueprint
from user.createDatabase import createTable
# Save Raw Data
from user.registerDeviceSaveData import registerDeviceSaveRaw
from user.DeviceSaveData import getDeviceListsOfSaveRawData
from user.DeviceSaveData import getDeviceListsOfStatus
from user.DeviceSaveData import getSaveDeviceDetail
from user.DeviceSaveData import updateSaveDeviceDataTime
from user.DeviceSaveData import deleteSaveDeviceDataTime
from user.getSaveData import getHistOfVitalData
from user.getSaveData import getAnalyticDataofPosture
from user.getSaveData import getSummaryDataofPosition
# from user.getSaveData import getSaveRawData
# Register New Device
from user.registerDevice import getregisterDeviceLists
from user.registerDevice import getregisterDevice
from user.registerDevice import registerNewDevice
from user.registerDevice import updateDeviceDetail
from user.registerDevice import deleteDeviceDetail
from user.registerDevice import getRLMacRoomData
from user.registerDevice import insertDeviceCredential
# from user.registerDevice import getDeviceStatusData
# add New User
from user.usersManagement import addNewUser
from user.usersManagement import updateUserDetails
from user.usersManagement import deleteUserDetails
from user.usersManagement import requestAllUsers
from user.usersManagement import requestSpecificUser
from user.usersManagement import getMQTTClientID
from user.usersManagement import setClientConnection

# update Password
from user.passwordManager import addPassword
# login
from user.authManager import signIn
from user.authManager import signOut
from user.authManager import auth
from user.config import config
# sent Mail manager
from user.sentMailManager import resetPasswordLink
# from flask_mysqldb import MySQL
# get Room details
from user.roomManager import getRoomData
from user.roomManager import getSpecificRoomData
from user.roomManager import getRoomAlertsData
from user.roomManager import readRoomAlertsData
from user.roomManager import getFilterLocationHistoryData
from user.roomManager import updateFilterLocationHistoryData
from user.roomManager import updateRoomLocationOnMapData

# add new room
from user.roomManager import addNewRoomDetail
from user.roomManager import updateRoomDetail
from user.roomManager import deleteRoomDetail
from user.roomManager import searchRoomDetail
# upload img
from user.uploadManager import uploadImgFile
from werkzeug.utils import secure_filename
# search device api
from user.searchDevManager import searchDevDetail
from user.laymanDetail import getLaymanData

from user.user_settings import get_data_types
from user.user_settings import get_alert_configurations
from user.user_settings import set_alert_configurations

import os
import json
from redis import Redis

app = Flask(__name__)
CORS(app)
redis = Redis(host='redis', port=6379)
app.register_blueprint(blueprint, url_prefix="")
# app.config['MYSQL_HOST'] = "db"
# app.config['MYSQL_USER'] = "root"
# app.config['MYSQL_PASSWORD'] = "14102022"
# app.config['MYSQL_DB'] = "Gaimetric"
# config = {
#     'user': 'flask',
#     'password': 'CrbI1q)KUV1CsOj-',
#     'host': 'db',
#     'port': '3306',
#     'database': 'Gaitmetric'
# }
config = config()
upload_folder = os.path.join('static', 'uploads')

app.config['UPLOAD'] = upload_folder
def test_table() -> List[Dict]:
    # config = {
    #     'user': 'root',
    #     'password': '220522',
    #     'host': 'db',
    #     'port': '3306',
    #     'database': 'Gaimetric'
    # }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM test_table')
    results = [{name: color} for (name, color) in cursor]
    cursor.close()
    connection.close()

    return results

# mysql = MySQL(app)
# cache = redis.Redis(host='redis', port=6379)

# def get_hit_count():
#     retries = 5
#     while True:
#         try:
#             return cache.incr('hits')
#         except redis.exceptions.ConnectionError as exc:
#             if retries == 0:
#                 raise exc
#             retries -= 1
#             time.sleep(0.5)

# def insertDB(sql):
#     connection = mysql.connector.connect(**config)
#     cursor = connection.cursor()
#     cursor.execute(sql)
#     connection.commit()
#     cursor.close()
#     connection.close()

# Home page
@app.route('/api', methods=['GET', 'POST'])
def hello():
    return render_template('Home.html')

# Detail page
@app.route('/api/Detail', methods=['GET', 'POST'])
def Detail():
    return render_template('Detail.html')

# get one register device details 
@app.route('/api/getRegDevice', methods=['POST'])
def getRegDevice():
    # count = get_hit_count()
    if request.method == 'POST': 
        data = request.json  
        login, admin = auth(data)
        if login:        
            return getregisterDevice(data)
        else:
            return {"ERROR": 'Not authorized!'}

# get all register device details
@app.route('/api/getRegDevices', methods=['POST'])
def getRegDevices():
    # count = get_hit_count()
    if request.method == 'POST': 
        data = request.json 
        login, admin = auth(data)
        print(f'login: {login}, admin: {admin}') 
        # with open("logs", "a+") as myfile:
        #     myfile.write("login: "+str(login)+", admin: "+str(admin)+"\n")
        if login:               
            return getregisterDeviceLists(data, admin)
        else:
            return {"ERROR": 'Not authorized!'}

# register new device
@app.route('/api/addNewDevice', methods=['POST'])
def addNewDevice():
    # count = get_hit_count()
    if request.method == 'POST':
        data = request.json 
        login, admin = auth(data)
        if login:
            if admin:                   
                return registerNewDevice(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Not authorized!'}
        
# register new device
@app.route('/api/addDeviceCredential', methods=['POST'])
def addDeviceCredential():
    if request.method == 'POST':
        data = request.json 
        login, admin = auth(data)
        if login:
            if admin:                   
                return insertDeviceCredential(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Not authorized!'}

#update register device detail
@app.route('/api/updateDevice', methods=['POST'])
def updateDevice():
    # count = get_hit_count()
    if request.method == 'POST':
        data = request.json   
        login, admin = auth(data)   
        if login:
            if admin:             
                return updateDeviceDetail(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Not authorized!'}

#delete register device
@app.route('/api/deleteDevice', methods=['POST'])
def deleteDevice():
    # count = get_hit_count()
    if request.method == 'POST':
        data = request.json    
        login, admin = auth(data)           
        if login:
            if admin:        
                return deleteDeviceDetail(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Not authorized!'}


# register device mac address and date/time to save raw data
@app.route('/api/saveDevice', methods=['GET', 'POST'])
def registerDeviceData():
    # count = get_hit_count()
    if request.method == 'POST':
        data = request.json      
        login, admin = auth(data)
        if login:            
            return registerDeviceSaveRaw(data)
    return render_template('SaveDevice.html')

# users management page url
@app.route('/api/usersManagement', methods=['GET', 'POST'])
def usersManagement():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                if admin:
                    return addNewUser(data)
                else:
                    return {"ERROR": 'Not authorized!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
    return render_template('Users.html')

# update user
@app.route('/api/updateUser', methods=['POST'])
def updateUser():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                if admin:
                    return updateUserDetails(data)
                else:
                    return {"ERROR": 'Not authorized!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# delete user
@app.route('/api/deleteUser', methods=['POST'])
def deleteUser():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                if admin:
                    return deleteUserDetails(data)
                else:
                    return {"ERROR": 'Not authorized!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# get all users
@app.route('/api/getAllUsers', methods=['POST'])
def getAllUsers():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                if admin:
                    return requestAllUsers()
                else:
                    return {"ERROR": 'Not authorized!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# get specific user
@app.route('/api/getSpecificUser', methods=['POST'])
def getSpecificUsers():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                return requestSpecificUser(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# get list of device status
@app.route('/api/getStatusDevice', methods=['POST'])
def getStatusDevice():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                return getDeviceListsOfStatus()
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# get list of save device data
@app.route('/api/getSaveDeviceRawData', methods=['POST'])
def getSaveDeviceRawData():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                return getDeviceListsOfSaveRawData()
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# get one list of save device data
@app.route('/api/getSaveDevice', methods=['POST'])
def getSaveDevice():
    if request.method == 'POST':
        data = request.json        
        if data:                 
            login, admin = auth(data)
            if login:
                return getSaveDeviceDetail(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# update save device time
@app.route('/api/updateSaveDeviceTime', methods=['POST'])
def updateSaveDeviceTime():
    if request.method == 'POST':
        data = request.json
        if data:                 
            login, admin = auth(data)
            if login:
                return updateSaveDeviceDataTime(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# delete save device time
@app.route('/api/deleteSaveDeviceTime', methods=['POST'])
def deleteSaveDeviceTime():
    if request.method == 'POST':
        data = request.json
        if data:                 
            login, admin = auth(data)
            if login:
                return deleteSaveDeviceDataTime(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

@app.route('/api/updateData', methods=["POST"])
def updateData():
    if request.method == 'POST':
        now = datetime.now()
        data = request.json
        X = data['x']
        Y = data['y']
        Z = data['z']
        dbName = data["deviceName"]+now.strftime("%Y%m%d")
        createTable(dbName)
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        # cursor.execute("CREATE TABLE customers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), address VARCHAR(255))")
        # connection.commit()
        
        # cursor = connection.cursor()
        cursor.execute("INSERT INTO "+dbName+" (X, Y, Z) VALUES (%s,%s,%s)", (json.dumps(X), json.dumps(Y), json.dumps(Z)))
        connection.commit()
        cursor.close()
        connection.close()
        # print(data)
    return 'success'

# retrieve saved data of trackdata and vitals
@app.route('/api/getHistOfVital', methods=["POST"])
def getData():
    if request.method == 'POST':
        data = request.json   
        if data:                 
            login, admin = auth(data)
            if login:
                data["API"] = "VITAL_DATA"
                cached_result = get_data_from_redis(data)
                if cached_result:
                    return cached_result
                
                result = getHistOfVitalData(data) 
                cache_data(data, json.dumps(result))
                return result
                # return getHistOfVitalData(data)  
                # return getSaveRawData(data)  
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}  

# retrieve summary saved data of vitals
@app.route('/api/getAnalyticData', methods=["POST"])
def getAnalyticData():
    if request.method == 'POST':
        data = request.json   
        if data:                 
            login, admin = auth(data)
            if login:
                data["API"] = "ANALYTICS_DATA"
                cached_result = get_data_from_redis(data)
                if cached_result:
                    return cached_result
                
                result = getAnalyticDataofPosture(data)  
                cache_data(data, json.dumps(result))
                return result
                # return getAnalyticDataofPosture(data)  
                # return getSaveRawData(data)  
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'} 

def get_data_from_redis(data):
    # Convert the JSON data to a string to use it as a key
    del data["Username"]
    del data["CODE"]
    del data["TYPE"]
    del data["ID"]
    key = str(data)
    cached_data = redis.get(key)
    if cached_data:
        return json.loads(cached_data)
    else:
        return None

def cache_data(data, result):
    key = str(data)
    redis.set(key, result)
    redis.expire(key, 3600)

# retrieve summary saved data of trackdata
@app.route('/api/getSummaryPositionData', methods=["POST"])
def getSummaryPositionData():
    if request.method == 'POST':
        data = request.json   
        if data:                 
            login, admin = auth(data)
            if login:
                data["API"] = "SUMMARY_POSITION"
                cached_result = get_data_from_redis(data)
                if cached_result:
                    return cached_result
                
                result = getSummaryDataofPosition(data)  
                cache_data(data, json.dumps(result))
                return result
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'} 

        
# update password url
@app.route('/api/updatePassword', methods=['GET', 'POST'])
def updatePassword():
    if request.method == 'POST':
        data = request.json  
        if data:                  
            return addPassword(data)
        else:
            return {"ERROR": 'Empty json!'}
    return render_template('updatePassword.html')

# login
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json  
        if data:                  
            return signIn(data)
        else:
            return {"ERROR": 'Empty json!'}
    return render_template('login.html')

@app.route('/api/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                return signOut(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

# sent email to user's email
@app.route('/api/sentEmail', methods=['POST'])
def sentEmail():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if admin:              
                return resetPasswordLink(data['USER_ID'])
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

@app.route('/api/getRoomDetails', methods=['POST'])
def getRoomDetails():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                return getRoomData(data, admin)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/getRoomDetail', methods=['POST'])
def getRoomDetail():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                return getSpecificRoomData(data, admin)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/uploadLogo', methods=['POST'])
def uploadLogo():
    if request.method == 'POST':
        file = request.files['logo']
        filename = "logo.png"
        file.save(os.path.join(app.config['UPLOAD'], filename))
        return {"image_source": filename}
    
@app.route('/api/uploadImg', methods=['POST'])
def uploadImg():
    if request.method == 'POST':
        if 'add-room-img' in request.files:
            file = request.files['add-room-img']
        else:
            file = request.files['update-room-img']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD'], filename))
        img = os.path.join(app.config['UPLOAD'], filename)
        suffix = datetime.now().strftime("%y%m%d%H%M%S%f")[:-3]
        # suffix = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
        new = os.path.join(app.config['UPLOAD'], suffix)
        os.rename(img, new)
        return {"image_source": suffix}
        # data = request.json  
        # if data:    
        #     login, admin = auth(data)
        #     if admin:              
        #         return uploadImgFile(data)
        #     else:
        #         return {"ERROR": 'Not authorized!'}
        # else:
        #     return {"ERROR": 'Empty json!'}

@app.route('/api/getDevSuggestion', methods=['POST'])
def getDevSuggestion():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if admin:              
                return searchDevDetail(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/getRoomSuggestion', methods=['POST'])
def getRoomSuggestion():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if admin:              
                return searchRoomDetail(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

@app.route('/api/addNewRoom', methods=['POST'])
def addNewRoom():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if admin:              
                return addNewRoomDetail(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

@app.route('/api/updateRoom', methods=['POST'])
def updateRoom():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if admin:              
                return updateRoomDetail(data, app.config['UPLOAD'])
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/deleteRoom', methods=['POST'])
def deleteRoom():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if admin:              
                return deleteRoomDetail(data, app.config['UPLOAD'])
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

@app.route('/api/getRLMacRoom', methods=['POST'])
def getRLMacRoom():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                return getRLMacRoomData(data)
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/test', methods=['GET'])
def getTest():
    if request.method == 'GET':
        return {"ERROR": 'Empty json!'}

# get device status
# @app.route('/api/getDeviceStatus', methods=['POST'])
# def getDeviceStatus():
#     if request.method == 'POST':
#         data = request.json  
#         if data:    
#             login, admin = auth(data)
#             if login:              
#                 return getDeviceStatusData(data, admin)
#             else:
#                 return {"ERROR": 'Not authorized!'}
#         else:
#             return {"ERROR": 'Empty json!'}

@app.route("/api/admin")
def admin():
    return redirect(url_for("home"))

@app.route('/api/Detail/Layman', methods=['GET'])
def Layman():
    room_id = request.args.get('room', type=str)
    if room_id is not None:

        # Render the HTML template with the data and ID
        return render_template('Layman.html')
    else:
        return "Room ID not provided."
    
@app.route('/api/LocationHistory', methods=['GET'])
def LocationHistory():
    room_id = request.args.get('room', type=str)
    if room_id is not None:

        # Render the HTML template with the data and ID
        return render_template('LocationHistory.html')
    else:
        return "Room ID not provided."

@app.route('/api/getFilterLocationHistory', methods=['POST'])
def getFilterLocationHistory():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                if "room_id" in data:              
                    return getFilterLocationHistoryData(data.get("room_id"))
                else:
                    return {"ERROR": 'Please provide room id!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/updateFilterLocationHistory', methods=['POST'])
def updateFilterLocationHistory():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                if "room_id" in data:              
                    return updateFilterLocationHistoryData(data.get("room_id"),data=data.get("data",[]))
                else:
                    return {"ERROR": 'Please provide room id!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

@app.route('/api/getRoomLaymanDetail', methods=['POST'])
def getRoomLaymanDetail():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = True ,True#auth(data)
            if login:              
                if "room_id" in data and "eow" in data:              
                    return getLaymanData(data.get("eow"),data.get("room_id"))
                else:
                    return {"ERROR": 'Please provide room id!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/getRoomAlerts', methods=['POST'])
def getRoomAlerts():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                if "room_id" in data:              
                    return getRoomAlertsData(data.get("room_id"),unread=data.get("unread",False),set=data.get("set",False))
                else:
                    return {"ERROR": 'Please provide room id!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/readRoomAlerts', methods=['POST'])
def readRoomAlerts():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                if "alerts" in data:              
                    return readRoomAlertsData(data.get("alerts"))
                else:
                    return {"ERROR": 'Please provide alerts id!'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}
        
@app.route('/api/updateRoomLocationOnMap', methods=['POST'])
def updateRoomLocationOnMap():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login and admin:              
                return updateRoomLocationOnMapData(data=data.get("data",[]))
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

@app.route('/api/getMQTTClientID', methods=['POST'])
def getMQTTClientIDAPI():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                client_id = getMQTTClientID(data.get("Username"))
                if (client_id):
                    return {"DATA":{
                        "client_id":client_id
                    }}
                else:
                    return {"ERROR": 'Cannot retrieve client ID'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Cannot retrieve client ID'}
        
@app.route('/api/setClientConnection', methods=['POST'])
def setClientConnectionAPI():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                result = setClientConnection(data.get("client_id"))
                if result:
                    return {"DATA": 'Connected'}
                else:
                    return {"ERROR": 'Cannot set connect'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Cannot set connect'}
        
@app.route('/api/getDataTypes', methods=['POST'])
def get_data_types_API():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                data_types = get_data_types()
                if (data_types):
                    return data_types
                else:
                    return {"ERROR": 'Cannot retrieve data types'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Not authorized!'}
        
@app.route('/api/getAlertConfigurations', methods=['POST'])
def get_alert_configurations_API():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login:              
                alert_configurations = get_alert_configurations()
                if (alert_configurations):
                    return alert_configurations
                else:
                    return {"ERROR": 'Cannot retrieve alert configurations'}
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Not authorized!'}

@app.route('/api/setAlertConfigurations', methods=['POST'])
def set_alert_configurations_API():
    if request.method == 'POST':
        data = request.json  
        if data:    
            login, admin = auth(data)
            if login and admin:              
                return set_alert_configurations(data=data.get("data",[]))
            else:
                return {"ERROR": 'Not authorized!'}
        else:
            return {"ERROR": 'Empty json!'}

if __name__ == "__main__":
    app.run(debug=True, threaded=True)

# def checkTable(dbName):
#     connection = mysql.connector.connect(**config)


