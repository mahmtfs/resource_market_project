from market import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    balance = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.Text, nullable=False, default="Bio")
    items = db.relationship('Item', backref='seller', lazy=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    volume = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

