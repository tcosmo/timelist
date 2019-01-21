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

    all_lists = List.query.all()

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
    if edit_id:
        query_answer = List.query.filter_by(id=edit_id).all()
        if len(query_answer) == 0 or not current_user.can_write(query_answer[0]):
            flash("List not found.","warning")
            return redirect(url_for('index'))

        the_list = query_answer[0]
        form.list_name = the_list.name
        form.all_read = the_list.all_read
        form.all_write = the_list.all_write
        form.default_order_desc = the_list.default_order_desc
        print( form.default_order_desc )
        if form.all_read:
            for x in form.list_users:
                x['readChecked'] = True
        else:
            nameCanRead = [u.username for u in the_list.read_by_users]
            print('Can Read:', nameCanRead)
            for x in form.list_users:
                if x['name'] in nameCanRead:
                    print("hello")
                    x['readChecked'] = True
        if form.all_write:
            for x in form.list_users:
                x['writeChecked'] = True
        else:
            nameCanWrite = [u.username for u in the_list.written_by_users]
            print('Can Write:', nameCanWrite)
            for x in form.list_users:
                if x['name'] in nameCanWrite:
                    x['writeChecked'] = True


        for lt in form.list_type:
            lt['checked'] = lt['name'] == the_list.list_type.name

        editMode = True

    if request.method == 'POST':
        if not editMode:
            new_list = List()
        else:
            new_list = the_list
        new_list.name = request.form.get('list_name')  # access the data inside
        new_list.list_type = ListType.query.filter_by(name = request.form.get('list_type') ).first()
        new_list.all_read = request.form.get('read-all') == "true"
        new_list.all_write = request.form.get('write-all') == "true"


        new_list.default_order_desc = request.form['gender'] == 'desc'

        if not new_list.all_read:
            new_list.read_by_users.append( current_user )
            for user in request.form.getlist('can_read'):
                u = User.query.filter_by(username = user).first()
                new_list.read_by_users.append( u )

        if not new_list.all_write:
            new_list.written_by_users.append( current_user )
            for user in request.form.getlist('can_write'):
                u = User.query.filter_by(username = user).first()
                new_list.written_by_users.append( u )

        # TODO log to systemd
        print("Creating list:")
        print(new_list.id)
        print(new_list.name)
        print(new_list.list_type )
        print(new_list.all_read)
        print(new_list.all_write)
        print(new_list.read_by_users)
        print(new_list.written_by_users)

        if not editMode:
            db.session.add(new_list)
        db.session.commit()

        flash('List {} successfully {}.'.format(new_list.name, 'edited' if editMode else 'created'), 'success')
        
        anchor = ""
        if new_list.is_private(current_user):
            anchor = "private"
        if new_list.is_shared(current_user):
            anchor = "shared"
        if new_list.is_public():
            anchor = "public"

        #TODO: redirect in the correct tab
        return redirect(url_for('index', _anchor=anchor))

    return render_template('new_list.html', title='New List', form=form, submit_text="Edit List" if editMode else "Create List")

@app.route('/view_list', methods=['GET'])
@login_required
def view_list():

    list_id = request.args.get('id')

    if list_id == None:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))

    query_answer = List.query.filter_by( id = list_id ).all()

    if len(query_answer) != 0:
        the_list = query_answer[0]
    if len(query_answer) == 0 or not current_user.can_read(the_list):
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))

    list_entry_class = eval(the_list.list_type.name)

    remove_id = request.args.get('remove')
    if remove_id != None and current_user.can_write(the_list):
        print("Remove entry")
        print(list_entry_class.query.filter_by(id=remove_id).all())
        list_entry_class.query.filter_by(id=remove_id).delete()
        the_list.last_modified = datetime.datetime.utcnow()
        db.session.commit()
        return redirect(url_for('view_list', id = list_id))



    entries = list_entry_class.query.filter_by(list_id=the_list.id).all()
    entries.sort(key=lambda x: (x.year,x.month,x.day))

    if the_list.default_order_desc:
        entries = entries[::-1]

    can_write = current_user.can_write(the_list)

    return render_template(os.path.join('list_templates',the_list.list_type.template), title='{}'.format(the_list.name), 
                                        list=the_list, entries=entries, can_write=can_write, time_format = Config.TIME_FORMAT)


@app.route('/new_entry', methods=['GET','POST'])
@login_required
def new_entry():

    list_id = request.args.get('id')

    if list_id == None:
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))

    query_answer = List.query.filter_by( id = list_id ).all()

    if len(query_answer) != 0:
        the_list = query_answer[0]
    if len(query_answer) == 0 or not current_user.can_read(the_list) or not current_user.can_write(the_list):
        flash('The list was not found.', 'warning')
        return redirect(url_for('index'))

    form = HiddenTagForm()
    list_entry_class = eval(the_list.list_type.name)

    now = datetime.datetime.now()
    entry_id = request.args.get('edit')

    form_preset = { 'day': now.day,
                    'month': now.month,
                    'year': now.year,
                    'title': '',
                    'content': '# Notes' } #initial content same as base.html:34

    submit_text = "Create Entry" 

    the_entry = DefaultList()
    updateMode = False

    if entry_id != None:
        entry_query = list_entry_class.query.filter_by(id=entry_id).all()
        if len(entry_query) == 0:
            flash('Entry not found', 'warning')
        else:
            the_entry = entry_query[0]
            form_preset['day'] = the_entry.day
            form_preset['month'] = the_entry.month
            form_preset['year'] = the_entry.year
            form_preset['title'] = the_entry.title
            form_preset['content'] = the_entry.content
            submit_text = "Update Entry" 
            updateMode = True

    

    if request.method == 'POST':
        the_entry.list_id = the_list.id
        the_entry.day = request.form.get('day')
        the_entry.month = request.form.get('month')
        the_entry.year = request.form.get('year')

        if not the_entry.day.isnumeric() or not the_entry.month.isnumeric() or not the_entry.year.isnumeric():
            flash('Fields day/month/year must be numerics.', 'danger')
            return redirect(url_for('new_entry', id = the_list.id))

        the_entry.title = request.form.get('title')
        raw_content = request.form.get('content')
        the_entry.content = utils.reformate_markdown( raw_content )

        if not updateMode:
            the_entry.static_folder = utils.createNewEntryFolder()

        the_entry.last_modified = datetime.datetime.utcnow()
        the_list.last_modified = datetime.datetime.utcnow()

        print("{} Entry".format("Update" if updateMode else "New"))
        print(the_entry.id)
        print(the_entry.day)
        print(the_entry.month)
        print(the_entry.year)
        print(the_entry.title)
        print(the_entry.content)

        if not updateMode:
            db.session.add(the_entry)
        db.session.commit()

        flash('Entry successfully {}.'.format('updated' if updateMode else 'created'), 'success')
        #TODO: redirect in the correct tab
        return redirect(url_for('view_list', id = the_list.id))

    #entries = list_entry_class.query.filter_by(list_id=the_list.id).all()
    return render_template(os.path.join('list_templates','new_entry_'+the_list.list_type.template), title='New Entry', list=the_list, form=form, form_preset=form_preset, submit_text=submit_text )


# @app.route('/list', methods=['GET'])
# @login_required
# def list():
#     list_uuid = request.args.get('uuid')
#     list_id   = lists_uuid_to_id[ list_uuid ]
#     list_name = available_lists[ list_id ][ 'name' ]
#     print( available_lists[ list_id ][ 'entries' ][ 0 ][ 'quickaccess'] )
#     return render_template('list.html', title='List View', list_name = list_name, entries = available_lists[ list_id ][ 'entries' ] )

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
