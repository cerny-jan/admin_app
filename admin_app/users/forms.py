from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email
from ..models import User, Permission


class EditUserForm(FlaskForm):
    userid = IntegerField()
    email = EmailField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    edituser = SubmitField('Save Changes')
    permissions = SelectMultipleField('Permissions')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.permissions.choices =  [(permission.name, permission.name) for permission in Permission.query.all()]


class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add User')
    permissions = SelectMultipleField('Permissions')

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.permissions.choices = [(permission.name, permission.name) for permission in Permission.query.all()]

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
