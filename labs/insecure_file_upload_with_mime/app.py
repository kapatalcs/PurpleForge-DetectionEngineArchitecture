import os 
from flask import Flask, render_template, request, session 
from datetime import datetime,timezone 
import json
import logging


app = Flask(__name__) 
app.secret_key = "supersecret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)

handler = logging.FileHandler("labs/insecure_file_upload_with_mime/logs/access.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)

access_logger.addHandler(handler)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)




@app.route("/upload", methods=["GET", "POST"]) 
def upload(): 
    ip = request.headers.get(
    "X-Forwarded-For",
    request.remote_addr
    )

    if request.method == "POST": 
        file = request.files["file"]

        mime_category = (
            file.content_type.split("/")[0]
            if file.content_type and "/" in file.content_type
            else "unknown"
            )
        
        if not file:
            action = "FAIL"
        elif not file.content_type.startswith("image/"):
            action = "FAIL"
        else:
            path = os.path.join(UPLOAD_FOLDER, file.filename) 
            file.save(path)
            action = "SUCCESS"

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip": ip,
            "lab": "insecure_file_upload_with_mime",
            "resource": "/upload",
            "action": action,
            "metadata": {
                "mime_category": mime_category,
                "extension": os.path.splitext(file.filename)[1][1:],
    }
}
        access_logger.info(json.dumps(log_entry))
        return "File uploaded"
    files = os.listdir(UPLOAD_FOLDER) 
    return render_template("upload.html", files=files)

if __name__ == "__main__": 
    app.run(host="127.0.0.1", port=5003, debug=False, use_reloader=False)