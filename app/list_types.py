import datetime
import enum, markdown
import bibtexparser
import pyparsing
import os

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

    def getTitle( self ):
        return self.title

    def __repr__(self):
        return "<Entry list_id:{} id:{} name:{}>".format(self.list_id, self.id, self.title)

    def getNbFiles( self ):
        if not os.path.exists('entries/'+self.static_folder):
            utils.myLogger("Static folder {} of ({},{}) not found.".format(self.static_folder,self.list_id,self.id))
            flash('System error, please report.', 'danger')
            return []

        directory_content = os.listdir('entries/'+self.static_folder)

        true_content = []

        for f in directory_content:
            if os.path.isfile(os.path.join('entries', self.static_folder, f)) and f[0]!='.':
               true_content.append({'name':f,'fontAwesome':utils.getFontAwesomeTag(f)})

        true_content.sort( key=lambda x: x['name'] )
        for k in range(len(true_content)):
            true_content[k]['id'] = k
        return len(true_content)

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

    @staticmethod
    def getClarityLevels():
        return ['Not Read', 'For Memory', 'WIP', 'Clear']


    @staticmethod
    def getBadgeForLevel( k ):
        badgeType = ['danger','info','warning','success']
        return '<span class="badge badge-pill badge-{}">{}</span>'.format(badgeType[k],BiblioList.getClarityLevels()[k])

    def getBadge(self):
        k = self.clarity_level
        return self.getBadgeForLevel(k)

    def get_form_preset( self, virgin ):
        now = datetime.now()
        form_preset = { 'day': now.day,
                        'month': now.month,
                        'year': now.year,
                        'content': '# Notes',
                        'bibtex_content': '',
                        'clarity_level': -1 }

        if virgin:
            return form_preset

        form_preset['day'] = self.day
        form_preset['month'] = self.month
        form_preset['year'] = self.year
        form_preset['content'] = self.content
        form_preset['bibtex_content'] = self.bibtex_content
        form_preset['clarity_level'] = self.clarity_level

        return form_preset

    def fill_entry_from_form( self, the_list ):
        self.list_id = the_list.id
        self.day = request.form.get('day')
        self.month = request.form.get('month')
        self.year = request.form.get('year')
        self.clarity_level = int(request.form['clarity_level'])

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

    def getTitle( self ):
        k = 6 if len(self.title.split()) > 7 else 5
        return "<h{}>{}</h{}>".format(k, self.title.replace('{','').replace('}',''),k)

    def getNbFiles( self ):
        if not os.path.exists('entries/'+self.static_folder):
            utils.myLogger("Static folder {} of ({},{}) not found.".format(self.static_folder,self.list_id,self.id))
            flash('System error, please report.', 'danger')
            return []

        directory_content = os.listdir('entries/'+self.static_folder)

        true_content = []

        for f in directory_content:
            if os.path.isfile(os.path.join('entries', self.static_folder, f)) and f[0]!='.':
               true_content.append({'name':f,'fontAwesome':utils.getFontAwesomeTag(f)})

        true_content.sort( key=lambda x: x['name'] )
        for k in range(len(true_content)):
            true_content[k]['id'] = k
        return len(true_content)