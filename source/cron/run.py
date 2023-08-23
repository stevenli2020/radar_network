import schedule
import datetime
import time

nowtime = str(datetime.datetime.now())

def job(t):
    print("I'm working...", str(datetime.datetime.now()), t)

for i in ["04:00"]:
    schedule.every().monday.at(i).do(job, i)
    schedule.every().tuesday.at(i).do(job, i)
    schedule.every().wednesday.at(i).do(job, i)
    schedule.every().thursday.at(i).do(job, i)
    schedule.every().friday.at(i).do(job, i)
    schedule.every().saturday.at(i).do(job, i)
    schedule.every().sunday.at(i).do(job, i)

while True:
    schedule.run_pending()
    time.sleep(30)