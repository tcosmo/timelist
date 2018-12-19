import os
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app import app 
from app.forms import LoginForm
from config import Config

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', lists = available_lists)

@app.route('/list', methods=['GET'])
def list():
    list_uuid = request.args.get('uuid')
    list_id   = lists_uuid_to_id[ list_uuid ]
    list_name = available_lists[ list_id ][ 'name' ]
    print( available_lists[ list_id ][ 'entries' ][ 0 ][ 'quickaccess'] )
    return render_template('list.html', title='List View', list_name = list_name, entries = available_lists[ list_id ][ 'entries' ] )

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/uploads/<path:filename>')
def download_file( filename ):
    list_uuid = request.args.get('list_uuid')
    entry_uuid = request.args.get('entry_uuid')
    print('\n\nl', list_uuid, 'e', entry_uuid, 'f', filename, '\n\n')
    path = os.path.join( Config.TL_DB_PATH, list_uuid, 'entries', entry_uuid, 'assets' )
    return send_from_directory(path, filename, as_attachment=True)