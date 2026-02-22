from flask import Flask, request, render_template_string, redirect, session, g
import time
import json
import os
from datetime import datetime, timezone
import logging

app = Flask(__name__)
app.secret_key = "lab-secret"


log_path = "labs/ssti_access_control/logs"
os.makedirs(log_path, exist_ok=True)

access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{log_path}/access.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)

if not access_logger.handlers:
    access_logger.addHandler(handler)


users = {
    "user1": {"password": "1234", "role": "user"},
    "user2": {"password": "user123", "role": "user"},
    "admin": {"password": "admin", "role": "admin"},
}

templates_db = {
    1: {"owner": "user1", "content": "Hello {{ name }}"},
    2: {"owner": "user2", "content": "Welcome {{ name }}"},
    3:{"owner": "admin", "content": "Secret Admin Template"},
}


def emit_event(start_time, response):
    response_time_ms = int((time.time() - start_time) * 1000)

    ip = request.headers.get(
    "X-Forwarded-For",
    request.remote_addr
    )


    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lab": "ssti_access_control",
        "action": getattr(g, "action", None),
        "ip": ip,
        "user": session.get("user"),
        "metadata":{
        "role": session.get("role"),
        "method": request.method,
        "path": request.path,
        "resource_id": getattr(g, "resource_id", None),
        "resource_owner": getattr(g, "resource_owner", None),
        "body": request.form.to_dict(),
        "response_status": response.status_code,
        "response_size": response.content_length or 0,
        "response_time_ms": response_time_ms,
        }
    }

    access_logger.info(json.dumps(log_entry))


@app.before_request
def before_request():
    g.start_time = time.time()
    g.action = None
    g.resource_id = None
    g.resource_owner = None


@app.after_request
def after_request(response):
    emit_event(g.start_time, response)
    return response


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.get(username)

        if user and user["password"] == password:
            session["user"] = username
            session["role"] = user["role"]
            g.action = "login_success"
            return redirect("/dashboard")

        g.action = "login_failed"
        return "Login failed", 401

    return '''
        <h2>Login</h2>
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit">
        </form>
    '''

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return f"""
    <h1>Welcome {session['user']}</h1>
    <ul>
        <li><a href="/templates">My Templates</a></li>
        <li><a href="/render">Create Template</a></li>
    </ul>
    """


@app.route("/templates")
def list_templates():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    g.action = "template_list"

    user_templates = {
        tid: t for tid, t in templates_db.items()
        if t["owner"] == username
    }

    html = "<h2>My Templates</h2><ul>"

    for tid in user_templates:
        html += f'<li><a href="/template/{tid}">Template {tid}</a></li>'

    html += "</ul>"

    return html


# IDOR 

@app.route("/template/<int:template_id>")
def view_template(template_id):
    if "user" not in session:
        return redirect("/login")

    template = templates_db.get(template_id)
    if not template:
        return "Not found", 404

    g.action = "template_view"
    g.resource_id = template_id
    g.resource_owner = template["owner"]

    return template["content"]


# SSTI 

@app.route("/render", methods=["GET", "POST"])
def render_template_vuln():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        user_input = request.form.get("template")
        g.action = "template_render"

        return render_template_string(user_input)

    return '''
        <h2>Create Template</h2>
        <form method="post">
            Template Content: <input name="template"><br>
            <input type="submit">
        </form>
    '''


# MFLAC 

@app.route("/admin/panel")
def admin_panel():
    if "user" not in session:
        return redirect("/login")

    g.action = "admin_panel_access"

    return "Admin secrets here"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=False, use_reloader=False)