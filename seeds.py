from werkzeug.security import generate_password_hash

from models import Attendance, Club, Event, Membership, User, db


DEMO_USERS = [
    {"name": "Alice Nguyen", "email": "alice.demo@clubsync.local", "password": "DemoPass123!"},
    {"name": "Liam Chen", "email": "liam.demo@clubsync.local", "password": "DemoPass123!"},
    {"name": "Priya Kumar", "email": "priya.demo@clubsync.local", "password": "DemoPass123!"},
    {"name": "Samuel Ng", "email": "samuel.demo@clubsync.local", "password": "DemoPass123!"},
    {"name": "Hana Lee", "email": "hana.demo@clubsync.local", "password": "DemoPass123!"},
    {"name": "Nina Shah", "email": "nina.demo@clubsync.local", "password": "DemoPass123!"},
    {"name": "Tariq Rahman", "email": "tariq.demo@clubsync.local", "password": "DemoPass123!"},
    {"name": "Amara Lim", "email": "amara.demo@clubsync.local", "password": "DemoPass123!"},
]

DEMO_CLUBS = [
    {
        "name": "AI Society",
        "description": "A student community exploring practical AI projects, ethics, and industry applications.",
        "category": "Tech",
        "image_path": "images/clubs/ai-society.png",
    },
    {
        "name": "Coding Club",
        "description": "Weekly coding sessions, project collaboration, and interview preparation for all levels.",
        "category": "Tech",
        "image_path": "images/clubs/coding-club.png",
    },
    {
        "name": "Robotics Club",
        "description": "Design, build, and test robotics systems for competitions and campus showcases.",
        "category": "Tech",
        "image_path": "images/clubs/robotics-club.png",
    },
    {
        "name": "Photography Club",
        "description": "Photo walks, editing workshops, and portfolio feedback for student photographers.",
        "category": "Arts",
        "image_path": "images/clubs/photography-club.png",
    },
    {
        "name": "Debate Society",
        "description": "Practice argumentation, public speaking, and structured debate formats.",
        "category": "Academic",
        "image_path": "images/clubs/debate-society.png",
    },
    {
        "name": "Cultural Exchange Club",
        "description": "Celebrate global cultures through language exchange, food events, and social activities.",
        "category": "Culture",
        "image_path": "images/clubs/cultural-exchange-club.png",
    },
    {
        "name": "Entrepreneurship Club",
        "description": "Pitch practice, startup workshops, and leadership development for student founders.",
        "category": "Leadership",
        "image_path": "images/clubs/entrepreneurship-club.png",
    },
]

DEMO_EVENTS = [
    {
        "club_name": "AI Society",
        "title": "AI Mini Hackathon",
        "date": "Saturday, May 10, 2026 | 9:00 AM - 4:00 PM",
        "description": "Build practical AI prototypes in cross-discipline teams with mentor checkpoints.",
    },
    {
        "club_name": "AI Society",
        "title": "Intro to Machine Learning Workshop",
        "date": "Wednesday, May 15, 2026 | 4:00 PM - 6:00 PM",
        "description": "Hands-on beginner workshop covering model basics and notebook-driven practice.",
    },
    {
        "club_name": "AI Society",
        "title": "AI Ethics Roundtable",
        "date": "Tuesday, May 21, 2026 | 6:00 PM - 7:30 PM",
        "description": "Student-led discussion on fairness, bias, and responsible AI deployment.",
    },
    {
        "club_name": "Coding Club",
        "title": "Python Pair Programming Night",
        "date": "Thursday, May 16, 2026 | 5:30 PM - 7:30 PM",
        "description": "Solve coding challenges in rotating pairs and review clean coding patterns.",
    },
    {
        "club_name": "Coding Club",
        "title": "Full-Stack Project Sprint",
        "date": "Saturday, May 24, 2026 | 10:00 AM - 2:00 PM",
        "description": "Build and demo small web apps with frontend and backend collaboration.",
    },
    {
        "club_name": "Robotics Club",
        "title": "Line Follower Build Lab",
        "date": "Monday, May 12, 2026 | 4:30 PM - 6:30 PM",
        "description": "Assemble and tune sensor-based line follower robots in guided teams.",
    },
    {
        "club_name": "Robotics Club",
        "title": "Robotics Showcase Prep",
        "date": "Friday, May 23, 2026 | 5:00 PM - 7:00 PM",
        "description": "Finalize demos and practice presentations for the inter-club showcase.",
    },
    {
        "club_name": "Photography Club",
        "title": "Golden Hour Campus Photo Walk",
        "date": "Sunday, May 18, 2026 | 5:00 PM - 6:30 PM",
        "description": "Capture portraits and landscapes around campus with peer feedback.",
    },
    {
        "club_name": "Photography Club",
        "title": "Lightroom Editing Clinic",
        "date": "Wednesday, May 28, 2026 | 4:00 PM - 6:00 PM",
        "description": "Improve color grading and workflow techniques with guided editing exercises.",
    },
    {
        "club_name": "Debate Society",
        "title": "Parliamentary Debate Bootcamp",
        "date": "Tuesday, May 20, 2026 | 5:30 PM - 7:30 PM",
        "description": "Practice parliamentary formats with adjudicator feedback and timed rounds.",
    },
    {
        "club_name": "Debate Society",
        "title": "Public Speaking Drill Session",
        "date": "Monday, May 27, 2026 | 4:00 PM - 5:30 PM",
        "description": "Build confidence with impromptu speeches and structured delivery drills.",
    },
    {
        "club_name": "Cultural Exchange Club",
        "title": "International Food Festival Planning",
        "date": "Thursday, May 22, 2026 | 3:30 PM - 5:00 PM",
        "description": "Coordinate food stalls, volunteer roles, and logistics for a campus showcase.",
    },
    {
        "club_name": "Cultural Exchange Club",
        "title": "Language Exchange Mixer",
        "date": "Friday, May 30, 2026 | 5:00 PM - 7:00 PM",
        "description": "Meet students from different backgrounds for guided language conversation circles.",
    },
    {
        "club_name": "Entrepreneurship Club",
        "title": "Startup Pitch Night",
        "date": "Wednesday, June 4, 2026 | 5:00 PM - 7:00 PM",
        "description": "Present startup ideas and receive feedback from student founders and mentors.",
    },
    {
        "club_name": "Entrepreneurship Club",
        "title": "Leadership in Product Teams",
        "date": "Monday, June 9, 2026 | 4:00 PM - 5:30 PM",
        "description": "Workshop on communication, prioritisation, and execution in student product teams.",
    },
]

DEMO_MEMBERSHIPS = {
    "alice.demo@clubsync.local": ["AI Society", "Coding Club"],
    "liam.demo@clubsync.local": ["AI Society", "Robotics Club"],
    "priya.demo@clubsync.local": ["Coding Club", "Debate Society"],
    "samuel.demo@clubsync.local": ["Robotics Club"],
    "hana.demo@clubsync.local": ["AI Society", "Photography Club"],
    "nina.demo@clubsync.local": ["Debate Society", "Cultural Exchange Club"],
    "tariq.demo@clubsync.local": ["Cultural Exchange Club", "Entrepreneurship Club"],
    "amara.demo@clubsync.local": ["Photography Club", "AI Society", "Entrepreneurship Club"],
}

DEMO_ATTENDANCE = {
    "alice.demo@clubsync.local": ["AI Mini Hackathon", "Full-Stack Project Sprint"],
    "liam.demo@clubsync.local": ["AI Mini Hackathon", "Robotics Showcase Prep"],
    "priya.demo@clubsync.local": ["Parliamentary Debate Bootcamp"],
    "samuel.demo@clubsync.local": ["Line Follower Build Lab"],
    "hana.demo@clubsync.local": ["Golden Hour Campus Photo Walk", "Intro to Machine Learning Workshop"],
    "nina.demo@clubsync.local": ["Language Exchange Mixer"],
    "amara.demo@clubsync.local": ["AI Ethics Roundtable", "Startup Pitch Night"],
}


def seed_demo_data():
    _seed_admin()
    users_by_email = _seed_users()
    clubs_by_name = _seed_clubs()
    events_by_title = _seed_events(clubs_by_name)
    _seed_memberships(users_by_email, clubs_by_name)
    _seed_attendance(users_by_email, events_by_title)
    db.session.commit()


def _seed_admin():
    admin_email = "admin@clubsync.edu"
    existing = User.query.filter_by(email=admin_email).first()
    if not existing:
        admin = User(
            name="Admin",
            email=admin_email,
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()


def _seed_users():
    users_by_email = {}

    for user_data in DEMO_USERS:
        user = User.query.filter_by(email=user_data["email"]).first()

        if not user:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
            )
            db.session.add(user)

        users_by_email[user_data["email"]] = user

    db.session.commit()

    for email in users_by_email:
        users_by_email[email] = User.query.filter_by(email=email).first()

    return users_by_email


def _seed_clubs():
    clubs_by_name = {}

    for club_data in DEMO_CLUBS:
        club = Club.query.filter_by(name=club_data["name"]).first()

        if not club:
            club = Club(
                name=club_data["name"],
                description=club_data["description"],
                category=club_data["category"],
                image_path=club_data["image_path"],
            )
            db.session.add(club)
        else:
            needs_update = False

            if club.description != club_data["description"]:
                club.description = club_data["description"]
                needs_update = True

            if club.category != club_data["category"]:
                club.category = club_data["category"]
                needs_update = True

            if club.image_path != club_data["image_path"]:
                club.image_path = club_data["image_path"]
                needs_update = True

            if needs_update:
                db.session.add(club)

        clubs_by_name[club_data["name"]] = club

    db.session.commit()

    for name in clubs_by_name:
        clubs_by_name[name] = Club.query.filter_by(name=name).first()

    return clubs_by_name


def _seed_events(clubs_by_name):
    events_by_title = {}

    for event_data in DEMO_EVENTS:
        club = clubs_by_name[event_data["club_name"]]
        event = Event.query.filter_by(club_id=club.id, title=event_data["title"]).first()

        if not event:
            event = Event(
                club_id=club.id,
                title=event_data["title"],
                date=event_data["date"],
                description=event_data["description"],
            )
            db.session.add(event)
        else:
            event.date = event_data["date"]
            event.description = event_data["description"]

        existing_with_title = events_by_title.get(event_data["title"])
        if existing_with_title and existing_with_title.club_id != club.id:
            raise ValueError(
                f"Duplicate demo event title detected across clubs: {event_data['title']}"
            )

        events_by_title[event_data["title"]] = event

    db.session.commit()

    return events_by_title


def _seed_memberships(users_by_email, clubs_by_name):
    for email, club_names in DEMO_MEMBERSHIPS.items():
        user = users_by_email[email]

        for club_name in club_names:
            club = clubs_by_name[club_name]
            existing_membership = Membership.query.filter_by(
                user_id=user.id,
                club_id=club.id,
            ).first()

            if not existing_membership:
                db.session.add(Membership(user_id=user.id, club_id=club.id))


def _seed_attendance(users_by_email, events_by_title):
    for email, event_titles in DEMO_ATTENDANCE.items():
        user = users_by_email[email]

        for title in event_titles:
            event = events_by_title.get(title)

            if not event:
                raise ValueError(
                    f"Attendance seed references unknown event title: {title}"
                )

            existing_attendance = Attendance.query.filter_by(
                user_id=user.id,
                event_id=event.id,
            ).first()

            if not existing_attendance:
                db.session.add(Attendance(user_id=user.id, event_id=event.id))
