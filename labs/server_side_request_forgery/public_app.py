from flask import Flask, request, render_template
import requests
import logging
import socket
import json
from datetime import datetime, timezone

app = Flask(__name__)


access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs/access.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)

access_logger.addHandler(handler)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def generate_pdf():
    url = request.form.get("url")

    resolved_ip = None

    try:
        hostname = url.split("//")[1].split("/")[0].split(":")[0]
        resolved_ip = socket.gethostbyname(hostname)

        response = requests.get(
            url,
            headers={"X-Internal-Request": "true"},
            timeout=3
        )


    except Exception:
        pass
    
    url = url.replace("\n", "").replace("\r", "")

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lab": "server_side_request_forgery",
        "ip": resolved_ip,
        "action": "SUCCESS",
        "metadata":{"user_input": url,}
        
    }

    access_logger.info(json.dumps(log_entry))



    return "PDF generated"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
