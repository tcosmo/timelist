import os, json, time
from datetime import datetime
import pprint

from flask import Flask
from config import Config
from flask import Markup

from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .tl_parsing import parse_title, get_raw_bib, get_body_content, parse_time_mark, time_mark_to_tuple

app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)

pp = pprint.PrettyPrinter(width=41, compact=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models
