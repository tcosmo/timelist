import os, json, time, logging, sys
from datetime import datetime
import pprint

from flask import Flask
from config import Config
from flask import Markup

from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager

from .tl_parsing import parse_title, get_raw_bib, get_body_content, parse_time_mark, time_mark_to_tuple


app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)

pp = pprint.PrettyPrinter(width=41, compact=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = "warning"

from app import routes, models, list_types

db.init_app(app)