import unittest
from unittest.mock import patch, MagicMock
from collections import defaultdict
import re

from user.sentMailManager import *

# Assuming the resetPasswordLink function is in the script user_script.py
# from user_script import resetPasswordLink, regex

class TestResetPasswordLink(unittest.TestCase):

  @patch('user.email.gmail.sentMail')
  @patch('user.email.gmailTemplate.emailTemplate')
  @patch('mysql.connector.connect')
  @patch('user.config.domain_url')
  def test_reset_password_link(self, mock_domain_url, mock_connect, mock_email_template, mock_sent_mail):
    mock_domain_url.return_value = "http://example.com"
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Test case where data is not an email
    data = '1234'
    mock_cursor.fetchone.return_value = ('testuser', 'CODE1234', 'test@example.com')

    result = resetPasswordLink(data)
    expected_result = defaultdict(list, {'DATA': [{"CODE": 0}]})

    self.assertEqual(result, expected_result)
    mock_cursor.execute.assert_called_with("SELECT LOGIN_NAME,CODE,EMAIL FROM USERS WHERE ID='%s'" % data)
    mock_email_template.assert_called_with('testuser', 'http://example.com/resetPassword?user=testuser&code=CODE1234&mode=reset', 'reset')
    mock_sent_mail.assert_called_with('test@example.com', 'Request to change password', mock_email_template.return_value)

    # Test case where user ID not found
    mock_cursor.fetchone.return_value = None

    result = resetPasswordLink(data)
    expected_result = defaultdict(list, {'ERROR': [{'ID': 'User not found'}]})

    self.assertEqual(result, expected_result)

    # Test case where data is an email
    data = 'test@example.com'
    mock_cursor.fetchone.return_value = ('testuser', 'CODE1234', 'test@example.com')

    result = resetPasswordLink(data)
    expected_result = defaultdict(list, {'DATA': [{"CODE": 0}]})

    self.assertEqual(result, expected_result)
    mock_cursor.execute.assert_called_with("SELECT LOGIN_NAME,CODE,EMAIL FROM USERS WHERE EMAIL='%s'" % data)
    mock_email_template.assert_called_with('testuser', 'http://example.com/resetPassword?user=testuser&code=CODE1234&mode=reset', 'reset')
    mock_sent_mail.assert_called_with('test@example.com', 'Request to change password', mock_email_template.return_value)

    # Test case where email not found
    mock_cursor.fetchone.return_value = None

    result = resetPasswordLink(data)
    expected_result = defaultdict(list, {'ERROR': [{'EMAIL': 'Email not found'}]})

    self.assertEqual(result, expected_result)

    mock_cursor.close.assert_called()
    mock_connection.close.assert_called()

if __name__ == '__main__':
  unittest.main()
