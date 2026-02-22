import requests
import sys
import time

TARGET = "http://127.0.0.1:5000/login"

USERS = [
    "admin",
    "user1",
    "user2",
    "user3",
    "user4",
    "user5",
    "user6",
    "user7",
    "user8",
    "user9",
]

PASSWORD = "wrongpassword"

FAKE_IP = "10.10.10.15"
DELAY = 0.5
TIMEOUT = 3


def spray():
    for user in USERS:
        fake_ip = FAKE_IP

        headers = {
            "X-Forwarded-For": fake_ip
        }

        try:
            r = requests.post(
                TARGET,
                data={
                    "username": user,
                    "password": PASSWORD
                },
                headers=headers,
                timeout=TIMEOUT
            )

            print(f"[LIVE] {fake_ip} -> {user} ({r.status_code})")
            time.sleep(DELAY)

        except requests.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            sys.exit(2)


if __name__ == "__main__":
    spray()
    sys.exit(0)
