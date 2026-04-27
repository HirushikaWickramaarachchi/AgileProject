from models import db

class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

    events = db.relationship("Event", backref="club", cascade="all, delete")
    memberships = db.relationship("Membership", backref="club", cascade="all, delete")
