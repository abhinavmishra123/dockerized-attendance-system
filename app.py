import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, make_response

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages'
DB_PATH = 'attendance.db'

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP,
            is_active BOOLEAN
        )
    ''')
    # Create attendance table with UNIQUE(session_id, roll_no)
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            timestamp TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            UNIQUE(session_id, roll_no)
        )
    ''')
    
    # Ensure there is at least one active session on startup
    active_session = c.execute('SELECT * FROM sessions WHERE is_active = 1').fetchone()
    if not active_session:
        new_token = str(uuid.uuid4())
        c.execute('INSERT INTO sessions (token, created_at, is_active) VALUES (?, ?, 1)', 
                  (new_token, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

init_db()

# --- HTML Templates (Embedded for simplicity) ---

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0ea5e9;
            --success: #10b981;
            --error: #ef4444;
            --warning: #f59e0b;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-image: radial-gradient(circle at top right, #1e293b, transparent 50%),
                              radial-gradient(circle at bottom left, #0f172a, transparent 50%);
        }
        .container {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 40px;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        h1 {
            margin-top: 0;
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }
        .btn {
            display: inline-block;
            background: var(--accent);
            color: #0f172a;
            font-weight: 600;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
            font-size: 1rem;
            margin-top: 20px;
        }
        .btn:hover {
            background: var(--accent-hover);
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.4);
        }
        .btn-warning {
            background: var(--warning);
        }
        .btn-warning:hover {
            background: #d97706;
            box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.4);
        }
        input[type="text"] {
            width: 100%;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(15, 23, 42, 0.5);
            color: white;
            font-size: 1rem;
            box-sizing: border-box;
            margin-bottom: 20px;
            font-family: 'Inter', sans-serif;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
        }
        .list-group {
            list-style: none;
            padding: 0;
            margin: 0;
            max-height: 400px;
            overflow-y: auto;
        }
        .list-item {
            background: rgba(255,255,255,0.05);
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .list-item .details {
            display: flex;
            flex-direction: column;
        }
        .list-item .roll {
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: 600;
        }
        .list-item .time {
            font-size: 0.85rem;
            color: var(--text-muted);
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }
        .message.success { background: rgba(16, 185, 129, 0.2); color: var(--success); border: 1px solid var(--success); }
        .message.error { background: rgba(239, 68, 68, 0.2); color: var(--error); border: 1px solid var(--error); }
        .link-box {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            word-break: break-all;
            color: var(--accent);
            font-family: monospace;
            margin: 20px 0;
            text-align: center;
            border: 1px dashed rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="message {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

ADMIN_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
<h1>Dashboard (Today)</h1>
<p style="text-align: center;">Share this link with students for today's attendance:</p>
<div class="link-box">
    {{ link }}
</div>

<h2>Attendees Today ({{ attendees|length }})</h2>
{% if attendees %}
    <ul class="list-group">
    {% for person in attendees %}
        <li class="list-item">
            <div class="details">
                <span><strong>{{ person.name }}</strong></span>
                <span class="roll">Roll No: {{ person.roll_no }}</span>
            </div>
            <span class="time">{{ person.timestamp }}</span>
        </li>
    {% endfor %}
    </ul>
{% else %}
    <p style="text-align: center; color: var(--text-muted);">No one has attended yet today.</p>
{% endif %}

<form action="{{ url_for('new_session') }}" method="post" style="margin-top: 30px;">
    <button type="submit" class="btn btn-warning" onclick="return confirm('Are you sure you want to start a new day? This will generate a new link and reset tracking for students.');">Start New Day (Reset Link)</button>
</form>
""")

ATTEND_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
<h1>Mark Attendance</h1>
<p style="text-align: center; margin-bottom: 30px;">Please enter your details to mark your attendance for today.</p>
<form action="{{ url_for('submit_attendance') }}" method="post">
    <input type="hidden" name="session_token" value="{{ session_token }}">
    <input type="text" name="name" placeholder="Enter your full name" required autocomplete="off">
    <input type="text" name="roll_no" placeholder="Enter your Roll Number" required autocomplete="off">
    <button type="submit" class="btn">Submit Attendance</button>
</form>
""")

SUCCESS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
<div style="text-align: center;">
    <h1 style="font-size: 5rem; margin-bottom: 0;">🎉</h1>
    <h1>Attendance Marked!</h1>
    <p>Thank you, <strong>{{ name }}</strong>.</p>
    <p style="color: var(--accent); font-weight: 600;">Roll No: {{ roll_no }}</p>
    <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 20px;">You can now close this window.</p>
</div>
""")

ERROR_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
<div style="text-align: center;">
    <h1 style="font-size: 5rem; margin-bottom: 0;">❌</h1>
    <h1>Access Denied</h1>
    <p>{{ reason }}</p>
</div>
""")

# --- Routes ---

@app.route('/')
def index():
    conn = get_db_connection()
    # Get active session
    active_session = conn.execute('SELECT * FROM sessions WHERE is_active = 1').fetchone()
    
    attendees = []
    link = "No active session."
    
    if active_session:
        # Get attendees ONLY for the active session
        attendees = conn.execute('''
            SELECT name, roll_no, timestamp 
            FROM attendance 
            WHERE session_id = ? 
            ORDER BY id DESC
        ''', (active_session['id'],)).fetchall()
        
        link = request.host_url.rstrip('/') + url_for('attendance', session_token=active_session['token'])

    conn.close()
    return render_template_string(ADMIN_TEMPLATE, attendees=attendees, link=link)

@app.route('/new_session', methods=['POST'])
def new_session():
    conn = get_db_connection()
    # Deactivate all sessions
    conn.execute('UPDATE sessions SET is_active = 0')
    # Create new session
    new_token = str(uuid.uuid4())
    conn.execute('INSERT INTO sessions (token, created_at, is_active) VALUES (?, ?, 1)', 
                 (new_token, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    flash('New Day started successfully! A new link has been generated.', 'success')
    return redirect(url_for('index'))

@app.route('/attendance/<session_token>')
def attendance(session_token):
    conn = get_db_connection()
    session = conn.execute('SELECT * FROM sessions WHERE token = ?', (session_token,)).fetchone()
    conn.close()

    if not session:
        return render_template_string(ERROR_TEMPLATE, reason="Invalid attendance link.")
    if session['is_active'] == 0:
        return render_template_string(ERROR_TEMPLATE, reason="This link has expired. The session is closed.")

    # Check if the device has already marked attendance for THIS session
    cookie_name = f'attendance_marked_{session_token}'
    if request.cookies.get(cookie_name):
        return render_template_string(ERROR_TEMPLATE, reason="You have already marked your attendance from this device for today.")

    return render_template_string(ATTEND_TEMPLATE, session_token=session_token)

@app.route('/submit', methods=['POST'])
def submit_attendance():
    session_token = request.form.get('session_token')
    name = request.form.get('name')
    roll_no = request.form.get('roll_no')

    # Double check cookie just in case
    cookie_name = f'attendance_marked_{session_token}'
    if request.cookies.get(cookie_name):
        return render_template_string(ERROR_TEMPLATE, reason="You have already marked your attendance from this device for today.")

    conn = get_db_connection()
    session = conn.execute('SELECT * FROM sessions WHERE token = ?', (session_token,)).fetchone()
    
    if not session or session['is_active'] == 0:
        conn.close()
        return render_template_string(ERROR_TEMPLATE, reason="Invalid or expired session.")
    
    try:
        conn.execute('INSERT INTO attendance (session_id, name, roll_no, timestamp) VALUES (?, ?, ?, ?)', 
                     (session['id'], name, roll_no, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except sqlite3.IntegrityError:
        # This catches the UNIQUE(session_id, roll_no) constraint violation
        conn.close()
        flash('This Roll Number has already been recorded for today.', 'error')
        return redirect(url_for('attendance', session_token=session_token))
    
    conn.close()

    # Create the success response and SET THE COOKIE specifically for this session
    response = make_response(render_template_string(SUCCESS_TEMPLATE, name=name, roll_no=roll_no))
    # Cookie lasts for a long time, but it's bound to the session_token name
    response.set_cookie(cookie_name, 'true', max_age=31536000) 
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
