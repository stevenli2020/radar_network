import mysql.connector
from user.config import config, vernemq
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

config = config()

def getLaymanData(room_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    result = {
        "data":{
            "room_id":room_id,
            "sleeping_hour":{
                "average":"2h08m",
                "longest":"4h0m",
                "shortest":"0m",
                "previous_average":"2h08m"
            },
            "bed_time":{
                "average":"2h08m",
                "longest":"4h0m",
                "shortest":"0m",
                "previous_average":"2h08m"
            },
            "wake_up_time":{
                "average":"2h08m",
                "longest":"4h0m",
                "shortest":"0m",
                "previous_average":"2h08m"
            },
            "time_in_bed":{
                "average":"2h08m",
                "longest":"4h0m",
                "shortest":"0m",
                "previous_average":"2h08m"
            },
            "in_room":{
                "average":"2h08m",
                "longest":"4h0m",
                "shortest":"0m",
                "previous_average":"2h08m"
            }
        }
    }
    # sql = "SELECT * FROM Gaitmetrics.ROOM_DETAILS WHERE ROOM_UUID=%s"%(room_id)
    # cursor.execute(sql)
    # result["data"]["room_name"] = cursor.fetchone()
    #     print(data)
    #     result["DATA"].append({"id":data["Id"]})
    # result["DATA"] =  #[{"MAC": MAC} for (MAC) in cursor]
    
    cursor.close()
    connection.close()
    return result
