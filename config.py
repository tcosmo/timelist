import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "ZWQ1NjE4OTZkOGU2MWVjNjU2ODY5Zjg0"
    TL_DB_PATH = os.environ.get('TL_DB_PATH') or "/home/cosmo/Documents/projects/timelist-db"
