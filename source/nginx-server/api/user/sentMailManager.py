import mysql.connector
from user.config import config, domain_url

from collections import defaultdict
from user.email.gmail import sentMail
from user.email.gmailTemplate import emailTemplate
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

config = config()

def resetPasswordLink(data):
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    print(data)
    if not re.fullmatch(regex, str(data)):        
        sql = "SELECT LOGIN_NAME,CODE,EMAIL FROM USERS WHERE ID='%s'"%(data)
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        if not dbresult:
            result['ERROR'].append({'ID': 'User not found'})
            return result
        body = emailTemplate(dbresult[0], domain_url() + "/resetPassword?user="+str(dbresult[0])+"&code="+str(dbresult[1])+"&mode=reset", "reset")
        sentMail(dbresult[2], 'Request to change password', body)        
    else:
        sql = "SELECT LOGIN_NAME,CODE,EMAIL FROM USERS WHERE EMAIL='%s'"%(data)
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        if not dbresult:
            result['ERROR'].append({'EMAIL': 'Email not found'})
            return result
        body = emailTemplate(dbresult[0], domain_url() + "/resetPassword?user="+str(dbresult[0])+"&code="+str(dbresult[1])+"&mode=reset", "reset")
        sentMail(dbresult[2], 'Request to change password', body)
    cursor.close()
    connection.close()
    result['DATA'].append({"CODE": 0})    
    return result