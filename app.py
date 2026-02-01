from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("users.db")

# CREATE TABLE (ONE TIME)
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    points INTEGER DEFAULT 0
)
""")
conn.close()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect('/login')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except:
            pass
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid Login")

    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    return render_template('dashboard.html', user=session['user'])

# ---------------- QUIZ ----------------
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user' not in session:
        return redirect('/login')

    questions = [
        {
            "question": "What does HTML stand for?",
            "options": [
                "Hyper Text Markup Language",
                "High Text Machine Language",
                "Hyperlinks Text Markup",
                "None"
            ],
            "answer": "Hyper Text Markup Language"
        },
        {
            "question": "Which language is used for backend?",
            "options": ["HTML", "CSS", "Python", "Photoshop"],
            "answer": "Python"
        },
        {
            "question": "Flask is a ____ framework?",
            "options": ["Frontend", "Backend", "Database", "Design"],
            "answer": "Backend"
        }
    ]

    if request.method == 'POST':
        score = 0

        for i, q in enumerate(questions):
            user_ans = request.form.get(f"q{i}")
            if user_ans == q['answer']:
                score += 1

        # UPDATE POINTS
        conn = get_db()
        conn.execute(
            "UPDATE users SET points = points + ? WHERE username = ?",
            (score, session['user'])
        )
        conn.commit()
        conn.close()

        return redirect('/leaderboard')

    return render_template('quiz.html', questions=questions)

# ---------------- LEADERBOARD ----------------
@app.route('/leaderboard')
def leaderboard():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    users = conn.execute(
        "SELECT username, points FROM users ORDER BY points DESC"
    ).fetchall()
    conn.close()

    return render_template('leaderboard.html', users=users)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
