import os
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from werkzeug.urls import url_parse
from app import app 
from app.forms import LoginForm, RegistrationForm, NewListForm
from config import Config

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, List, ReadUserList, WriteUserList, ListType
from app.list_types import DefaultList, BiblioList

@app.route('/')
@app.route('/index')
@login_required
def index():
    public_lists = List.query.filter( List.all_read ).all()
    
    #TODO: do better by SQLing the query
    all_lists = List.query.all()
    private_lists = []
    
    for list_ in all_lists:
        if not list_.all_read:
            if  len( list_.wrote_by_users ) == 1 and len( list_.read_by_users ) == 1:
                if current_user.can_read( list_ ) and current_user.can_write( list_ ):
                    private_lists.append(list_)

    shared_lists = []
    for list_ in all_lists:
        if not list_.all_read and not list_ in private_lists:
            print( list_ )
            if current_user.can_read( list_ ):
                shared_lists.append(list_)

    return render_template('index.html', title='Home', public_lists = public_lists, private_lists = private_lists, shared_lists = shared_lists )

@app.route('/new_list', methods=['GET', 'POST'])
@login_required
def new_list():
    form = NewListForm()


    return render_template('new_list.html', title='New List', form=form)

@app.route('/list', methods=['GET'])
@login_required
def list():
    list_uuid = request.args.get('uuid')
    list_id   = lists_uuid_to_id[ list_uuid ]
    list_name = available_lists[ list_id ][ 'name' ]
    print( available_lists[ list_id ][ 'entries' ][ 0 ][ 'quickaccess'] )
    return render_template('list.html', title='List View', list_name = list_name, entries = available_lists[ list_id ][ 'entries' ] )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'warning')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'warning')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a Timelist registered user!', 'info')
        return redirect(url_for('login'))
    else:
        flash_errors( form )
    
    return render_template('register.html', title='Register', form=form)

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html', title='Profile' )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/uploads/<path:filename>')
@login_required
def download_file( filename ):
    list_uuid = request.args.get('list_uuid')
    entry_uuid = request.args.get('entry_uuid')
    print('\n\nl', list_uuid, 'e', entry_uuid, 'f', filename, '\n\n')
    path = os.path.join( Config.TL_DB_PATH, list_uuid, 'entries', entry_uuid, 'assets' )
    return send_from_directory(path, filename, as_attachment=True)