from app import app

#import time

#print('hello')
#time.sleep( 5 )

from app import app, db
import app.utils as utils
from app.models import User, List, ListType
from app.list_types import DefaultList, BiblioList

import os, click
click.echo("Working directory: {}".format(os.getcwd()))
click.echo("Home directory: {}".format(os.getenv("HOME")))
click.echo("Current user: {}".format(os.getuid()))

if not os.path.isdir('entries'):
	click.echo("Entries folder not found, aborting.")
	exit(1)
else:
	click.echo("Entries folder found.")

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'List': List, 'WriteUserList': WriteUserList, 'ListType': ListType,
    		'DefaultList': DefaultList, 'BiblioList': BiblioList }
