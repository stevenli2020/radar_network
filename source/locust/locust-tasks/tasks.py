from locust import HttpUser, task, between
import copy

user_auth = {
    "ID": "1",
    "Username": "sam",
    "CODE": "b17b335442917ed088cbea18393beadacc113bfbb6e9f2899c760228b977985d",
    "TYPE": "1"
}

class MyUser(HttpUser):
    wait_time = between(5, 15)
    host = "https://aswelfarehome.gaitmetrics.org"

    @task(10)
    def test_main(self):
      self.client.get("/")

    @task(10)
    def test_dashboard(self):
      self.client.get("/dashboard")

    @task(10)
    def test_rooms_api(self):
      self.client.post("/api/getRoomDetails", json=user_auth)

    @task(1)
    def test_devices_api(self):
      self.client.post("/api/getRegDevices", json=user_auth)

    @task(1)
    def test_users_api(self):
      self.client.post("/api/getAllUsers", json=user_auth)

    @task(3)
    def test_summary_api(self):
      data = copy.deepcopy(user_auth)
      data["ROOM_UUID"] = "f3f6a64bec6e4715925ab25c41fdbf02"
      data["CUSTOM"] = 0
      self.client.post("/api/getAnalyticData", json=data)

    @task(3)
    def test_vital_api(self):
      data = copy.deepcopy(user_auth)
      data["CUSTOM"] = 0
      data["TIME"] = "1 WEEK"
      data["ROOM_UUID"] = "f3f6a64bec6e4715925ab25c41fdbf02"
      self.client.post("/api/getHistOfVital", json=data)

    @task(3)
    def test_analysis_api(self):
      data = copy.deepcopy(user_auth)
      data["eow"] = "2024-04-28"
      self.client.post("/api/getRoomLaymanDetail", json=data)

    @task(3)
    def test_location_api(self):
      data = copy.deepcopy(user_auth)
      data["DEVICEMAC"] = "F412FAE252E8"
      data["TIME"] = "HOUR"
      data["CUSTOM"] = 0
      self.client.post("/api/getSummaryPositionData", json=data)