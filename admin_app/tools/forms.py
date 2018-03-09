from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from ..models import GoogleProject


class AddGoogleProjectForm(FlaskForm):
    project_id = StringField('Project ID', validators=[DataRequired()])
    project_name = StringField('Project Name', validators=[DataRequired()])
    submit = SubmitField('Add Google Project')
