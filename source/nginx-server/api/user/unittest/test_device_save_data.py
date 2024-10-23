import unittest
from unittest.mock import patch, Mock
import mysql.connector
from datetime import datetime
import pytz
from tzlocal import get_localzone

# Assuming the functions are in a module named `module_name`
from user.DeviceSaveData import getDeviceListsOfStatus, getDeviceListsOfSaveRawData, getSaveDeviceDetail, updateSaveDeviceDataTime, deleteSaveDeviceDataTime

class TestDeviceSaveData(unittest.TestCase):

  @patch('mysql.connector.connect')
  @patch('tzlocal.get_localzone', return_value=pytz.utc)
  def test_getDeviceListsOfStatus(self, mock_get_localzone, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.return_value = None
    mock_cursor.__iter__.return_value = iter([
        ('mac1', 'status1', datetime(2023, 1, 1, tzinfo=pytz.utc), 'name1'),
        ('mac2', 'status2', None, 'name2')
    ])
    
    expected_result = {
        'DATA': [
            {'MAC': 'mac1', 'STATUS': 'status1', 'TIMESTAMP': datetime(2023, 1, 1, tzinfo=pytz.utc), 'NAME': 'name1'},
            {'MAC': 'mac2', 'STATUS': 'status2', 'TIMESTAMP': None, 'NAME': 'name2'}
        ]
    }
    result = getDeviceListsOfStatus()
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_getDeviceListsOfSaveRawData(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.return_value = None
    mock_cursor.__iter__.return_value = iter([
        (1, 'mac1', 'start1', 'expired1'),
        (2, 'mac2', 'start2', 'expired2')
    ])
    
    expected_result = {
        'DATA': [
            {'Id': 1, 'MAC': 'mac1', 'Start': 'start1', 'Expired': 'expired1'},
            {'Id': 2, 'MAC': 'mac2', 'Start': 'start2', 'Expired': 'expired2'}
        ]
    }
    result = getDeviceListsOfSaveRawData()
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_getSaveDeviceDetail(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.return_value = None
    mock_cursor.__iter__.return_value = iter([
        (1, 'mac1', 'start1', 'expired1')
    ])
    
    req = {'Id': '1'}
    expected_result = {
        'DATA': [{'Id': 1, 'MAC': 'mac1', 'Start': 'start1', 'Expired': 'expired1'}]
    }
    result = getSaveDeviceDetail(req)
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_updateSaveDeviceDataTime(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    
    req = {'Id': '1', 'MAC': 'mac1', 'TIME': '2023-01-01-2024-01-01'}
    expected_result = {'CODE': 0}
    
    result = updateSaveDeviceDataTime(req)
    self.assertEqual(result, expected_result)
    mock_cursor.execute.assert_called_with("UPDATE RL_DEVICE_SAVE SET Start='%s', Expired='%s', MAC='%s' WHERE Id='%s'" % ('2023-01-01', '2024-01-01', 'mac1', '1'))

  @patch('mysql.connector.connect')
  def test_deleteSaveDeviceDataTime(self, mock_connect):
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    
    req = {'Id': '1'}
    expected_result = {'CODE': 0}
    
    result = deleteSaveDeviceDataTime(req)
    self.assertEqual(result, expected_result)
    mock_cursor.execute.assert_called_with("DELETE FROM RL_DEVICE_SAVE WHERE Id='%s'" % '1')

if __name__ == '__main__':
  unittest.main()
