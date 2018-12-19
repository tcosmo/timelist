from datetime import datetime
from app import db, login

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import ARRAY

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), index=True, unique=True)
    email         = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)    

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class List(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    created       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name          = db.Column(db.String(64), index=True)
    list_type_id  = db.Column(db.Integer, db.ForeignKey('list_type.id'), index=True)

    can_read      = db.relationship('ReadUserList', uselist=True, backref='can_read', lazy='dynamic')
    can_write     = db.relationship('WriteUserList', uselist=True, backref='can_write', lazy='dynamic')

class ReadUserList(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), primary_key=True)

class WriteUserList(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), primary_key=True)

class ListType(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String, unique=True)
    template      = db.Column(db.String)