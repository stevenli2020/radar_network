import unittest
from unittest.mock import patch, MagicMock
import mysql.connector
from user.getSaveData import getSaveRawData, getHistOfVitalData, getAnalyticDataofPosture, getSummaryDataofPosition

class TestGetSaveData(unittest.TestCase):

  @patch('mysql.connector.connect')
  def test_getSaveRawData(self, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, '2024-07-20 14:00:00', '00:11:22:33:44:55', 'timestamp1:rawdata1,timestamp2:rawdata2')
    ]
    data = {
        'CUSTOM': 0,
        'TIME': '30 MINUTE',
        'DEVICEMAC': '00:11:22:33:44:55'
    }

    # Act
    result = getSaveRawData(data)

    # Assert
    self.assertIn('DATA', result)
    self.assertIsInstance(result['DATA'], list)

  @patch('mysql.connector.connect')
  def test_getHistOfVitalData(self, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [
        ('00:11:22:33:44:55,00:11:22:33:44:56',),
        None
    ]
    data = {
        'ROOM_UUID': 'some-room-uuid',
        'CUSTOM': 0,
        'TIME': 'HOUR'
    }

    # Act
    result = getHistOfVitalData(data)

    # Assert
    self.assertIn('ERROR', result)

  @patch('mysql.connector.connect')
  def test_getAnalyticDataofPosture(self, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [
        ('00:11:22:33:44:55,00:11:22:33:44:56',),
        (60, 30)
    ]
    mock_cursor.fetchall.side_effect = [
        [('2024-07-20 14:00:00', 1, 1)],
        [('2024-07-20 14:00:00', 1, 1)]
    ]
    data = {
        'ROOM_UUID': 'some-room-uuid'
    }

    # Act
    result = getAnalyticDataofPosture(data)

    # Assert
    self.assertIn('DATA', result)

  @patch('mysql.connector.connect')
  def test_getSummaryDataofPosition(self, mock_connect):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [
        (10, 10, 1),
        (5, 5, 0, 0)
    ]
    mock_cursor.fetchall.return_value = [
        ('5,5', 10)
    ]
    data = {
        'DEVICEMAC': '00:11:22:33:44:55',
        'TIME': 'HOUR'
    }

    # Act
    result = getSummaryDataofPosition(data)

    # Assert
    self.assertIn('DATA', result)
    self.assertIsInstance(result['DATA'], list)

if __name__ == '__main__':
  unittest.main()
