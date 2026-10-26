from flask import Flask, jsonify, request, session, redirect, url_for, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, re
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "portal.db")
app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.secret_key = os.environ.get("PORTAL_SECRET_KEY", "change-this-development-secret")
CORS(app, supports_credentials=True)

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            instructor TEXT NOT NULL,
            duration TEXT NOT NULL,
            level TEXT NOT NULL,
            category TEXT NOT NULL,
            image TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lesson_order INTEGER NOT NULL,
            video_url TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            enrolled_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, course_id)
        );
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
            completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, lesson_id)
        );
        """)
        count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        if count == 0:
            sample_courses = [
                ("Python for Beginners", "Learn Python fundamentals, variables, conditions, loops, and functions through practical examples.", "Mr. Kumar", "4 weeks", "Beginner", "Programming", "python"),
                ("Web Development Basics", "Build your first web pages using semantic HTML, modern CSS, and JavaScript.", "Ms. Ananya", "5 weeks", "Beginner", "Web Development", "web"),
                ("SQL and Databases", "Understand relational databases, SQL queries, joins, and data modelling.", "Dr. Ravi", "3 weeks", "Intermediate", "Database", "sql"),
                ("Introduction to Artificial Intelligence", "Explore AI concepts, machine learning basics, and responsible AI.", "Ms. Priya", "4 weeks", "Beginner", "AI", "ai"),
                ("Git and GitHub Essentials", "Learn version control, branches, commits, and collaborative workflows.", "Mr. Arun", "2 weeks", "Beginner", "Tools", "git"),
                ("Data Structures Fundamentals", "Study arrays, linked lists, stacks, queues, and basic algorithm analysis.", "Dr. Meera", "6 weeks", "Intermediate", "Programming", "data")
            ]
            db.executemany("INSERT INTO courses(title,description,instructor,duration,level,category,image) VALUES(?,?,?,?,?,?,?)", sample_courses)
            lesson_sets = {
                1: [("Introduction to Python","Python is a readable, general-purpose programming language. In this lesson, install Python and run your first print statement."),("Variables and Data Types","Variables store values. Common types include int, float, str, and bool. Use type(value) to inspect a value."),("Conditions and Loops","Use if/elif/else to make decisions. Use for and while loops to repeat tasks."),("Functions","Functions group reusable code. Define one with def and pass values through parameters.")],
                2: [("HTML Page Structure","HTML gives a page its structure. Learn headings, paragraphs, links, images, and semantic elements."),("CSS Styling","CSS controls colours, spacing, typography, borders, and visual appearance."),("Responsive Layouts","Flexbox and Grid help create layouts that adapt to different screen sizes."),("JavaScript Basics","JavaScript adds interaction. Learn variables, events, functions, and DOM updates.")],
                3: [("Database Concepts","A relational database stores related data in tables made of rows and columns."),("SELECT and WHERE","Use SELECT to read data and WHERE to filter rows."),("Joins and Relationships","Joins combine related tables using keys. Primary keys identify rows and foreign keys link tables."),("Safe Data Changes","Use INSERT, UPDATE, and DELETE carefully. Parameterized queries help prevent SQL injection.")],
                4: [("What is AI?","Artificial intelligence describes systems that perform tasks commonly associated with human intelligence."),("Machine Learning Basics","Machine learning models learn patterns from examples and use them to make predictions."),("Data and Evaluation","Training data, test data, and suitable metrics help evaluate model quality."),("Responsible AI","Consider fairness, privacy, transparency, and the limitations of AI systems.")],
                5: [("Why Version Control?","Version control records project changes and helps teams collaborate safely."),("Commits and History","A commit records a snapshot of changes with a message describing the work."),("Branches and Merging","Branches allow work in parallel. Merging combines changes back into a target branch."),("GitHub Collaboration","Repositories host code online. Pull requests let others review proposed changes.")],
                6: [("Arrays and Lists","Arrays and lists store ordered collections of values."),("Linked Lists","Linked lists connect nodes using references, allowing flexible insertion and deletion."),("Stacks and Queues","Stacks follow last-in-first-out; queues follow first-in-first-out."),("Algorithm Complexity","Big O notation describes how time or memory use grows with input size.")]
            }
            for cid, lessons in lesson_sets.items():
                db.executemany("INSERT INTO lessons(course_id,title,content,lesson_order) VALUES(?,?,?,?)",
                               [(cid, title, content, i+1) for i,(title,content) in enumerate(lessons)])

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error":"Please log in to continue."}), 401
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form
    name = str(data.get("name","")).strip()
    email = str(data.get("email","")).strip().lower()
    password = str(data.get("password",""))
    if len(name) < 2:
        return jsonify({"error":"Please enter your name (at least 2 characters)."}), 400
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error":"Please enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error":"Password must contain at least 8 characters."}), 400
    try:
        with get_db() as db:
            cur = db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                             (name,email,generate_password_hash(password)))
            session["user_id"] = cur.lastrowid
            session["user_name"] = name
        return jsonify({"message":"Account created successfully.","user":{"name":name,"email":email}}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error":"An account with this email already exists."}), 409

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    email = str(data.get("email","")).strip().lower()
    password = str(data.get("password",""))
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error":"Invalid email or password."}), 401
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return jsonify({"message":"Logged in successfully.","user":{"name":user["name"],"email":user["email"]}})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message":"Logged out successfully."})

@app.route("/api/auth/me")
def me():
    if not session.get("user_id"):
        return jsonify({"user":None})
    return jsonify({"user":{"name":session.get("user_name")}})

@app.route("/api/courses")
def courses():
    search = request.args.get("search","").strip()
    category = request.args.get("category","").strip()
    level = request.args.get("level","").strip()
    query = "SELECT c.*, COUNT(l.id) AS lesson_count FROM courses c LEFT JOIN lessons l ON l.course_id=c.id WHERE 1=1"
    params=[]
    if search:
        query += " AND (c.title LIKE ? OR c.description LIKE ? OR c.instructor LIKE ?)"
        params += [f"%{search}%"]*3
    if category:
        query += " AND c.category=?"; params.append(category)
    if level:
        query += " AND c.level=?"; params.append(level)
    query += " GROUP BY c.id ORDER BY c.id"
    with get_db() as db:
        rows=db.execute(query,params).fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/api/courses/<int:course_id>")
def course_detail(course_id):
    with get_db() as db:
        course=db.execute("SELECT * FROM courses WHERE id=?",(course_id,)).fetchone()
        if not course: return jsonify({"error":"Course not found."}),404
        lessons=db.execute("SELECT id,title,content,lesson_order FROM lessons WHERE course_id=? ORDER BY lesson_order",(course_id,)).fetchall()
    return jsonify({"course":dict(course),"lessons":[dict(x) for x in lessons]})

@app.route("/api/courses/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll(course_id):
    with get_db() as db:
        if not db.execute("SELECT id FROM courses WHERE id=?",(course_id,)).fetchone():
            return jsonify({"error":"Course not found."}),404
        try:
            db.execute("INSERT INTO enrollments(user_id,course_id) VALUES(?,?)",(session["user_id"],course_id))
        except sqlite3.IntegrityError:
            return jsonify({"message":"You are already enrolled in this course."}),200
    return jsonify({"message":"Enrollment successful."}),201

@app.route("/api/my-courses")
@login_required
def my_courses():
    uid=session["user_id"]
    with get_db() as db:
        rows=db.execute("""
            SELECT c.*, COUNT(DISTINCT l.id) AS lesson_count,
                   COUNT(DISTINCT p.lesson_id) AS completed_count
            FROM enrollments e JOIN courses c ON c.id=e.course_id
            LEFT JOIN lessons l ON l.course_id=c.id
            LEFT JOIN progress p ON p.lesson_id=l.id AND p.user_id=e.user_id
            WHERE e.user_id=? GROUP BY c.id ORDER BY e.enrolled_at DESC
        """,(uid,)).fetchall()
    result=[]
    for row in rows:
        item=dict(row); total=item["lesson_count"]
        item["progress"]=round(item["completed_count"]/total*100) if total else 0
        result.append(item)
    return jsonify(result)

@app.route("/api/lessons/<int:lesson_id>")
@login_required
def lesson_detail(lesson_id):
    with get_db() as db:
        row=db.execute("""SELECT l.*,c.title AS course_title FROM lessons l JOIN courses c ON c.id=l.course_id
                          JOIN enrollments e ON e.course_id=c.id AND e.user_id=?
                          WHERE l.id=?""",(session["user_id"],lesson_id)).fetchone()
        if not row: return jsonify({"error":"Lesson not found or you are not enrolled."}),404
        done=db.execute("SELECT 1 FROM progress WHERE user_id=? AND lesson_id=?",(session["user_id"],lesson_id)).fetchone()
        nav=db.execute("SELECT id,title FROM lessons WHERE course_id=? ORDER BY lesson_order",(row["course_id"],)).fetchall()
    lesson=dict(row); lesson["completed"]=bool(done)
    lesson["lesson_list"]=[dict(x) for x in nav]
    return jsonify(lesson)

@app.route("/api/lessons/<int:lesson_id>/complete", methods=["POST"])
@login_required
def complete_lesson(lesson_id):
    with get_db() as db:
        lesson=db.execute("""SELECT l.id,l.course_id FROM lessons l JOIN enrollments e
                             ON e.course_id=l.course_id AND e.user_id=? WHERE l.id=?""",
                          (session["user_id"],lesson_id)).fetchone()
        if not lesson: return jsonify({"error":"Lesson not found or you are not enrolled."}),404
        db.execute("INSERT OR IGNORE INTO progress(user_id,lesson_id) VALUES(?,?)",(session["user_id"],lesson_id))
        total=db.execute("SELECT COUNT(*) FROM lessons WHERE course_id=?",(lesson["course_id"],)).fetchone()[0]
        completed=db.execute("""SELECT COUNT(*) FROM progress p JOIN lessons l ON l.id=p.lesson_id
                                WHERE p.user_id=? AND l.course_id=?""",(session["user_id"],lesson["course_id"])).fetchone()[0]
    return jsonify({"message":"Lesson marked as complete.","completed":completed,"total":total,
                    "progress":round(completed/total*100) if total else 0})

@app.route("/api/categories")
def categories():
    with get_db() as db:
        rows=db.execute("SELECT DISTINCT category FROM courses ORDER BY category").fetchall()
    return jsonify([r["category"] for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
