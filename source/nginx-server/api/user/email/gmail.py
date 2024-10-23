import smtplib
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError


# wolryshamgswgvzu

# SCOPES = [
#         "https://www.googleapis.com/auth/gmail.send"
#     ]
# flow = InstalledAppFlow.from_client_secrets_file(
#             'credentials.json', SCOPES)
# creds = flow.run_local_server(port=0)
# def sentMail(recipient, subject, body):
#     service = build('gmail', 'v1', credentials=creds)
#     # message = MIMEText('This is the body of the email')
#     # message['to'] = 'recipient@gmail.com'
#     # message['subject'] = 'Email Subject'
#     message = MIMEText(body)
#     message['to'] = recipient
#     message['subject'] = subject
#     create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
#     try:
#         message = (service.users().messages().send(userId="me", body=create_message).execute())
#         print(F'sent message to {message} Message Id: {message["id"]}')
#     except HTTPError as error:
#         print(F'An error occurred: {error}')
#         message = None


sender_email = "www.gaitmetric.com.sg@gmail.com"
sender_password = "wolryshamgswgvzu"
# recipient_email = "recipient@gmail.com"
def sentMail(recipient, subject, body):
    # subject = "Hello from Python"
    # body = """
    # <html>
    # <body>
    #     <p>This is an <b>HTML</b> email sent from Python using the Gmail SMTP server.</p>
    # </body>
    # </html>
    # """
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = recipient
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient, html_message.as_string())
    server.quit()