from flask import flash
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, List, ListType

import app.utils as utils
from app.list_types import *

import click

def getList(list_id, checkWriteAccess=True):
    query_result = List.query.filter_by(id=list_id).all()

    if len(query_result) == 0:
        return False, None

    the_list = query_result[0]
    if checkWriteAccess and not current_user.can_write(the_list):
        return False, None

    return True, the_list

def getListEntries( the_list ):
    list_entry_class = eval(the_list.list_type.name)

    entries = list_entry_class.query.filter_by(list_id=the_list.id).all()

    return entries

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
