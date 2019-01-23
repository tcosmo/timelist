from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, SelectMultipleField, \
FormField, FieldList
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.widgets import CheckboxInput
from app.models import User, List, ListType

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class HiddenTagForm(FlaskForm):
    pass

class CheckBoxForm(FlaskForm):
    name = CheckboxInput()

class NewListForm(object):

    def __init__(self):
        self.form = CheckBoxForm()

        self.list_name = ""

        self.all_read = False
        self.all_write = False
        
        self.default_order_desc = True

        self.list_type = [ { 'name': t.name, 'is_current_user': False, 'description': t.description, 'checked': True if t.name == 'DefaultList' else False } for t in ListType.query.all() ]
        self.list_users  = sorted([ {'name': u.username, 'is_current_user': False, 'readChecked': False, 'readEnabled': True, 'writeChecked': False, 'writeEnabled': True } for u in User.query.all() ], key=lambda x: x['name'])

    def hidden_tag(self):
        return self.form.hidden_tag()

    def set_current_user( self, username ):
        for x in self.list_users:
            if x['name'] == username:
                x['is_current_user'] = username
                x['writeChecked'] = True
                x['writeEnabled'] = False
                x['readChecked'] = True
                x['readEnabled'] = False
                break

    def set_public(self):
        self.all_read = True
        self.all_write = True

        for x in self.list_users:
            x['readChecked'] = True
       
        for x in self.list_users:
            x['writeChecked'] = True


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()], render_kw={"placeholder": "Optional"} )
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
