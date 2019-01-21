import os, uuid, config
import shutil
import datetime
import click

from flask_login import current_user
import flask

def myLogger( message ):
    username = "anonymous" if current_user.is_anonymous else current_user.username
    click.echo(flask.request.host.split(":")[0] + " - - "+datetime.datetime.now().strftime('[%d/%b/%Y %H:%M:%S]')+" {} ".format(username)+"{}".format(message))


def reformate_markdown(raw_content):
    """ Converts `SimpleMDE` Markdown to python markdown.markdown.
    """
    to_return = ""
    print(raw_content)
    for ligne in raw_content.split("\r\n"):
        print("#", ligne.strip())
        #if len(ligne.strip()) == 0:

        if len(ligne) != 0 and '#' in ligne and ligne.strip()[0] == '#':
            to_return += ligne + "\n"
        else:
            to_return += ligne + "   " +"\n"


    to_return = to_return.replace('*','-')

    return to_return

def timeMarkToStr( tm ):
    """ Transforms int 9 to 09 for pretty date printing.
    """
    if len(str(tm)) == 1:
        return "0"+str(tm)
    return str(tm)

def createNewEntryFolder():
    filename = str(uuid.uuid4().hex)

    while os.path.exists('entries/'+filename):
        filename = str(uuid.uuid4().hex)

    os.makedirs('entries/'+filename)

    return filename

def removeEntryFolder( folderName ):
    shutil.rmtree('entries/'+folderName, ignore_errors=True)
