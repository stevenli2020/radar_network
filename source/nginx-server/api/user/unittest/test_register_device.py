import unittest
from unittest.mock import patch, MagicMock
from user.registerDevice import (  # Replace 'registerDevice' with the name of your module file.
    getRLMacRoomData,
    getregisterDeviceLists,
    getregisterDevice,
    registerNewDevice,
    updateDeviceDetail,
    deleteDeviceDetail,
    insertDeviceCredential
)

class TestDatabaseFunctions(unittest.TestCase):

  @patch('registerDevice.mysql.connector.connect')
  def test_getRLMacRoomData(self, mock_connect):
    # Setup mock
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ('00:11:22:33:44:55', 'TypeA', 1.0, 2.0)
    ]
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    req = {'ROOM_UUID': 'test-room-uuid'}
    result = getRLMacRoomData(req)
    
    expected_result = {
        "DATA": [{"MAC": '00:11:22:33:44:55', "TYPE": 'TypeA', "DEPLOY_X": 1.0, "DEPLOY_Y": 2.0}]
    }
    self.assertEqual(result, expected_result)

  @patch('registerDevice.mysql.connector.connect')
  def test_getregisterDeviceLists_admin(self, mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, '00:11:22:33:44:55', 'Device1', 'TypeA', 'ACTIVE', 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, None, 'Desc1', 'Room1')
    ]
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    req = {'ID': 'test-user-id'}
    result = getregisterDeviceLists(req, admin=True)
    
    expected_result = {
        "DATA": [{
            "Id": 1, "MAC": '00:11:22:33:44:55', "NAME": 'Device1', "TYPE": 'TypeA', "STATUS": 'ACTIVE',
            "DEPLOY_X": 1.0, "DEPLOY_Y": 2.0, "DEPLOY_Z": 3.0, "ROT_X": 4.0, "ROT_Y": 5.0, "ROT_Z": 6.0,
            "LAST DATA": None, "DESCRIPTION": 'Desc1', "ROOM_NAME": 'Room1'
        }]
    }
    self.assertEqual(result, expected_result)

  @patch('registerDevice.mysql.connector.connect')
  def test_registerNewDevice_success(self, mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    req = {
        'MAC': '00:11:22:33:44:55', 'NAME': 'NewDevice', 'DEPLOY_X': 1.0, 'DEPLOY_Y': 2.0, 'DEPLOY_Z': 3.0,
        'ROT_X': 4.0, 'ROT_Y': 5.0, 'ROT_Z': 6.0, 'DEPLOY_LOC': 'room-uuid', 'DEVICE_TYPE': 'TypeA', 'DESCRIPTION': 'Test device'
    }
    with patch('registerDevice.Add_Vernemq_db') as mock_add_vernemq:
      result = registerNewDevice(req)
      expected_result = {"DATA": [{"MESSAGE": "Device 00:11:22:33:44:55 registered successfully"}]}
      self.assertEqual(result, expected_result)
      mock_add_vernemq.assert_called_once_with(req['MAC'])

  @patch('registerDevice.mysql.connector.connect')
  def test_updateDeviceDetail_success(self, mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, '00:11:22:33:44:55', 'Device1', 'TypeA', 'ACTIVE', 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, None, 'Desc1', 'room-uuid')
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    req = {
        'MAC': '00:11:22:33:44:55', 'NAME': 'UpdatedDevice', 'DEVICE_TYPE': 'TypeB', 'DEPLOY_X': 1.5, 'DEPLOY_Y': 2.5,
        'DEPLOY_Z': 3.5, 'ROT_X': 4.5, 'ROT_Y': 5.5, 'ROT_Z': 6.5, 'DEPLOY_LOC': 'new-room-uuid', 'DESCRIPTION': 'Updated description', 'Id': 1
    }
    result = updateDeviceDetail(req)
    expected_result = {"DATA": [{"MESSAGE": "Device 00:11:22:33:44:55 updated successfully"}]}
    self.assertEqual(result, expected_result)

  @patch('registerDevice.mysql.connector.connect')
  def test_deleteDeviceDetail(self, mock_connect):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    req = {'Id': 1, 'MAC': '00:11:22:33:44:55'}
    result = deleteDeviceDetail(req)
    expected_result = {"CODE": 0}
    self.assertEqual(result, expected_result)

  @patch('registerDevice.mysql.connector.connect')
  def test_insertDeviceCredential(self, mock_connect):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    req = {
        'username': '00:11:22:33:44:55',
        'password': 'testpassword'
    }
    result = insertDeviceCredential(req)
    expected_result = {"DATA": ["Device credential inserted!"]}
    self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
