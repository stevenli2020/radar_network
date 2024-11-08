from sqlite3 import Timestamp, connect
import time
from datetime import datetime, timedelta

# import redis
from typing import List, Dict
from flask import Flask, render_template, request, redirect, url_for, jsonify
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
from user.getSaveData import getHistOfWallData
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
from user.roomManager import getRoomsAlerts
from user.roomManager import getDeviceConfig
from user.roomManager import setDeviceConfig
from user.roomManager import readRoomAlertsData
from user.roomManager import getFilterLocationHistoryData
from user.roomManager import updateFilterLocationHistoryData
from user.roomManager import updateRoomLocationOnMapData

# add new room
from user.roomManager import addNewRoomDetail
from user.roomManager import updateRoomDetail
from user.roomManager import deleteRoomDetail
from user.roomManager import searchRoomDetail
from user.roomManager import update_active_room

# upload img
from user.uploadManager import uploadImgFile
from werkzeug.utils import secure_filename

# search device api
from user.searchDevManager import searchDevDetail
from user.laymanDetail import getLaymanData

from user.user_settings import get_data_types
from user.user_settings import get_alert_configurations
from user.user_settings import set_alert_configurations

from user.mqtt_manager import trigger_alert

from user.algo_configs import (
    get_algo_configs,
    add_algo_config,
    update_algo_configs,
    delete_algo_config,
)
from user.notifier_manager import get_notifier, add_notifier, delete_notifier

import os
import json
from redis import Redis
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

app = Flask(__name__)
CORS(app)
redis = Redis(host="redis", port=6379)
app.register_blueprint(blueprint, url_prefix="")

config = config()
upload_folder = os.path.join("static", "uploads")

app.config["UPLOAD"] = upload_folder
app.config["JWT_SECRET_KEY"] = (
    "gaitmetrics_jwt_12345"  # Change this to a random secret key
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)

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
# @app.route('/api', methods=['GET', 'POST'])
# def hello():
#     return render_template('Home.html')

# Detail page
# @app.route('/api/Detail', methods=['GET', 'POST'])
# def Detail():
#     return render_template('Detail.html')


# get one register device details
@app.route("/api/getRegDevice", methods=["POST"])
@jwt_required()
def getRegDevice():
    # count = get_hit_count()
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            return getregisterDevice(data)
        else:
            return {"ERROR": "Not authorized!"}


# get all register device details
@app.route("/api/getRegDevices", methods=["POST"])
@jwt_required()
def getRegDevices():
    # count = get_hit_count()
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        print(f"login: {login}, admin: {admin}")
        # with open("logs", "a+") as myfile:
        #     myfile.write("login: "+str(login)+", admin: "+str(admin)+"\n")
        if login:
            return getregisterDeviceLists(data, admin)
        else:
            return {"ERROR": "Not authorized!"}


# register new device
@app.route("/api/addNewDevice", methods=["POST"])
@jwt_required()
def addNewDevice():
    # count = get_hit_count()
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            if admin:
                return registerNewDevice(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Not authorized!"}


# register new device
@app.route("/api/addDeviceCredential", methods=["POST"])
@jwt_required()
def addDeviceCredential():
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            if admin:
                return insertDeviceCredential(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Not authorized!"}


# update register device detail
@app.route("/api/updateDevice", methods=["POST"])
@jwt_required()
def updateDevice():
    # count = get_hit_count()
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            if admin:
                return updateDeviceDetail(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Not authorized!"}


# delete register device
@app.route("/api/deleteDevice", methods=["POST"])
@jwt_required()
def deleteDevice():
    # count = get_hit_count()
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            if admin:
                return deleteDeviceDetail(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Not authorized!"}


# register device mac address and date/time to save raw data
@app.route("/api/saveDevice", methods=["GET", "POST"])
@jwt_required()
def registerDeviceData():
    # count = get_hit_count()
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            return registerDeviceSaveRaw(data)
    return render_template("SaveDevice.html")


# users management page url
@app.route("/api/usersManagement", methods=["GET", "POST"])
@jwt_required()
def usersManagement():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if admin:
                    return addNewUser(data)
                else:
                    return {"ERROR": "Not authorized!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}
    return render_template("Users.html")


# update user
@app.route("/api/updateUser", methods=["POST"])
@jwt_required()
def updateUser():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if admin:
                    return updateUserDetails(data)
                else:
                    return {"ERROR": "Not authorized!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


# delete user
@app.route("/api/deleteUser", methods=["POST"])
@jwt_required()
def deleteUser():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if admin:
                    return deleteUserDetails(data)
                else:
                    return {"ERROR": "Not authorized!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


# get all users
@app.route("/api/getAllUsers", methods=["POST"])
@jwt_required()
def getAllUsers():
    if request.method == "POST":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            if admin:
                return requestAllUsers()
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Not authorized!"}


# get specific user
@app.route("/api/getSpecificUser", methods=["POST"])
@jwt_required()
def getSpecificUsers():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                return requestSpecificUser(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


# get list of device status
@app.route("/api/getStatusDevice", methods=["POST"])
@jwt_required()
def getStatusDevice():
    if request.method == "POST":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            return getDeviceListsOfStatus()
        else:
            return {"ERROR": "Not authorized!"}


# get list of save device data
@app.route("/api/getSaveDeviceRawData", methods=["POST"])
@jwt_required()
def getSaveDeviceRawData():
    if request.method == "POST":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            return getDeviceListsOfSaveRawData()
        else:
            return {"ERROR": "Not authorized!"}


# get one list of save device data
@app.route("/api/getSaveDevice", methods=["POST"])
@jwt_required()
def getSaveDevice():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                return getSaveDeviceDetail(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


# update save device time
@app.route("/api/updateSaveDeviceTime", methods=["POST"])
@jwt_required()
def updateSaveDeviceTime():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                return updateSaveDeviceDataTime(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


# delete save device time
@app.route("/api/deleteSaveDeviceTime", methods=["POST"])
@jwt_required()
def deleteSaveDeviceTime():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                return deleteSaveDeviceDataTime(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/updateData", methods=["POST"])
def updateData():
    if request.method == "POST":
        now = datetime.now()
        data = request.json
        X = data["x"]
        Y = data["y"]
        Z = data["z"]
        dbName = data["deviceName"] + now.strftime("%Y%m%d")
        createTable(dbName)
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        # cursor.execute("CREATE TABLE customers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), address VARCHAR(255))")
        # connection.commit()

        # cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO " + dbName + " (X, Y, Z) VALUES (%s,%s,%s)",
            (json.dumps(X), json.dumps(Y), json.dumps(Z)),
        )
        connection.commit()
        cursor.close()
        connection.close()
        # print(data)
    return "success"


# retrieve saved data of trackdata and vitals
@app.route("/api/getHistOfVital", methods=["POST"])
@jwt_required()
def getData():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
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
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getHistOfWall", methods=["POST"])
@jwt_required()
def getWallData():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                data["API"] = "WALL_DATA"
                cached_result = get_data_from_redis(data)
                if cached_result:
                    return cached_result

                result = getHistOfWallData(data)
                cache_data(data, json.dumps(result))
                return result
                # return getHistOfVitalData(data)
                # return getSaveRawData(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


# retrieve summary saved data of vitals
@app.route("/api/getAnalyticData", methods=["POST"])
@jwt_required()
def getAnalyticData():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                data["API"] = "ANALYTICS_DATA"
                cached_result = get_data_from_redis(data)
                if cached_result:
                    return cached_result

                result = getAnalyticDataofPosture(data)
                cache_data(data, json.dumps(result))
                return result
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/refreshAnalyticData", methods=["POST"])
@jwt_required()
def refreshAnalyticData():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                data["API"] = "ANALYTICS_DATA"

                result = getAnalyticDataofPosture(data)
                # cache_data(data, json.dumps(result))
                return result
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


def get_data_from_redis(data):
    # Convert the JSON data to a string to use it as a key
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
@app.route("/api/getSummaryPositionData", methods=["POST"])
@jwt_required()
def getSummaryPositionData():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                data["API"] = "SUMMARY_POSITION"
                cached_result = get_data_from_redis(data)
                if cached_result:
                    return cached_result

                result = getSummaryDataofPosition(data)
                cache_data(data, json.dumps(result))
                return result
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


# update password url
@app.route("/api/updatePassword", methods=["GET", "POST"])
def updatePassword():
    if request.method == "POST":
        data = request.json
        if data:
            return addPassword(data)
        else:
            return {"ERROR": "Empty json!"}
    return render_template("updatePassword.html")


# login
@app.route("/api/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        if data:
            result = signIn(data)
            if result.get("DATA") and len(result.get("DATA")) > 0:
                access_token = create_access_token(identity=result.get("DATA")[0])
                return (
                    jsonify(
                        access_token=access_token,
                        type=result.get("DATA")[0].get("TYPE"),
                        username=result.get("DATA")[0].get("Username"),
                    ),
                    200,
                )
            else:
                return result
        else:
            return {"ERROR": "Empty json!"}
    return render_template("login.html")


@app.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    if request.method == "POST":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            return signOut(current_user)
        else:
            return {"ERROR": "Not authorized!"}


# sent email to user's email
@app.route("/api/sentEmail", methods=["POST"])
@jwt_required()
def sentEmail():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if admin:
                return resetPasswordLink(data["USER_ID"])
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getRoomDetails", methods=["POST"])
@jwt_required()
def getRoomDetails():
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        print(login, admin)
        if login:
            return getRoomData(current_user, admin)
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/getRoomDetail", methods=["POST"])
@jwt_required()
def getRoomDetail():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                return getSpecificRoomData(data, admin)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/uploadLogo", methods=["POST"])
@jwt_required()
def uploadLogo():
    if request.method == "POST":
        file = request.files["logo"]
        filename = "logo.png"
        file.save(os.path.join(app.config["UPLOAD"], filename))
        return {"image_source": filename}


@app.route("/api/uploadImg", methods=["POST"])
@jwt_required()
def uploadImg():
    if request.method == "POST":
        if "add-room-img" in request.files:
            file = request.files["add-room-img"]
        else:
            file = request.files["update-room-img"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD"], filename))
        img = os.path.join(app.config["UPLOAD"], filename)
        suffix = datetime.now().strftime("%y%m%d%H%M%S%f")[:-3]
        # suffix = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
        new = os.path.join(app.config["UPLOAD"], suffix)
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


@app.route("/api/getDevSuggestion", methods=["POST"])
@jwt_required()
def getDevSuggestion():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if admin:
                return searchDevDetail(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getRoomSuggestion", methods=["POST"])
@jwt_required()
def getRoomSuggestion():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if admin:
                return searchRoomDetail(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/addNewRoom", methods=["POST"])
@jwt_required()
def addNewRoom():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if admin:
                return addNewRoomDetail(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/updateRoom", methods=["POST"])
@jwt_required()
def updateRoom():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if admin:
                return updateRoomDetail(data, app.config["UPLOAD"])
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/deleteRoom", methods=["POST"])
@jwt_required()
def deleteRoom():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if admin:
                return deleteRoomDetail(data, app.config["UPLOAD"])
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getRLMacRoom", methods=["POST"])
@jwt_required()
def getRLMacRoom():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                return getRLMacRoomData(data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/test", methods=["GET"])
def getTest():
    if request.method == "GET":
        return {"ERROR": "Empty json!"}


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


@app.route("/api/Detail/Layman", methods=["GET"])
def Layman():
    room_id = request.args.get("room", type=str)
    if room_id is not None:

        # Render the HTML template with the data and ID
        return render_template("Layman.html")
    else:
        return "Room ID not provided."


@app.route("/api/LocationHistory", methods=["GET"])
def LocationHistory():
    room_id = request.args.get("room", type=str)
    if room_id is not None:

        # Render the HTML template with the data and ID
        return render_template("LocationHistory.html")
    else:
        return "Room ID not provided."


@app.route("/api/getFilterLocationHistory", methods=["POST"])
@jwt_required()
def getFilterLocationHistory():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if "room_id" in data:
                    return getFilterLocationHistoryData(data.get("room_id"))
                else:
                    return {"ERROR": "Please provide room id!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/updateFilterLocationHistory", methods=["POST"])
@jwt_required()
def updateFilterLocationHistory():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if "room_id" in data:
                    return updateFilterLocationHistoryData(
                        data.get("room_id"), data=data.get("data", [])
                    )
                else:
                    return {"ERROR": "Please provide room id!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getRoomLaymanDetail", methods=["POST"])
@jwt_required()
def getRoomLaymanDetail():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if "room_id" in data and "eow" in data:
                    return getLaymanData(data.get("eow"), data.get("room_id"))
                else:
                    return {"ERROR": "Please provide room id!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getRoomAlerts", methods=["POST"])
@jwt_required()
def getRoomAlerts():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if "room_id" in data:
                    return getRoomAlertsData(
                        data.get("room_id"),
                        unread=data.get("unread", False),
                        set=data.get("set", False),
                    )
                else:
                    return {"ERROR": "Please provide room id!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getCriticalAlerts", methods=["POST"])
def getAlerts():
    if request.method == "POST":
        data = request.json
        if data:
            if "MAC" in data:
                return getRoomsAlerts(data.get("MAC"), unread=data.get("unread", True))
            else:
                return {"ERROR": "Please provide MAC!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getDeviceConfig", methods=["POST"])
def getConfig():
    if request.method == "POST":
        data = request.json
        if data:
            if "MAC" in data:
                return getDeviceConfig(data.get("MAC"))
            else:
                return {"ERROR": "Please provide MAC!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/setDeviceConfig", methods=["POST"])
def setConfig():
    if request.method == "POST":
        data = request.json
        if data:
            if "MAC" in data:
                return setDeviceConfig(data.get("MAC"), flag=data.get("flag", True))
            else:
                return {"ERROR": "Please provide MAC!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/readRoomAlerts", methods=["POST"])
@jwt_required()
def readRoomAlerts():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                if "ROOM_UUID" in data:
                    return readRoomAlertsData(data.get("ROOM_UUID"))
                else:
                    return {"ERROR": "Please provide room uuid!"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/updateRoomLocationOnMap", methods=["POST"])
@jwt_required()
def updateRoomLocationOnMap():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login and admin:
                return updateRoomLocationOnMapData(data=data.get("data", []))
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/getMQTTClientID", methods=["POST"])
@jwt_required()
def getMQTTClientIDAPI():
    if request.method == "POST":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            client_id = getMQTTClientID(current_user.get("Username"))
            if client_id:
                return {"DATA": {"client_id": client_id}}
            else:
                return {"ERROR": "Cannot retrieve client ID"}
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/setClientConnection", methods=["POST"])
@jwt_required()
def setClientConnectionAPI():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login:
                result = setClientConnection(data.get("client_id"))
                if result:
                    return {"DATA": "Connected"}
                else:
                    return {"ERROR": "Cannot set connect"}
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Cannot set connect"}


@app.route("/api/getDataTypes", methods=["POST"])
@jwt_required()
def get_data_types_API():
    if request.method == "POST":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            data_types = get_data_types()
            if data_types:
                return data_types
            else:
                return {"ERROR": "Cannot retrieve data types"}
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/getAlertConfigurations", methods=["POST"])
@jwt_required()
def get_alert_configurations_API():
    if request.method == "POST":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login:
            alert_configurations = get_alert_configurations()
            if alert_configurations:
                return alert_configurations
            else:
                return {"ERROR": "Cannot retrieve alert configurations"}
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/setAlertConfigurations", methods=["POST"])
@jwt_required()
def set_alert_configurations_API():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login and admin:
                return set_alert_configurations(data=data.get("data", []))
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/triggerAlert", methods=["POST"])
@jwt_required()
def trigger_alert_API():
    if request.method == "POST":
        data = request.json
        if data:
            current_user = get_jwt_identity()
            login, admin = auth(current_user)
            if login and admin:
                return trigger_alert(data=data)
            else:
                return {"ERROR": "Not authorized!"}
        else:
            return {"ERROR": "Empty json!"}


@app.route("/api/algo-config", methods=["GET"])
def algo_config():
    if request.method == "GET":
        # Return all configurations
        return get_algo_configs()


@app.route("/api/algo-config", methods=["POST"])
@jwt_required()
def new_algo_config():
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login and admin:
            key = data.get("CONFIG_KEY")
            value = data.get("VALUE")
            if not key:
                return {"ERROR": "Data required!"}
            return add_algo_config(key, value)
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/algo-config", methods=["PUT"])
@jwt_required()
def update_algo_config():
    data = request.json
    current_user = get_jwt_identity()
    login, admin = auth(current_user)
    if login and admin:
        return update_algo_configs(data.get("data", []))
    else:
        return {"ERROR": "Not authorized!"}


@app.route("/api/algo-config/<key>", methods=["DELETE"])
@jwt_required()
def algo_config_key(key):
    if request.method == "DELETE":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login and admin:
            return delete_algo_config(key)
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/notifier", methods=["GET"])
@jwt_required()
def get_notifier_api():
    if request.method == "GET":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login and admin:
            return get_notifier()
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/notifier", methods=["POST"])
@jwt_required()
def add_notifier_api():
    if request.method == "POST":
        data = request.json
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login and admin:
            print(data)
            email = data.get("EMAIL")
            if not email:
                return {"ERROR": "Data required!"}
            return add_notifier(email)
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/notifier/<email>", methods=["DELETE"])
@jwt_required()
def delete_notifier_api(email):
    if request.method == "DELETE":
        current_user = get_jwt_identity()
        login, admin = auth(current_user)
        if login and admin:
            return delete_notifier(email)
        else:
            return {"ERROR": "Not authorized!"}


@app.route("/api/updateRoomActive", methods=["POST"])
@jwt_required()
def update_active_room_api():
    data = request.json
    current_user = get_jwt_identity()
    login, admin = auth(current_user)
    if login and admin:
        room_uuid = data.get("ROOM_UUID")
        active = data.get("ACTIVE")
        if not room_uuid:
            return {"ERROR": "Data required!"}
        return update_active_room(room_uuid, active)
    else:
        return {"ERROR": "Not authorized!"}


if __name__ == "__main__":
    app.run(debug=True, threaded=True)

# def checkTable(dbName):
#     connection = mysql.connector.connect(**config)
