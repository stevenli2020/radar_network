import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from user.laymanDetail import getLaymanData

class TestLaymanDetail(unittest.TestCase):

  @patch('laymanDetail.get_data_from_analysis')
  @patch('laymanDetail.weekly_inroom_analysis')
  @patch('mysql.connector.connect')
  def test_getLaymanData(self, mock_connect, mock_weekly_analysis, mock_get_data):
    # Arrange
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.side_effect = [
        {"room_name": "Room 1@Location 1", "ID": 1, "MAC": "00:11:22:33:44:55,66:77:88:99:AA:BB"},
        {"max": "8h", "min": "6h", "average": "7h"},
        {"max": "10:00 PM", "min": "9:00 PM", "average": "9:30 PM"},
        {"max": "6:00 AM", "min": "5:00 AM", "average": "5:30 AM"},
        {"max": "9h", "min": "7h", "average": "8h"},
        {"max": "15h", "min": "10h", "average": "12h"},
        {"max": "5", "min": "2", "average": "3.5"},
        {"max": "20", "min": "12", "average": "16"},
        {"max": "80", "min": "60", "average": "70"},
        {"max": "4h", "min": "2h", "average": "3h"},
    ]
    
    mock_cursor.fetchall.side_effect = [
        [{"VALUE": "7h"}],
    ]
    
    mock_get_data.side_effect = [
        ("8h", "6h", "7h"),
        ("10:00 PM", "9:00 PM", "9:30 PM"),
        ("6:00 AM", "5:00 AM", "5:30 AM"),
        ("9h", "7h", "8h"),
        ("15h", "10h", "12h"),
        ("5", "2", "3.5"),
        ("20", "12", "16"),
        ("80", "60", "70"),
        ("4h", "2h", "3h"),
        ("8h", "6h", "7h"), # Previous week's data
        ("10:00 PM", "9:00 PM", "9:30 PM"),
        ("6:00 AM", "5:00 AM", "5:30 AM"),
        ("9h", "7h", "8h"),
        ("15h", "10h", "12h"),
        ("5", "2", "3.5"),
        ("20", "12", "16"),
        ("80", "60", "70"),
        ("4h", "2h", "3h")
    ]
    
    mock_weekly_analysis.return_value = [
        {"date": "2024-07-14", "total": 8*60, "social": 1*60, "moving": 2*60, "upright": 1*60, "laying": 4*60, "unknown": 0, "not_in_room": 16*60},
        # More days as needed
    ]
    
    date = "2024-07-21"
    room_uuid = "some-room-uuid"

    # Act
    result = getLaymanData(date, room_uuid)

    # Assert
    self.assertEqual(result["data"]["room_name"], "Room 1@Location 1")
    self.assertEqual(result["data"]["sensors"], ["00:11:22:33:44:55", "66:77:88:99:AA:BB"])
    self.assertEqual(result["data"]["sleeping_hour"]["average"], "7h")
    self.assertEqual(result["data"]["bed_time"]["average"], "9:30 PM")
    self.assertEqual(result["data"]["wake_up_time"]["average"], "5:30 AM")
    self.assertEqual(result["data"]["time_in_bed"]["average"], "8h")
    self.assertEqual(result["data"]["in_room"]["average"], "12h")
    self.assertEqual(result["data"]["sleep_disruption"]["average"], "3.5")
    self.assertEqual(result["data"]["breath_rate"]["average"], "16")
    self.assertEqual(result["data"]["heart_rate"]["average"], "70")
    self.assertEqual(result["data"]["disrupt_duration"]["average"], "3h")
    self.assertEqual(len(result["data"]["inroom_analysis"]), 7)

if __name__ == '__main__':
    unittest.main()
