import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from user.registerDeviceSaveData import registerDeviceSaveRaw

class TestRegisterDeviceSaveRaw(unittest.TestCase):

  @patch('mysql.connector.connect')
  @patch('registerDeviceSaveData.datetime')
  def test_registerDeviceSaveRaw_custom_0(self, mock_datetime, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    now = datetime(2024, 7, 21, 12, 0, 0)
    mock_datetime.now.return_value = now

    data = {
        'DEVICEMAC': '00:11:22:33:44:55',
        'TIME': 'week',
        'CUSTOM': 0
    }

    mock_cursor.fetchall.side_effect = [[]]  # No existing records

    # Act
    result = registerDeviceSaveRaw(data)

    # Assert
    expected_expiry = now + timedelta(weeks=1)
    mock_cursor.execute.assert_called_with("INSERT INTO RL_DEVICE_SAVE (MAC, Expired) VALUES (%s, %s)", (data['DEVICEMAC'], expected_expiry))
    mock_connection.commit.assert_called_once()
    self.assertEqual(result, {"DATA": [{"MESSAGE": "Device 00:11:22:33:44:55 registered succefully"}]})

  @patch('mysql.connector.connect')
  @patch('registerDeviceSaveData.datetime')
  def test_registerDeviceSaveRaw_custom_1(self, mock_datetime, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    now = datetime(2024, 7, 21, 12, 0, 0)
    mock_datetime.now.return_value = now

    data = {
        'DEVICEMAC': '00:11:22:33:44:55',
        'TIME': '2024-07-21T12:00:00-2024-07-28T12:00:00',
        'CUSTOM': 1
    }

    mock_cursor.fetchall.side_effect = [[]]  # No existing records

    # Act
    result = registerDeviceSaveRaw(data)

    # Assert
    ts = data['TIME'].split('-')
    mock_cursor.execute.assert_called_with("INSERT INTO RL_DEVICE_SAVE (MAC, Start, Expired) VALUES (%s, %s, %s)", (data['DEVICEMAC'], ts[0], ts[1]))
    mock_connection.commit.assert_called_once()
    self.assertEqual(result, {"DATA": [{"MESSAGE": "Device 00:11:22:33:44:55 registered succefully"}]})

  @patch('mysql.connector.connect')
  def test_registerDeviceSaveRaw_time_not_selected(self, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    data = {
        'DEVICEMAC': '00:11:22:33:44:55',
        'TIME': 'please select',
        'CUSTOM': 0
    }

    # Act
    result = registerDeviceSaveRaw(data)

    # Assert
    self.assertEqual(result, {'ERROR': [{'CODE': 0, 'TIME': 'Please select Time'}]})

  @patch('mysql.connector.connect')
  def test_registerDeviceSaveRaw_mac_empty(self, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    data = {
        'DEVICEMAC': '',
        'TIME': 'week',
        'CUSTOM': 0
    }

    # Act
    result = registerDeviceSaveRaw(data)

    # Assert
    self.assertEqual(result, {'ERROR': [{'CODE': 0, 'MAC': 'MAC is Empty'}]})

if __name__ == '__main__':
  unittest.main()
