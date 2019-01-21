import enum, markdown

from app import db
from sqlalchemy import Enum

from datetime import datetime

from flask import Markup

from app.utils import timeMarkToStr

class DefaultList(db.Model):
    """ Represents a default list entry, e.g. the group meeting list.
    """
    id            = db.Column(db.Integer, primary_key=True)
    list_id       = db.Column(db.Integer, db.ForeignKey('list.id'), index=True)

    created       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    static_folder = db.Column(db.String, index=True, unique=True)

    year          = db.Column(db.Integer, index=True)
    month         = db.Column(db.Integer, index=True)
    day           = db.Column(db.Integer, index=True)

    title         = db.Column(db.String, index=True)
    content       = db.Column(db.String, index=True)

    def getFormattedContent( self ):
        return Markup(markdown.markdown(self.content))

    def getFormattedDate( self ):
        first_try = "/".join( [ timeMarkToStr(self.day), timeMarkToStr(self.month), timeMarkToStr(self.year) ] )
        if first_try[ 0 ] == '/':
            first_try = first_try[ 1: ]

        if first_try[ 0 ] == '/':
            first_try = first_try[ 1: ]

        if len( first_try ) == 0:
            first_try = "Future"
        return first_try

    def __repr__(self):
        return "<Entry {}>".format(self.title)

# class PaperClarityLevel(enum.Enum):
#     NotRead  = 0
#     NotClear = 1
#     Ok       = 2

class BiblioList(db.Model):
    """ Represents a list entry of papers/reading. 

        Warning: could not use inheritance from DefaultList in the 
        code due to sqlalchemy inner mechanism.
        c.f. https://docs.sqlalchemy.org/en/latest/orm/inheritance.html
    """
    id            = db.Column(db.Integer, primary_key=True)
    list_id       = db.Column(db.Integer, db.ForeignKey('list.id'), index=True)

    created       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    static_folder = db.Column(db.String, index=True, unique=True)

    year          = db.Column(db.Integer)
    month         = db.Column(db.Integer)
    day           = db.Column(db.Integer)

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

    def __repr__(self):
        return "<Entry {}>".format(self.title)