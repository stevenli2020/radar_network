import unittest
from unittest.mock import patch, Mock
from collections import defaultdict
import uuid
import mysql.connector
from datetime import datetime
import pytz
from tzlocal import get_localzone

# Assuming the functions are in a module named `module_name`
from user.authManager import searchRoomDetail, getRoomData, getSpecificRoomData, addNewRoomDetail, updateRoomDetail, deleteRoomDetail, getRoomAlertsData, getRoomsAlerts, readRoomAlertsData, getFilterLocationHistoryData, updateFilterLocationHistoryData, updateRoomLocationOnMapData, auth, signIn, signOut

class TestAuthManager(unittest.TestCase):

  @patch('mysql.connector.connect')
  def test_searchRoomDetail(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [('Room1', 'uuid1'), ('Room2', 'uuid2')]
    
    data = {'VALUE': 'Room'}
    expected_result = {
        'DATA': [
            {'ROOM_NAME': 'Room1', 'ROOM_UUID': 'uuid1'},
            {'ROOM_NAME': 'Room2', 'ROOM_UUID': 'uuid2'}
        ]
    }
    result = searchRoomDetail(data)
    self.assertEqual(result, expected_result)
    mock_cursor.execute.assert_called_with("SELECT ROOM_NAME, ROOM_UUID FROM Gaitmetrics.ROOMS_DETAILS WHERE ROOM_NAME LIKE CONCAT('%', %s, '%')", ('Room',))

  @patch('mysql.connector.connect')
  @patch('tzlocal.get_localzone', return_value=pytz.utc)
  def test_getRoomData(self, mock_get_localzone, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (1, 'loc1', 'Room1', 'uuid1', 'img1', 'info1', 1, 1, 'status1', 1, datetime(2023, 1, 1), datetime(2023, 1, 1), 1, 1, 1, 1, 'mac1')
    ]
    
    req = {'ID': '123'}
    admin = True
    result = getRoomData(req, admin)
    self.assertTrue('DATA' in result)

  @patch('mysql.connector.connect')
  def test_addNewRoomDetail(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None
    
    data = {
        'ROOM_NAME': 'Room1',
        'ROOM_LOC': 'loc1',
        'ROOM_X': '1',
        'ROOM_Y': '1',
        'IMAGE_NAME': 'img1',
        'INFO': 'info1'
    }
    expected_result = {
        'DATA': [{'CODE': 0}]
    }
    result = addNewRoomDetail(data)
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_updateRoomDetail(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    
    data = {
        'ROOM_NAME': 'Room1',
        'ROOM_LOC': 'loc1',
        'ROOM_X': '1',
        'ROOM_Y': '1',
        'IMAGE_NAME': 'img1',
        'INFO': 'info1',
        'ROOM_UUID': 'uuid1',
        'O_IMAGE_NAME': 'old_img1'
    }
    uploadsLoc = '/uploads'
    expected_result = {
        'DATA': [{'CODE': 0}]
    }
    result = updateRoomDetail(data, uploadsLoc)
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_deleteRoomDetail(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = True
    
    data = {
        'ROOM_UUID': 'uuid1',
        'IMAGE_NAME': 'img1'
    }
    uploadsLoc = '/uploads'
    expected_result = {
        'DATA': [{'CODE': 0}]
    }
    result = deleteRoomDetail(data, uploadsLoc)
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_auth(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [(1, 'admin', '123', 'code', 1)]
    
    data = {
        'Username': 'admin',
        'ID': '1',
        'CODE': 'code',
        'TYPE': 1
    }
    login, admin = auth(data)
    self.assertTrue(login)
    self.assertTrue(admin)

  @patch('mysql.connector.connect')
  def test_signIn(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 'admin', '123', 'code', 1)
    
    data = {
        'LOGIN_NAME': 'admin',
        'PWD': '123'
    }
    result = signIn(data)
    self.assertTrue('DATA' in result)
    self.assertFalse('ERROR' in result)

  @patch('mysql.connector.connect')
  def test_signOut(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 'admin', 'code', 1)
    
    data = {
        'ID': '1',
        'CODE': 'code'
    }
    expected_result = {
        'DATA': [{'CODE': 0}]
    }
    result = signOut(data)
    self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
