from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, SelectMultipleField
from wtforms.widgets import CheckboxInput
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class NewListForm(FlaskForm):
    list_name = StringField('List name', validators=[DataRequired()])
    list_type = SelectMultipleField('Languages', option_widget=CheckboxInput(), choices = [('cpp', 'C++'), 
      ('py', 'Python')])

    list_can_read = SelectMultipleField('Languages', option_widget=CheckboxInput(), choices = [('cpp', 'C++'), 
      ('py', 'Python')])
    list_can_write = SelectMultipleField('Languages', option_widget=CheckboxInput(), choices = [('cpp', 'C++'), 
      ('py', 'Python')])

    submit = SubmitField('Create New List')

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