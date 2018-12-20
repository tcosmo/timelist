from app import app

#import time

#print('hello')
#time.sleep( 5 )

from app import app, db
from app.models import User, List, ReadUserList, WriteUserList, ListType
from app.list_types import DefaultList, BiblioList

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'List': List, 'ReadUserList': ReadUserList, 'WriteUserList': WriteUserList, 'ListType': ListType,
    		'DefaultList': DefaultList, 'BiblioList': BiblioList }