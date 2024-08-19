import unittest
from unittest.mock import patch, MagicMock
import json
import time
from datetime import datetime, timedelta

from run import *

class TestMQTTScripts(unittest.TestCase):

  @patch('mysql.connector.connect')
  def test_get_room_uuid_by_mac(self, mock_connect):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [{'ID': 1, 'ROOM_UUID': 'uuid1234'}]
    
    mac = '00:11:22:33:44:55'
    result = get_room_uuid_by_mac(mac)
    
    mock_cursor.execute.assert_called_once_with(
        f"SELECT rd.ID,rrm.ROOM_UUID FROM RL_ROOM_MAC rrm LEFT JOIN ROOMS_DETAILS rd ON rrm.ROOM_UUID=rd.ROOM_UUID WHERE rrm.MAC='{mac}';"
    )
    self.assertEqual(result, {'ID': 1, 'ROOM_UUID': 'uuid1234'})

  @patch('mysql.connector.connect')
  def test_insert_alert(self, mock_connect):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    
    mock_cursor.fetchone.return_value = {'count': 0}
    
    room_id = 1
    msg = {
        "URGENCY": "2",
        "TYPE": "1",
        "DETAILS": "Test Alert"
    }
    
    insert_alert(room_id, msg)
    
    check_sql = f"""
        SELECT COUNT(*) AS count
        FROM ALERT
        WHERE ROOM_ID = '{room_id}'
        AND URGENCY = '{msg["URGENCY"]}'
        AND TYPE = '{msg["TYPE"]}'
        AND DETAILS = '{msg["DETAILS"]}'
        AND TIMESTAMP >= NOW() - INTERVAL 15 SECOND
    """
    
    mock_cursor.execute.assert_any_call(check_sql)
    self.assertTrue(mock_cursor.execute.called)
    self.assertTrue(mock_connection.commit.called)

  @patch('paho.mqtt.client.Client')
  def test_connect_mqtt(self, mock_client):
    mock_instance = mock_client.return_value
    
    client = connect_mqtt()
    
    mock_instance.username_pw_set.assert_called_once_with('py-client1', 'c764eb2b5fa2d259dc667e2b9e195218')
    mock_instance.connect.assert_called_once_with('143.198.199.16', 1883)
    self.assertEqual(client, mock_instance)

  @patch('paho.mqtt.client.Client')
  @patch('mysql.connector.connect')
  def test_on_message(self, mock_connect, mock_client):
    mock_mqtt_instance = mock_client.return_value
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [{'ID': 1, 'ROOM_UUID': 'uuid1234'}]
    
    # Sample message and topic
    topic = "/GMT/DEV/00:11:22:33:44:55/ALERT"
    msg_payload = {
        "URGENCY": "2",
        "TYPE": "1",
        "DETAILS": "Test Alert"
    }
    
    mock_msg = MagicMock()
    mock_msg.topic = topic
    mock_msg.payload.decode.return_value = json.dumps(msg_payload)
    
    subscribe(mock_mqtt_instance)
    mock_mqtt_instance.on_message(mock_mqtt_instance, None, mock_msg)
    
    real_topic = pub_topic1.replace("ROOM_UUID", 'uuid1234')
    mock_mqtt_instance.publish.assert_called_with(real_topic, "New alert")

  def test_check_sol_threshold(self):
    first_ts = time.time() - 40  # 40 seconds ago
    curr_ts = time.time()
    
    result = check_sol_threshold(first_ts, curr_ts)
    self.assertTrue(result)

    first_ts = time.time() - 20  # 20 seconds ago
    curr_ts = time.time()
    
    result = check_sol_threshold(first_ts, curr_ts)
    self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()