from flask import Flask, render_template, request, redirect
import sqlite3
import logging
from datetime import datetime, timezone
import os
import json

app = Flask(__name__)
app.secret_key = "weak-secret"

os.makedirs("labs/web_login/logs", exist_ok=True)

def get_db():
    return sqlite3.connect("labs/web_login/web_login_users.db")


access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)

handler = logging.FileHandler("labs/web_login/logs/access.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)

access_logger.addHandler(handler)

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db()
    cur = conn.cursor()

    query = f"""
    SELECT * FROM users
    WHERE username = '{username}'
    AND password = '{password}'
    """
    cur.execute(query)
    user = cur.fetchone()

    action = "LOGIN_SUCCESS" if user else "LOGIN_FAIL"

    ip = request.headers.get(
    "X-Forwarded-For",
    request.remote_addr
    )

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip":ip,
        "method": request.method,
        "path": request.path,
        "status": 200 if user else 401,
        "action": action,
        "user": username,
        "lab": "web_login"
    }

    access_logger.info(json.dumps(log_entry))


    if user:
        return redirect("/dashboard")
    else:
        return "Login failed", 401

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
