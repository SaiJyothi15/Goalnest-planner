from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import os, json, datetime, random

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

USERS_FILE = 'users.json'
DATA_FILE = 'tasks.json'
STREAK_FILE = 'streak.json'
FEEDBACK_FILE = 'feedback.json'

# Ensure data files exist
for file, default in [
    (USERS_FILE, {}),
    (DATA_FILE, []),
    (STREAK_FILE, {"date": "", "streak": 0, "longest": 0}),
    (FEEDBACK_FILE, [])
]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump(default, f)

# Helper functions
def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_tasks():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f)

def load_streak():
    with open(STREAK_FILE) as f:
        return json.load(f)

def save_streak(data):
    with open(STREAK_FILE, 'w') as f:
        json.dump(data, f)

def save_feedback(entry):
    with open(FEEDBACK_FILE) as f:
        data = json.load(f)
    data.append(entry)
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f)

# Routes

@app.route('/')
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        identifier = request.form.get("Email")
        password = request.form.get("password")

        user = users.get(identifier)

        if not user:
            for u in users.values():
                if isinstance(u, dict) and u.get("email") == identifier:
                    user = u
                    break

        if user and user.get("password") == password:
            session['Name'] = user.get('name')
            session['email'] = user.get('email')
            return redirect(url_for("index"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if email in users:
            return 'Email already registered!', 400
        
        # Save new user
        users[email] = {
            'name': name,
            'email': email,
            'password': password,
            'current_streak': 0,
            'longest_streak': 0
        }
        save_users(users)

        return redirect(url_for('login'))  # redirect to login page after successful registration
    
    # For GET request, render the registration form
    return render_template('register.html')
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/tasks', methods=['GET', 'POST', 'DELETE'])
def tasks():
    tasks = load_tasks()
    if request.method == 'GET':
        return jsonify(tasks)
    elif request.method == 'POST':
        t = request.json.get('task')
        cat = request.json.get('category', 'General')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tasks.append({"task": t, "category": cat, "created_at": timestamp, "completed": False})
        save_tasks(tasks)
        return jsonify(tasks)
    else:
        t = request.json.get('task')
        tasks = [x for x in tasks if x['task'] != t]
        save_tasks(tasks)
        return jsonify(tasks)

@app.route('/complete', methods=['POST'])
def complete():
    tasks = load_tasks()
    t = request.json.get('task')

    for obj in tasks:
        if obj['task'] == t:
            obj['completed'] = True
    save_tasks(tasks)

    streak = load_streak()
    today = datetime.date.today()
    last_date_str = streak.get("date", "")
    last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date() if last_date_str else None

    if not last_date or (today - last_date).days > 1:
        streak["streak"] = 1
    elif (today - last_date).days == 1:
        streak["streak"] += 1

    if streak["streak"] > streak.get("longest", 0):
        streak["longest"] = streak["streak"]

    streak["date"] = today.isoformat()
    save_streak(streak)

    return jsonify(streak)

@app.route('/streak')
def get_streak():
    streak = load_streak()
    today = datetime.date.today().isoformat()
    if streak.get("date") != today:
        tasks = load_tasks()
        if not any(t["completed"] for t in tasks if t.get("created_at", "").startswith(today)):
            streak["streak"] = 0
    return jsonify({"streak": streak.get("streak", 0), "longest": streak.get("longest", 0)})

@app.route('/recommendation')
def rec():
    tip_list = [
        "Break big tasks into smaller chunks.",
        "Use the Pomodoro technique.",
        "Remove distractions before you start.",
        "Start with the easiest task first.",
        "Review your goals every morning.",
        "Reward yourself after tasks."
    ]
    return jsonify({"tip": random.choice(tip_list)})

@app.route('/encourage')
def encourage():
    pool = {
        "Study": [f"Great job studying! #{i}" for i in range(1, 26)],
        "Work": [f"Excellent work! Keep it up #{i}" for i in range(1, 26)],
        "Fitness": [f"You're crushing your fitness goals! #{i}" for i in range(1, 26)],
        "General": [f"Awesome progress today! #{i}" for i in range(1, 26)]
    }
    cat = request.args.get('category', 'General')
    return jsonify({"encourage": random.choice(pool.get(cat, pool["General"]))})
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        entry = request.form.get('feedback')
        save_feedback({"feedback": entry, "time": datetime.datetime.now().isoformat()})
        return "Thank you for your feedback!"
    return render_template('feedback.html')
import json
import os

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


if __name__ == '__main__':
    app.run(debug=True)

