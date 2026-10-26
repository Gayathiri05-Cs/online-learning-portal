# LearnSpace — Online Learning Portal

A responsive full-stack online learning portal built with **Python Flask**, **SQLite**, HTML, CSS, and JavaScript.

## Features

- Student registration and login with hashed passwords
- Course catalog with search, category, and level filters
- Course details and lesson previews
- Student enrollment in courses
- Protected lesson pages with previous/next navigation
- Mark lessons complete and calculate course progress
- My Learning dashboard with progress bars
- Responsive layout for desktop, tablet, and mobile
- SQLite database initialized automatically with six sample courses and 24 lessons
- REST-style JSON API and manual test checklist

## Requirements

- Python 3.10 or later
- pip

## Run locally (Windows PowerShell)

```powershell
# 1. Open this project folder in VS Code, then open Terminal > New Terminal
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. The database and sample course content are created automatically on first run.

If PowerShell blocks environment activation, run this command in the current terminal and retry activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

To stop the server, press `Ctrl+C` in the terminal.

## Project structure

```text
OnlineLearningPortal/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── frontend/
│   ├── templates/index.html
│   └── static/
│       ├── style.css
│       └── app.js
├── database/          # SQLite database is generated at runtime
├── data/              # Reserved for optional data files
├── tests/              # Test location
├── screenshots/        # Add screenshots before submission
└── test_cases.md
```

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Log in |
| POST | `/api/auth/logout` | Log out |
| GET | `/api/auth/me` | Current session |
| GET | `/api/courses` | List/search/filter courses |
| GET | `/api/courses/<id>` | Course and lessons |
| POST | `/api/courses/<id>/enroll` | Enroll current student |
| GET | `/api/my-courses` | Enrolled courses and progress |
| GET | `/api/lessons/<id>` | Get an enrolled lesson |
| POST | `/api/lessons/<id>/complete` | Mark lesson complete |
| GET | `/api/categories` | List course categories |

## Security notes

- Passwords are hashed with Werkzeug; plain-text passwords are never stored.
- SQL queries use parameters.
- Lesson access and enrollment/progress operations require a logged-in session.
- The default Flask secret key is for local development only. Set `PORTAL_SECRET_KEY` to a long random secret before deployment.
- For production deployment, disable debug mode, use HTTPS, configure secure cookies, and add CSRF protection/rate limiting.

## Testing

Follow `test_cases.md` to check registration, login, duplicate emails, course filtering, enrollment, lesson completion, and progress tracking.

## Notes

This is an educational project with sample lesson text, not a commercial learning management system. Optional features such as admin management, certificates, reviews, and video embedding can be added later.
