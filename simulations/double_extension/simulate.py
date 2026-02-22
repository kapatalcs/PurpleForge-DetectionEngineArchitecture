import requests

url = "http://127.0.0.1:5002/upload"


files = {
    "file": ("images.jpg.png", open(r"attacks\double_extension\images.jpg.png", "rb"), "image/png")
}

response = requests.post(url, files=files)

print(response.status_code)
print(response.text)