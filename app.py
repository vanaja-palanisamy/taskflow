import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import sqlite3
from flask_dance.contrib.google import make_google_blueprint, google

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB = "tasks.db"


# ---------------- GOOGLE LOGIN ----------------

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="google_login"
)

app.register_blueprint(google_bp, url_prefix="/login")


# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            start_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            category TEXT,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- GOOGLE LOGIN SUCCESS ----------------
@app.route("/google_login")
def google_login():

    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")

    if not resp.ok:
        return "Google login failed"

    info = resp.json()
    email = info["email"]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username=?", (email,))
    user = cursor.fetchone()

    if not user:
        hashed_password = generate_password_hash(email)

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (email, hashed_password))

        conn.commit()
    
        cursor.execute("SELECT id FROM users WHERE username=?", (email,))
        user = cursor.fetchone()

    conn.close()

    session["user_id"] = user[0]

    return redirect(url_for("all_tasks"))


# ---------------- HOME ----------------
@app.route("/")
def home():
    if not google.authorized:
        return redirect("/login/google")
    return redirect(url_for("google_login"))


# ---------------- CREATE TASK ----------------
@app.route("/create")
def create_task():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    return render_template("create_task.html")


# ---------------- ADD TASK ----------------
@app.route("/add", methods=["POST"])
def add_task():

    if "user_id" not in session:
        return {"success": False}

    user_id = session["user_id"]

    name = request.form["name"]
    description = request.form.get("description", "")
    start_date = request.form["start_date"]
    due_date = request.form["due_date"]
    category = request.form.get("category", "")
    status = request.form["status"]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks 
        (user_id,name,description,start_date,due_date,category,status)
        VALUES (?,?,?,?,?,?,?)
    """, (user_id, name, description, start_date, due_date, category, status))

    conn.commit()
    conn.close()

    return {"success": True}


# ---------------- VIEW TASKS ----------------
@app.route("/tasks")
def all_tasks():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    user_id = session["user_id"]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id=?",
        (user_id,)
    )

    tasks_data = cursor.fetchall()
    conn.close()

    tasks = []

    for t in tasks_data:
        tasks.append({
            "id": t[0],
            "name": t[2],
            "description": t[3],
            "start_date": t[4],
            "due_date": t[5],
            "category": t[6],
            "status": t[7]
        })

    return render_template("all_tasks.html", tasks=tasks)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)