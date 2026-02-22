import requests

url = "http://127.0.0.1:5003/upload"



files = {
    "file": ("blank.pdf", open(r"attacks\mime_spoofing\blank.pdf", "rb"), "image/png")
}

response = requests.post(url, files=files)

print(response.status_code)
print(response.text)