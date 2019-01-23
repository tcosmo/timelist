import datetime
import enum, markdown

from app import db
from sqlalchemy import Enum

from datetime import datetime

from flask import Markup, request

import app.utils as utils

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
        first_try = "/".join( [ utils.timeMarkToStr(self.day), utils.timeMarkToStr(self.month), utils.timeMarkToStr(self.year) ] )
        if first_try[ 0 ] == '/':
            first_try = first_try[ 1: ]

        if first_try[ 0 ] == '/':
            first_try = first_try[ 1: ]

        if len( first_try ) == 0:
            first_try = "Future"
        return first_try

    def get_form_preset( self, virgin ):
        now = datetime.now()
        form_preset = { 'day': now.day,
                        'month': now.month,
                        'year': now.year,
                        'title': '',
                        'content': '# Notes' }

        if virgin:
            return form_preset

        form_preset['day'] = self.day
        form_preset['month'] = self.month
        form_preset['year'] = self.year
        form_preset['title'] = self.title
        form_preset['content'] = self.content

        return form_preset

    def fill_entry_from_form( self, the_list ):
        self.list_id = the_list.id
        self.day = request.form.get('day')
        self.month = request.form.get('month')
        self.year = request.form.get('year')

        if not self.day.isnumeric() or not self.month.isnumeric() or not self.year.isnumeric():
            return False, 'Fields day/month/year must be numerics.'

        self.title = request.form.get('title')
        raw_content = request.form.get('content')
        self.content = utils.reformate_markdown( raw_content )

        self.last_modified = datetime.utcnow()
        the_list.last_modified = datetime.utcnow()

        return True, ""

    def __repr__(self):
        return "<Entry list_id:{} id:{} name:{}>".format(self.list_id, self.id, self.title)

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