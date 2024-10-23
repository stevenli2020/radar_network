data = {
    "prod": {
        'host': 'db',
        'port': '3306',
    },
    "aswelfarehome": {
        'host': '143.198.199.16',
        'port': '2203',
    },
    "htx": {
        'host': '128.199.240.137',
        'port': '2203',
    },
    "testbed": {
        'host': '139.59.254.201',
        'port': '2203',
    },
    "nec": {
        'host': '54.64.188.137',
        'port': '2203',
    },
}

key = "prod"

def config():
    return {
        'user': 'flask',
        'password': 'CrbI1q)KUV1CsOj-',
        'host': data[key]['host'],
        'port': data[key]['port'],
        'database': 'Gaitmetrics'
    }

def vernemq():
    return {
        'user': 'flask',
        'password': 'CrbI1q)KUV1CsOj-',
        'host': data[key]['host'],
        'port': data[key]['port'],
        'database': 'vernemq_db'
    }

def domain_url():
    return "https://aswelfarehome.gaitmetrics.org"

def server_ip():
    return "143.198.199.16"
