from app import app

#import time

#print('hello')
#time.sleep( 5 )

from app import app, db
from app.models import User, List

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'List': List}