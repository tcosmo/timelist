import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "ZWQ1NjE4OTZkOGU2MWVjNjU2ODY5Zjg0"
    #TL_DB_PATH = os.environ.get('TL_DB_PATH') or "/home/cosmo/Documents/projects/timelist-db"
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://cosmo:cosmo@127.0.0.1:5432/timelist'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TIME_FORMAT = "%b %d %Y %H:%M:%S"

