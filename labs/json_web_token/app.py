from flask import Flask, render_template, request, redirect, jsonify
import jwt
from datetime import datetime, timezone
import logging
import json
import base64

app = Flask(__name__)
SECRET_KEY = "supersecretkey"

users = {
    "user1": {"password": "1234", "role": "user"},
    "admin": {"password": "admin1234", "role": "admin"}

}

access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)

handler = logging.FileHandler("labs/json_web_token/logs/access.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)

access_logger.addHandler(handler)

def log_event(action, ip, user=None, resource=None, metadata=None,):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lab": "json_web_token",
        "action": action,
        "ip": ip,
        "user": user,
        "resource": resource,
        "metadata": metadata or {}
    }
    access_logger.info(json.dumps(log_entry))


@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    user = users.get(username)

    if not user or user["password"] != password:
        log_event(
            action="LOGIN_FAILED",
            ip=request.remote_addr,
            user=username,
            resource="/login",
        )
        return "Invalid credentials", 401


    log_event(
        action="LOGIN_SUCCESS",
        ip=request.remote_addr,
        user=username,
        resource="/login",
        metadata={"role": user["role"]}
    )
        

    token = jwt.encode(
        {
            "username": username,
            "role": user["role"]
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "token": token
    })

@app.route("/admin")
def admin():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return "Missing Authorization header", 401

    token = auth_header.split(" ")[1]

    try:
        parts = token.split(".")
        payload_b64 = parts[1]

        payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
        decoded = json.loads(payload_bytes.decode())

        header_b64 = parts[0]
        header_bytes = base64.urlsafe_b64decode(header_b64 + "==")
        header = json.loads(header_bytes.decode())

        log_event(
            action="JWT_RECEIVED",
            ip=request.headers.get("X-Forwarded-For", request.remote_addr),
            user=decoded.get("username"),
            resource="/admin",
            metadata={
                "alg": header.get("alg"),
                "role_in_token": decoded.get("role")
            }
        )

        if decoded.get("role") == "admin":
            return render_template("admin.html", user=decoded.get("username"))
        else:
            return "You are not admin", 403

    except Exception as e:
        return f"Token error: {str(e)}", 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005, debug=False, use_reloader=False)