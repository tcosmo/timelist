import os

from datetime import datetime
from app import db, login

from flask import flash, request
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

        return hash_ == hash2_

    def can_read(self, list_ ):
        return list_.all_read or (list_ in self.readable_lists)

    def can_write(self, list_ ):
        return list_.all_write or (list_ in self.writable_lists)

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
        if self.is_public():
            return False

        if len( self.written_by_users ) == 1 and len( self.read_by_users ) == 1:
                if current_user.can_read( self ) and current_user.can_write( self ):
                    return True
        return False

    def is_shared(self, current_user):
        if not self.is_public() and not self.is_private(current_user):
            if current_user.can_read( self ):
                return True
        return False

    def getAnchor( self, current_user ):
        if self.is_private(current_user):
            return "private"
        if self.is_shared(current_user):
            return "shared"
        return "public"

    def fill_list_from_form( self, current_user ):
        self.name = request.form.get('list_name')  # access the data inside
        self.list_type = ListType.query.filter_by(name = request.form.get('list_type') ).first()
        self.all_read = request.form.get('read-all') == "true"
        self.all_write = request.form.get('write-all') == "true"

        self.default_order_desc = request.form['gender'] == 'desc'

        if not self.all_read:
            self.read_by_users = []
            self.read_by_users.append( current_user )
            for user in request.form.getlist('can_read'):
                u = User.query.filter_by(username = user).first()
                self.read_by_users.append( u )

        if not self.all_write:
            self.written_by_users = []
            self.written_by_users.append( current_user )
            for user in request.form.getlist('can_write'):
                u = User.query.filter_by(username = user).first()
                self.written_by_users.append( u )

        self.last_modified = datetime.now()

    def fill_form(self, form):
        form.list_name = self.name
        form.all_read = self.all_read
        form.all_write = self.all_write
        form.default_order_desc = self.default_order_desc
        
        if form.all_read:
            for x in form.list_users:
                x['readChecked'] = True
        else:
            nameCanRead = [u.username for u in self.read_by_users]
            for x in form.list_users:
                if x['name'] in nameCanRead:
                    x['readChecked'] = True
        if form.all_write:
            for x in form.list_users:
                x['writeChecked'] = True
        else:
            nameCanWrite = [u.username for u in self.written_by_users]
            for x in form.list_users:
                if x['name'] in nameCanWrite:
                    x['writeChecked'] = True

        for lt in form.list_type:
            lt['checked'] = lt['name'] == self.list_type.name

    def __repr__(self):
        return '<List id:{} name:{}>'.format( self.id, self.name )

class ListType(db.Model):
    id            = db.Column(db.Integer, index=True, primary_key=True)
    name          = db.Column(db.String, index=True, unique=True)
    template      = db.Column(db.String, index=True)

    description = db.Column(db.String, index=True)

    instances     = db.relationship('List', backref='list_type', lazy='dynamic')


    def get_template_path( self ):
        return os.path.join('list_templates','new_entry_'+self.template)

    def __repr__(self):
        return '<ListType {}>'.format( self.name )
