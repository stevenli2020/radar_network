import unittest
from unittest.mock import patch, MagicMock

from user.user_settings import get_data_types, get_alert_configurations, set_alert_configurations  # Update with your actual module name

class TestUserSettings(unittest.TestCase):

  @patch('mysql.connector.connect')
  def test_get_data_types(self, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.__iter__.return_value = iter([
        (1, 'data_key_1', 'Data Label 1'),
        (2, 'data_key_2', 'Data Label 2')
    ])

    result = get_data_types()
    expected_result = {
        "DATA": [
            {"ID": 1, "value": 'data_key_1', "label": 'Data Label 1'},
            {"ID": 2, "value": 'data_key_2', "label": 'Data Label 2'}
        ]
    }
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_get_alert_configurations(self, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.__iter__.return_value = iter([
        (1, 'data_type_1', 'mode_1', 10, 20, 30),
        (2, 'data_type_2', 'mode_2', 15, 25, 35)
    ])

    result = get_alert_configurations()
    expected_result = {
        "DATA": [
            {"ID": 1, "DATA_TYPE": 'data_type_1', "MODE": 'mode_1', "MIN_DATA_POINT": 10, "MAX_DATA_POINT": 20, "THRESHOLD": 30},
            {"ID": 2, "DATA_TYPE": 'data_type_2', "MODE": 'mode_2', "MIN_DATA_POINT": 15, "MAX_DATA_POINT": 25, "THRESHOLD": 35}
        ]
    }
    self.assertEqual(result, expected_result)

  @patch('mysql.connector.connect')
  def test_set_alert_configurations(self, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    data = [
        {"DATA_TYPE": 'data_type_1', "MODE": 'mode_1', "MIN_DATA_POINT": 10, "MAX_DATA_POINT": 20, "THRESHOLD": 30},
        {"DATA_TYPE": 'data_type_2', "MODE": 'mode_2', "MIN_DATA_POINT": 15, "MAX_DATA_POINT": 25, "THRESHOLD": 35}
    ]

    result = set_alert_configurations(data)
    self.assertEqual(result, {"RESULT": True})

    # Verify the DELETE and INSERT SQL commands were executed
    self.assertEqual(mock_cursor.execute.call_count, 3)  # 1 DELETE + 2 INSERTS
    mock_cursor.execute.assert_any_call("DELETE FROM `ALERT_CONFIGS`;")
    mock_cursor.execute.assert_any_call(
        "INSERT INTO `ALERT_CONFIGS` (`DATA_TYPE`,`MODE`,`MIN_DATA_POINT`,`MAX_DATA_POINT`,`THRESHOLD`) VALUES ('data_type_1','mode_1','10','20','30');")
    mock_cursor.execute.assert_any_call(
        "INSERT INTO `ALERT_CONFIGS` (`DATA_TYPE`,`MODE`,`MIN_DATA_POINT`,`MAX_DATA_POINT`,`THRESHOLD`) VALUES ('data_type_2','mode_2','15','25','35');")

if __name__ == '__main__':
    unittest.main()
