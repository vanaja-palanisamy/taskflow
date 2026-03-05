from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB = 'tasks.db'


# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
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
    ''')

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('all_tasks'))
    return redirect(url_for('login_page'))


# ---------------- REGISTER ----------------
@app.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect(url_for('all_tasks'))
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
    except:
        conn.close()
        return "Username already exists"

    conn.close()
    return redirect(url_for('login_page'))


# ---------------- LOGIN ----------------
@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('all_tasks'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        return redirect(url_for('all_tasks'))
    else:
        return "Invalid credentials"


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# ---------------- CREATE TASK PAGE ----------------
@app.route('/create')
def create_task():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('create_task.html')


# ---------------- ADD TASK ----------------
@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return {"success": False}, 403

    user_id = session['user_id']

    name = request.form['name']
    description = request.form.get('description', '')
    start_date = request.form['start_date']
    due_date = request.form['due_date']
    category = request.form.get('category', '')
    status = request.form['status']

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO tasks 
        (user_id, name, description, start_date, due_date, category, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (user_id, name, description, start_date, due_date, category, status)
    )

    conn.commit()
    conn.close()

    return {"success": True}


# ---------------- VIEW TASKS ----------------
@app.route('/tasks')
def all_tasks():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

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
            'id': t[0],
            'name': t[2],
            'description': t[3],
            'start_date': t[4],
            'due_date': t[5],
            'category': t[6],
            'status': t[7]
        })

    return render_template('all_tasks.html', tasks=tasks)


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)