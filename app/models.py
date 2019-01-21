from datetime import datetime
from app import db, login

from flask import flash
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import ARRAY

import passlib.hash

import app.utils as utils

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), index=True, unique=True)
    email         = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin      = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        i = self.password_hash[0] == "$"
        hash_split = self.password_hash[i:].split("$")

        if len(hash_split) != 3:
            utils.myLogger("Serious issue with login, please contact an admin.")
            flash("Serious issue with login, please contact an admin.", "danger")
            return False
        method, salt, hash_ = hash_split

        utils.myLogger("Loggin attempt, method {}.".format(method))

        if method != "apr1":
            return check_password_hash(self.password_hash, password)

        _, _, hash2_ = passlib.hash.apr_md5_crypt(salt).hash(password,salt=salt)[1:].split('$')

        print(salt, hash_,hash2_)

        return hash_ == hash2_

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

    default_order_desc = db.Column(db.Boolean, default=True)

    all_read      = db.Column(db.Boolean, index=True, default=False)
    all_write     = db.Column(db.Boolean, index=True, default=False)

    read_by_users = db.relationship('User', secondary=ReaduUserList, backref='readable_lists')
    written_by_users = db.relationship('User', secondary=WriteUserList, backref='writable_lists')

    def is_public(self):
        return self.all_read

    def is_private(self, current_user):
        if  len( self.written_by_users ) == 1 and len( self.read_by_users ) == 1:
                if current_user.can_read( self ) and current_user.can_write( self ):
                    return True
        return False

    def is_shared(self, current_user):
        if self.is_public() and not self.is_private(current_user):
            if current_user.can_read( self ):
                return True
        return False

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
