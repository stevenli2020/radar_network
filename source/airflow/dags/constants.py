import datetime

NAP_START_LIMIT = datetime.time(6, 0, 0)
NAP_END_LIMIT = datetime.time(20, 0, 0)

DEFAULT_NIGHT_START = "18:00"
DEFAULT_NIGHT_END = "06:00"

THRESHOLD = 60 * 45
SLEEPING_THRESHOLD = 60 * 45
DISRUPTION_THRESHOLD = 60 * 2.5
DISRUPTION_RESTORE_THRESHOLD = 60 * 10

MIN_BREATH_RATE = 8
MIN_HEART_RATE = 40

NOT_IN_ROOM_THRESHOLD = 60 * 3

data = {
    "aswelfarehome": {
        "host": "143.198.199.16",
        "port": "2203",
        "domain_url": "https://aswelfarehome.gaitmetrics.org",
        "server_name": "Aswelfarehome",
    },
    "htx": {
        "host": "128.199.240.137",
        "port": "2203",
        "domain_url": "https://htx.gaitmetrics.org",
        "server_name": "HTX",
    },
    "testbed": {
        "host": "139.59.254.201",
        "port": "2203",
        "domain_url": "https://testbed.gaitmetrics.org",
        "server_name": "Testbed",
    },
    "nec": {
        "host": "54.64.188.137",
        "port": "2203",
        "domain_url": "http://nec.gaitmetrics.org",
        "server_name": "NEC",
    },
}


def config(key):
    return {
        "user": "flask",
        "password": "CrbI1q)KUV1CsOj-",
        "host": data[key]["host"],
        "port": data[key]["port"],
        "database": "Gaitmetrics",
    }


def vernemq(key):
    return {
        "user": "flask",
        "password": "CrbI1q)KUV1CsOj-",
        "host": data[key]["host"],
        "port": data[key]["port"],
        "database": "vernemq_db",
    }


def domain_url(key):
    return data[key]["domain_url"]


def server_name(key):
    return data[key]["server_name"]
