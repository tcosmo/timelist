import enum

from app import db
from sqlalchemy import Enum

from datetime import datetime

class DefaultList(db.Model):
    """ Represents a default list, e.g. the group meeting list.
    """
    id            = db.Column(db.Integer, primary_key=True)
    created       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    static_folder = db.Column(db.String, index=True, unique=True)

    year          = db.Column(db.Integer, primary_key=True)
    month         = db.Column(db.Integer, primary_key=True)
    day           = db.Column(db.Integer, primary_key=True)

    title         = db.Column(db.String, index=True)
    content       = db.Column(db.String, index=True)

# class PaperClarityLevel(enum.Enum):
#     NotRead  = 0
#     NotClear = 1
#     Ok       = 2

class BiblioList(db.Model):
    """ Represents a list of papers/reading. 

        Warning: could not use inheritance from DefaultList in the 
        code due to sqlalchemy inner mechanism.
        c.f. https://docs.sqlalchemy.org/en/latest/orm/inheritance.html
    """
    id            = db.Column(db.Integer, primary_key=True)
    created       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    static_folder = db.Column(db.String, index=True, unique=True)

    year          = db.Column(db.Integer, primary_key=True)
    month         = db.Column(db.Integer, primary_key=True)
    day           = db.Column(db.Integer, primary_key=True)

    title         = db.Column(db.String, index=True)
    content       = db.Column(db.String, index=True)

    pdf_file           = db.Column(db.String, index=True)
    annotated_pdf_file = db.Column(db.String, index=True)
    link               = db.Column(db.String, index=True)
    tldr_file          = db.Column(db.String, index=True)
    bibtex_file        = db.Column(db.String, index=True)
    bibtex_content     = db.Column(db.String, index=True)
    more               = db.Column(db.Boolean, index=True, default=False)#if more stuff to share, should open asset directory

    clarity_level      = db.Column(db.Integer)