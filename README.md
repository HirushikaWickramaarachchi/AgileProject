# ClubSync – Student Club Management Platform

## Overview
ClubSync is a web application designed to help university students and club administrators manage student clubs in a centralised and efficient way.

Users can join clubs, view events, and track their participation, while administrators can manage members and organise events.

---

## Key Features
- User authentication (signup, login, logout)
- Browse and join clubs
- View club details and members
- View and attend events
- Track attendance history
- Edit user profile
- Admin controls for managing members, clubs, and events

---

## Team Members
| Name | UWA ID | GitHub Username |
|------|--------|----------------|
| Atharva Dalvi | 24591632 | atharvadalvii |
| Farahnaz Abdi | 24575614 | farahnazabdi92 |
| Chaohong Lin | 25063505 | aub11y |
| Hirushika Wickramaarachchi | 24890015 | HirushikaWickramaarachchi |

---

## Project Structure
```
project-root/
├── templates/        # HTML pages (Jinja2 templates)
├── static/           # CSS, JavaScript, images
├── models/           # SQLAlchemy database models
├── routes/           # Flask route blueprints
├── tests/            # Unit and Selenium tests
├── app.py            # Application entry point
├── seeds.py          # Demo data seeder
└── requirements.txt  # Python dependencies
```

---

## How to Launch the Application

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

Demo data (clubs, events, users) is seeded automatically on first run.

---

## How to Run the Tests

**Unit tests**
```bash
pytest tests/test_auth.py tests/test_clubs.py tests/test_admin.py
```

**Selenium tests** (requires the Flask server to be running)
```bash
# Terminal 1 — start the server
python app.py

# Terminal 2 — run Selenium tests
pytest tests/test_selenium.py
```

Selenium tests require Google Chrome and ChromeDriver installed.

---

## Technologies Used
- HTML, CSS (custom + Bootstrap 5)
- JavaScript (DOM manipulation, AJAX)
- Flask + Jinja2 templates
- SQLite via SQLAlchemy
- Flask-WTF (CSRF protection)
- pytest + Selenium (testing)
