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
    for ligne in raw_content.split("\r\n"):
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

def createNewEntryFolder( filename = None ):

    if filename is None:
        filename = str(uuid.uuid4().hex)

    myLogger("Creating entry folder {}".format(filename))

    while os.path.exists('entries/'+filename):
        filename = str(uuid.uuid4().hex)

    os.makedirs('entries/'+filename)

    return filename

def removeEntryFolder( folderName ):
    myLogger("Deleting entry folder {}".format(folderName))
    shutil.rmtree('entries/'+folderName, ignore_errors=True)

class runEntrySanityCheck( object ):
    memoizer = {}
    def runEntrySanityCheck( list_id, entries ):
        """ Creates entry folder with appropriate name if doesn't exist.
        """
        myLogger("Running entry folder sanity check for list {}".format(list_id))
        if list_id in runEntrySanityCheck.memoizer:
            myLogger("Already done, aborting".format(list_id))
            return

        runEntrySanityCheck.memoizer[list_id] = True

        for entry in entries:
            if not os.path.exists('entries/'+entry.static_folder):
                myLogger("Static folder needed for entry {}".format(entry.id))
                createNewEntryFolder(entry.static_folder)

fileFontAwesome = { 
    'gif': 'file-image-o',
    'jpeg': 'file-image-o',
    'jpg': 'file-image-o',
    'png': 'file-image-o',

    'pdf': 'file-pdf-o',

    'doc': 'file-word-o',
    'docx': 'file-word-o',

    'ppt': 'file-powerpoint-o',
    'pptx': 'file-powerpoint-o',

    'xls': 'file-excel-o',
    'xlsx': 'file-excel-o',

    'aac': 'file-audio-o',
    'mp3': 'file-audio-o',
    'ogg': 'file-audio-o',

    'avi': 'file-video-o',
    'flv': 'file-video-o',
    'mkv': 'file-video-o',
    'mp4': 'file-video-o',

    'gz': 'file-zip-o',
    'zip': 'file-zip-o',

    'css': 'file-code-o',
    'html': 'file-code-o',
    'js': 'file-code-o',
    'rs': 'file-code-o',
    'py': 'file-code-o',
    'c': 'file-code-o',
    'cpp': 'file-code-o',
    'nix': 'file-code-o',

    'txt': 'file-text-o',
    'md': 'file-text-o',

    'file': 'file' }

def getFontAwesomeTag( filename ):
    global fileFontAwesome
    if not '.' in filename:
        extension = 'file'
    else:
        extension = filename.split('.')[-1]

    if not extension in fileFontAwesome:
        extension = 'file'

    return fileFontAwesome[extension]

def nameOfACopy( name ):
    if not '.' in name:
        return name + ' - copy'

    n,e = name.split('.')
    return n + ' - copy'+'.'+e