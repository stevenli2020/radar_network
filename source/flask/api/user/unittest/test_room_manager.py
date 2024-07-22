import unittest
from unittest.mock import MagicMock, patch
from user.roomManager import *  # Replace with your actual module name

class TestRoomFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = {
            'user': 'your_user',
            'password': 'your_password',
            'host': 'your_host',
            'database': 'your_database'
        }
        # Initialize any setup needed for tests

    def test_searchRoomDetail(self):
        # Mocking database connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        data = {'VALUE': 'test_value'}

        with patch('mysql.connector.connect', return_value=mock_connection):
            result = searchRoomDetail(data)
            self.assertIsInstance(result, defaultdict)
            self.assertIn('DATA', result)

    def test_getRoomData(self):
        # Mocking database connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        req = {'MAC': 'test_mac'}
        admin = True  # Change to False if testing non-admin case

        with patch('mysql.connector.connect', return_value=mock_connection):
            result = getRoomData(req, admin)
            self.assertIsInstance(result, dict)
            self.assertIn('DATA', result)

    def test_getSpecificRoomData(self):
        # Mocking database connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        req = {'ROOM_UUID': 'test_room_uuid'}
        admin = True  # Change to False if testing non-admin case

        with patch('mysql.connector.connect', return_value=mock_connection):
            result = getSpecificRoomData(req, admin)
            self.assertIsInstance(result, dict)
            self.assertIn('DATA', result)

    # Add more tests for other functions similarly

if __name__ == '__main__':
    unittest.main()

