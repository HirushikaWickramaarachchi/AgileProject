from models import db

class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    events = db.relationship("Event", backref="club", cascade="all, delete")
    memberships = db.relationship("Membership", backref="club", cascade="all, delete")