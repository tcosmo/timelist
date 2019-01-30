import os
from flask import flash
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, List, ListType

import app.utils as utils
from app.list_types import *

import click

def getList(list_id, checkWriteAccess=False, checkReadAccess=False):
    query_result = List.query.filter_by(id=list_id).all()

    if len(query_result) == 0:
        return False, None

    the_list = query_result[0]

    if checkReadAccess and not current_user.can_read(the_list):
        return False, None

    if checkWriteAccess and not current_user.can_write(the_list):
        return False, None

    return True, the_list

def getEntry( the_list, entry_id ):
    list_entry_class = eval(the_list.list_type.name)
    entry_query = list_entry_class.query.filter_by(id=entry_id).all()
    
    if len(entry_query) == 0:
        return False, None

    return True, entry_query[0]

def getStaticFiles( the_entry ):
    if not os.path.exists('entries/'+the_entry.static_folder):
        utils.myLogger("Static folder {} of ({},{}) not found.".format(the_entry.static_folder,the_entry.list_id,the_entry.id))
        flash('System error, please report.', 'danger')
        return []

    directory_content = os.listdir('entries/'+the_entry.static_folder)

    true_content = []

    for f in directory_content:
        if os.path.isfile(os.path.join('entries', the_entry.static_folder, f)) and f[0]!='.':
           true_content.append({'name':f,'fontAwesome':utils.getFontAwesomeTag(f)})

    true_content.sort( key=lambda x: x['name'] )
    for k in range(len(true_content)):
        true_content[k]['id'] = k
    return true_content

def getStaticFile( the_entry, file_id ):
    static_files = getStaticFiles( the_entry )

    if file_id >=0 and file_id < len(static_files):
        return True,os.path.join(os.getcwd(),'entries',the_entry.static_folder),static_files[file_id]['name']

    return False, None

def addStaticFile( the_entry, file, filename ):

    file.save(os.path.join(os.getcwd(),'entries',the_entry.static_folder, filename))

    return

def addOrUpdateEntry(the_entry,updateMode=False):

    if not updateMode:
        utils.myLogger("Creating entry {}".format(the_entry))
        the_entry.static_folder = utils.createNewEntryFolder()
        db.session.add(the_entry)
    else:
        utils.myLogger("Updating entry {}".format(the_entry))

    db.session.commit()

    utils.myLogger("Entry {} {}".format(the_entry, "updated" if updateMode else "created"))

    flash('Entry successfully {}.'.format('updated' if updateMode else 'created'), 'success')

def addOrUpdateList(the_list,updateMode=False):
    if not updateMode:
        utils.myLogger("Creating list {}".format(the_list))
        db.session.add(the_list)
    else:
        utils.myLogger("Updating list {}".format(the_list))

    db.session.commit()
    utils.myLogger("List {} {}".format(the_list, "updated" if updateMode else "created"))

    flash('List {} successfully {}.'.format(the_list.name, 'edited' if updateMode else 'created'), 'success')


def getListEntries( the_list, inOrder = False ):
    list_entry_class = eval(the_list.list_type.name)

    entries = list_entry_class.query.filter_by(list_id=the_list.id).all()

    if inOrder:
        entries.sort(key=lambda x: (x.year,x.month,x.day))
        if the_list.default_order_desc:
            entries = entries[::-1]

    return entries

def removeEntry( the_list, entry_id ):

    exists, the_entry = getEntry(the_list,entry_id)

    if not ( exists and current_user.can_write(the_list) ):
        flash("The entry was not found.", "warning")
        return

    utils.removeEntryFolder( the_entry.static_folder )
    db.session.delete( the_entry )
    the_list.last_modified = datetime.utcnow()
    db.session.commit()


def removeList( list_id ):    
    query_result = List.query.filter_by(id=list_id).all()

    exists, the_list = getList( list_id, checkWriteAccess=True )

    if not exists:
        flash("The list was not found.", "warning")
        return

    utils.myLogger("Removing list {}".format(the_list))

    the_list.written_by_users = []
    the_list.read_by_users = []
    
    entries = getListEntries( the_list )

    for entry in entries:
        utils.myLogger("\tRemoving entry {}".format(entry))
        utils.myLogger("\tRemoving entry folder {}".format(entry.static_folder))
        utils.removeEntryFolder( entry.static_folder )
        db.session.delete(entry)

    db.session.delete(the_list)
    
    db.session.commit()

    utils.myLogger("List removed")
    flash('The list "{}" was deleted.'.format(the_list.name), "success")
