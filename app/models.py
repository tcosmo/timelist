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
        return list_.all_read or list_ in self.readable_lists

    def can_write(self, list_ ):
        return list_.all_write or list_ in self.writable_lists

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

ReaduUserList = db.Table('read_user_list',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('list_id', db.Integer, db.ForeignKey('list.id'), primary_key=True)
)

WriteUserList = db.Table('write_user_list',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('list_id', db.Integer, db.ForeignKey('list.id'), primary_key=True)
)

class List(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    created       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name          = db.Column(db.String(64), index=True)
    list_type_id  = db.Column(db.Integer, db.ForeignKey('list_type.id'), index=True)

    all_read      = db.Column(db.Boolean, index=True, default=False)
    all_write     = db.Column(db.Boolean, index=True, default=False)

    read_by_users = db.relationship('User', secondary=ReaduUserList, backref='readable_lists')
    written_by_users = db.relationship('User', secondary=WriteUserList, backref='writable_lists')

    def __repr__(self):
        return '<List {}>'.format( self.name )

class ListType(db.Model):
    id            = db.Column(db.Integer, index=True, primary_key=True)
    name          = db.Column(db.String, index=True, unique=True)
    template      = db.Column(db.String, index=True)

    description = db.Column(db.String, index=True)

    instances     = db.relationship('List', backref='list_type', lazy='dynamic')

    def __repr__(self):
        return '<ListType {}>'.format( self.name )
