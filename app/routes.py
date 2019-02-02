import os, datetime, markdown
from flask import render_template, flash, redirect, url_for, request, send_from_directory, Markup, abort
from werkzeug.urls import url_parse
from werkzeug.datastructures import MultiDict
from app import app, db
from app.forms import LoginForm, RegistrationForm, NewListForm, HiddenTagForm
import app.utils as utils
from config import Config

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, List, ListType
from app.list_types import *

from werkzeug.utils import secure_filename

import app.data_management as dataManage

import click

@app.route('/')
@app.route('/index', methods=['GET'])
@login_required
def index():
    """ Main view.
    """
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

    return render_template('index.html', title='', public_lists = public_lists, 
                                         private_lists = private_lists, shared_lists = shared_lists, 
                                         time_format = Config.TIME_FORMAT, can_write = can_write, is_admin=current_user.is_admin )

@app.route('/new_list', methods=['GET', 'POST'])
@login_required
def new_list():
    """ New list creation.
    """
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
    """ List view.
    """
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
    utils.runEntrySanityCheck.runEntrySanityCheck(list_id, entries)

    return render_template(os.path.join('list_templates',the_list.list_type.template), title='{}'.format(the_list.name), 
                                        list=the_list, entries=entries, can_write=current_user.can_write(the_list), time_format = Config.TIME_FORMAT)

@app.route('/new_entry', methods=['GET','POST'])
@login_required
def new_entry():
    """ New entry creation.
    """
    list_id  = request.args.get('id')
    entry_id = request.args.get('edit')

    exists, the_list = dataManage.getList(list_id, checkWriteAccess=True, checkReadAccess=True)
    if not exists:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))


    the_entry = eval(the_list.list_type.name)()
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
            return redirect(request.url)
        
        dataManage.addOrUpdateEntry(the_entry,updateMode=updateMode)

        #TODO: redirect in the correct entry anchor
        return redirect(url_for('view_list', id = the_list.id, _anchor='entry-{}'.format(the_entry.id)))


    return render_template(the_list.list_type.get_template_path(), 
                           title='New Entry', list=the_list, form=HiddenTagForm(), 
                           form_preset=form_preset, updateMode=updateMode, the_entry=the_entry)

@app.route('/folder', methods=['GET','POST'])
@login_required
def folder():


    list_id  = request.args.get('list')
    entry_id = request.args.get('entry')

    if list_id is None or entry_id is None:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))
    exists, the_list = dataManage.getList(list_id, checkReadAccess=True)
    if not exists:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))
    exists, the_entry = dataManage.getEntry(the_list, entry_id)
    if not exists:        
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))

    remove_id = request.args.get('remove')
    if remove_id != None and current_user.can_write(the_list):
        success, filename = dataManage.removeStaticFile( the_entry, int(remove_id) )
        if success:
            flash('File "{}" successfully removed.'.format(filename), 'success')
        else:
            flash('File not found.', 'warning')
        return redirect(url_for('folder', list = the_list.id, entry=the_entry.id))


    file_list = dataManage.getStaticFiles(the_entry)

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No selected file.', 'warning')
            return redirect(request.url)
        file = request.files['file']

        if not (file is None) and current_user.can_write(the_list):
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file.', 'warning')
                return redirect(request.url)

            filename = secure_filename(file.filename)
            list_names = [ f['name'] for f in file_list ]
            while filename in list_names:
                filename = utils.nameOfACopy(filename)
            
            dataManage.addStaticFile(the_entry,file,filename)
            flash('File successfully uploaded.', 'success')
            return redirect(url_for('folder', list = the_list.id, entry=the_entry.id))


    return render_template("folder.html", the_list = the_list, the_entry = the_entry,
                           title='Folder', file_list=file_list, entry_folder=the_entry.static_folder, can_write=current_user.can_write(the_list))

@app.route('/files', methods=['GET'])
@login_required
def download_file():
    list_id  = request.args.get('list')
    entry_id = request.args.get('entry')
    file_id = request.args.get('file')

    if list_id is None or entry_id is None or file_id is None:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))
    exists, the_list = dataManage.getList(list_id, checkReadAccess=True)
    if not exists:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))
    exists, the_entry = dataManage.getEntry(the_list, entry_id)
    if not exists:        
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))

    exists,filepath,filename = dataManage.getStaticFile(the_entry, int(file_id))
    if not exists:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))

    utils.myLogger("Downloading file {} {}".format(filepath,filename))
    return send_from_directory(filepath, filename, as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Login view.
    """
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

@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if not current_user.is_admin:
        return abort(404)
    return render_template('admin.html', title='Admin' )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))