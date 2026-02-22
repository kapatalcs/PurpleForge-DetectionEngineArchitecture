from flask import Flask

app = Flask(__name__)

@app.route("/secret")
def secret():
    return " INTERNAL SECRET DATA "

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6000, debug=False, use_reloader=False)