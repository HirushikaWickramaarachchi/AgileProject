# ClubSync – Student Club Management Platform

## Overview
ClubSync is a web application designed to help university students and club administrators manage student clubs in a centralised and efficient way.

Users can sign up, browse and join clubs, view events, and track their attendance history. Administrators have a dedicated panel to manage users, clubs, events, and memberships.

---

## Key Features
- User authentication (signup, login, logout, profile editing)
- Browse and join clubs
- View club details and current members
- View events and mark attendance
- Track personal attendance history
- Admin panel: manage clubs, events, members, and user accounts
- Unified login — admin users are automatically redirected to the admin dashboard from the standard login page
- AJAX-powered event attendee viewer (admin panel)
- CSRF protection on all state-changing forms
- Global dark mode — persistent across all pages with moon/sun toggle; synced between user and admin interfaces

---

## Team Members
| UWA ID | Name | GitHub Username |
|--------|------|----------------|
| 24591632 | Atharva Dalvi | atharvadalvii |
| 24575614 | Farahnaz Abdi | farahnazabdi92 |
| 25063505 | Chaohong Lin | aub11y |
| 24890015 | Hirushika Wickramaarachchi | HirushikaWickramaarachchi |

---

## Project Structure
```
AgileProject/
├── app.py              # Application entry point; creates DB and seeds demo data on first run
├── seeds.py            # Demo data seeder (called automatically by app.py)
├── requirements.txt    # Python dependencies
├── models/             # SQLAlchemy models (User, Club, Event, Membership, Attendance)
├── routes/             # Flask blueprints (auth, clubs, dashboard, admin)
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JavaScript, images
│   ├── css/
│   └── js/
├── components/         # Reusable HTML partials
└── tests/              # Unit tests (pytest) and Selenium browser tests
    ├── conftest.py
    ├── test_auth.py
    ├── test_clubs.py
    ├── test_admin.py
    └── test_selenium.py
```

---

## How to Launch the Application

**Requirements:** Python 3.10 or later, Google Chrome (for Selenium tests)

**1. Clone the repository**
```bash
git clone https://github.com/HirushikaWickramaarachchi/AgileProject.git
cd AgileProject
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
```

**5. Run the application**
```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

On first run, the database is created and populated automatically with demo clubs, events, and users via `seeds.py`. No manual seeding step is needed.

**Demo credentials**

| Role | Email | Password |
|------|-------|----------|
| Regular user | alice.demo@clubsync.local | DemoPass123! |
| Admin | admin@clubsync.edu | admin123 |

> Admin users can log in via either `/login` (redirected automatically to the admin dashboard) or directly via `/admin/login`.

---

## How to Run the Tests

The project includes **96 unit tests** across four files and **10 Selenium browser tests**.

**Unit tests** (no server required)
```bash
pytest tests/test_auth.py tests/test_clubs.py tests/test_admin.py -v
```

**All unit tests at once**
```bash
pytest tests/ --ignore=tests/test_selenium.py -v
```

**Selenium tests** (requires the Flask server to be running and ChromeDriver installed)
```bash
# Terminal 1 — start the server
python app.py

# Terminal 2 — run Selenium tests
pytest tests/test_selenium.py -v
```

> Selenium tests use headless Chrome and connect to `http://127.0.0.1:5000`. Ensure no other process occupies that port.

---

## Technologies Used
- HTML, CSS (custom + Bootstrap 5), JavaScript
- Flask 3 + Jinja2 templates
- SQLite via SQLAlchemy ORM
- Flask-WTF (CSRF protection)
- python-dotenv (environment variable management)
- Flask-Migrate / Alembic (database schema migrations)
- pytest + Selenium WebDriver (testing)
- AJAX via `fetch()` for dynamic data loading (admin event attendees)
