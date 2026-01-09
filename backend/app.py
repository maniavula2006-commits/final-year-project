from flask import Flask, render_template, request
import subprocess
import sys
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
APP_DIR = os.path.join(BASE_DIR, "..", "app")

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home", methods=["POST"])
def home():
    return render_template("home.html")

@app.route("/select")
def select_mode():
    return render_template("select_mode.html")

@app.route("/run", methods=["POST"])
def run_mode():
    mode = request.form["mode"]

    if mode == "US":
        subprocess.Popen([sys.executable, os.path.join(APP_DIR, "realtime_us.py")])
    else:
        subprocess.Popen([sys.executable, os.path.join(APP_DIR, "realtime_india.py")])

    return "Translator started. Check camera window."

if __name__ == "__main__":
    app.run(debug=True)
