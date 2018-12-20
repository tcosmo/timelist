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

    def can_read(self, list_ ):
        print( self.readable_lists )
        return list_ in [ a.list_ for a in self.readable_lists ]

    def can_write(self, list_ ):
        return list_ in [ a.list_ for a in self.writable_lists ]

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

    all_read      = db.Column(db.Boolean, index=True, default=False)
    all_write     = db.Column(db.Boolean, index=True, default=False)

    def __repr__(self):
        return '<List {}>'.format( self.name )

class ReadUserList(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), primary_key=True)

    user = db.relationship("User", backref='readable_lists')
    list_ = db.relationship("List", backref='read_by_users')

class WriteUserList(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), primary_key=True)

    user = db.relationship("User", backref='writable_lists')
    list_ = db.relationship("List", backref='wrote_by_users')

class ListType(db.Model):
    id            = db.Column(db.Integer, index=True, primary_key=True)
    name          = db.Column(db.String, index=True, unique=True)
    template      = db.Column(db.String, index=True)

    instances     = db.relationship('List', backref='list_type', lazy='dynamic')

    def __repr__(self):
        return '<ListType {}>'.format( self.name )