import os, datetime, markdown
from flask import render_template, flash, redirect, url_for, request, send_from_directory, Markup
from werkzeug.urls import url_parse
from werkzeug.datastructures import MultiDict
from app import app, db
from app.forms import LoginForm, RegistrationForm, NewListForm, HiddenTagForm
import app.utils as utils
from config import Config

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, List, ListType
from app.list_types import *

import app.data_management as dataManage

import click

@app.route('/')
@app.route('/index', methods=['GET'])
@login_required
def index():

    remove_id = request.args.get('remove')
    if remove_id != None:
        dataManage.removeList( remove_id )
        return redirect(url_for('index'))

    all_lists = sorted(List.query.all(), key=lambda x: x.name)

    public_lists = list(filter(lambda x: x.is_public(),all_lists))
    shared_lists = list(filter(lambda x: x.is_shared( current_user ),all_lists))
    private_lists = list(filter(lambda x: x.is_private( current_user ),all_lists))

    can_write = {}
    for list_ in all_lists:
        can_write[list_.id] = current_user.can_write(list_)

    return render_template('index.html', title='Home', public_lists = public_lists, 
                                         private_lists = private_lists, shared_lists = shared_lists, 
                                         time_format = Config.TIME_FORMAT, can_write = can_write, is_admin=current_user.is_admin )

@app.route('/new_list', methods=['GET', 'POST'])
@login_required
def new_list():
    form = NewListForm()
    form.set_current_user(current_user.username) 

    editMode = False
    edit_id = request.args.get('edit')
    if not edit_id is None:
        exists, the_list = dataManage.getList(edit_id, checkWriteAccess=True, checkReadAccess=True)

        if not exists:
            flash("List not found.","warning")
            return redirect(url_for('index'))

        the_list.fill_form( form )
        editMode = True

    if not editMode and request.method == 'GET':
        isPublic = not request.args.get('public') is None
        if isPublic:
            form.set_public()

    if request.method == 'POST':
        if not editMode:
            the_list = List()

        the_list.fill_list_from_form( current_user )
        dataManage.addOrUpdateList(the_list,updateMode=editMode)

        return redirect(url_for('index', _anchor=the_list.getAnchor(current_user)))

    return render_template('new_list.html', title='New List', form=form, submit_text="Edit List" if editMode else "Create List")

@app.route('/view_list', methods=['GET'])
@login_required
def view_list():
    list_id = request.args.get('id')
    
    exists, the_list = dataManage.getList(list_id, checkReadAccess=True)
    if not exists:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))
    
    list_entry_class = eval(the_list.list_type.name)

    remove_id = request.args.get('remove')
    if remove_id != None and current_user.can_write(the_list):
        dataManage.removeEntry( the_list, remove_id )
        return redirect(url_for('view_list', id = list_id))

    entries = dataManage.getListEntries( the_list, inOrder=True )
    return render_template(os.path.join('list_templates',the_list.list_type.template), title='{}'.format(the_list.name), 
                                        list=the_list, entries=entries, can_write=current_user.can_write(the_list), time_format = Config.TIME_FORMAT)

@app.route('/new_entry', methods=['GET','POST'])
@login_required
def new_entry():

    list_id  = request.args.get('id')
    entry_id = request.args.get('edit')

    exists, the_list = dataManage.getList(list_id, checkWriteAccess=True, checkReadAccess=True)
    if not exists:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))


    the_entry = DefaultList()
    form_preset = the_entry.get_form_preset(virgin=True)

    updateMode = False
    if entry_id != None:
        exists, the_entry = dataManage.getEntry(the_list,entry_id)
        if not exists:
            flash('Entry not found', 'warning')
        else:
            form_preset = the_entry.get_form_preset(virgin=False)
            updateMode = True

    if request.method == 'POST':
        good, message = the_entry.fill_entry_from_form( the_list )
        if not good:
            flash(message, 'danger')
            return redirect(url_for('new_entry', id = the_list.id))
        
        dataManage.addOrUpdateEntry(the_entry,updateMode=updateMode)

        #TODO: redirect in the correct entry anchor
        return redirect(url_for('view_list', id = the_list.id))


    return render_template(the_list.list_type.get_template_path(), 
                           title='New Entry', list=the_list, form=HiddenTagForm(), 
                           form_preset=form_preset, submit_text="Update Entry" if updateMode else "Create Entry")

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

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a Timelist registered user!', 'info')
#         return redirect(url_for('login'))
#     else:
#         flash_errors( form )

#     return render_template('register.html', title='Register', form=form)

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html', title='Profile' )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# @app.route('/uploads/<path:filename>')
# @login_required
# def download_file( filename ):
#     list_uuid = request.args.get('list_uuid')
#     entry_uuid = request.args.get('entry_uuid')
#     print('\n\nl', list_uuid, 'e', entry_uuid, 'f', filename, '\n\n')
#     path = os.path.join( Config.TL_DB_PATH, list_uuid, 'entries', entry_uuid, 'assets' )
#     return send_from_directory(path, filename, as_attachment=True)
