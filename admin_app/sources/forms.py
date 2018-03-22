from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import  DataRequired
from ..models import CallRail


class AddCallRailForm(FlaskForm):
    name = StringField('Name')
    account_id = StringField('Account ID', validators=[DataRequired()])
    developer_token = StringField('Account ID', validators=[DataRequired()])
    submit = SubmitField('Add CallRail')
