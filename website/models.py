from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    ratings = db.relationship("Rating", backref='user', lazy=True)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    movie = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
