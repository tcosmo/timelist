import datetime
import enum, markdown
import bibtexparser
import pyparsing

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
        to_join = []
        if self.day != 0:
            to_join.append(utils.timeMarkToStr(self.day))
        if self.month != 0:
            to_join.append(utils.timeMarkToStr(self.month))
        if self.year != 0:
            to_join.append(utils.timeMarkToStr(self.year))

        return "Future" if len(to_join) == 0 else "/".join(to_join)

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

    bibtex_content     = db.Column(db.String, index=True)

    clarity_level      = db.Column(db.Integer)

    def __repr__(self):
        return "<Entry {}>".format(self.title)

    def getFormattedDate( self ):
        to_join = []
        if self.day != 0:
            to_join.append(utils.timeMarkToStr(self.day))
        if self.month != 0:
            to_join.append(utils.timeMarkToStr(self.month))
        if self.year != 0:
            to_join.append(utils.timeMarkToStr(self.year))

        return "Future" if len(to_join) == 0 else "/".join(to_join)

    def getFormattedContent( self ):
        return Markup(markdown.markdown(self.content))

    def parseBibtex(self):
        try:
            toReturn = bibtexparser.loads(self.bibtex_content).entries
            if len(toReturn) == 0:
                return {'ok': False, 'entry': {}}
            return {'ok': True, 'entry': toReturn[0]}
        except pyparsing.ParseException:
            return {'ok': False, 'entry': {}}

    def getBadge(self):
        if self.clarity_level == 0:
            return '<span class="badge badge-pill badge-danger">Not Read</span>'
        if self.clarity_level == 1:
            return '<span class="badge badge-pill badge-info">For Memory</span>'
        if self.clarity_level == 2:
            return '<span class="badge badge-pill badge-warning">WIP</span>'

        return '<span class="badge badge-pill badge-success">Ok</span>'

    def get_form_preset( self, virgin ):
        now = datetime.now()
        form_preset = { 'day': now.day,
                        'month': now.month,
                        'year': now.year,
                        'content': '# Notes',
                        'bibtex_content': '' }

        if virgin:
            return form_preset

        form_preset['day'] = self.day
        form_preset['month'] = self.month
        form_preset['year'] = self.year
        form_preset['content'] = self.content
        form_preset['bibtex_content'] = self.bibtex_content

        return form_preset

    def fill_entry_from_form( self, the_list ):
        self.list_id = the_list.id
        self.day = request.form.get('day')
        self.month = request.form.get('month')
        self.year = request.form.get('year')

        if not self.day.isnumeric() or not self.month.isnumeric() or not self.year.isnumeric():
            return False, 'Fields day/month/year must be numerics.'

        raw_content = request.form.get('content')
        self.content = utils.reformate_markdown( raw_content )
        self.bibtex_content = request.form.get('bibtex_content')
        returnDict = self.parseBibtex()

        if not returnDict['ok']:
            return False, 'Your bibtex did not parse well, it has been reset to its previous state.'

        self.title = returnDict['entry']['title']

        self.last_modified = datetime.utcnow()
        the_list.last_modified = datetime.utcnow()

        return True, ""