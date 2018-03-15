from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired
from ..models import GoogleProject


class AddGoogleProjectForm(FlaskForm):
    google_big_query_id = IntegerField()
    google_email = StringField()
    project_id = StringField('Project ID', validators=[DataRequired()])
    submit = SubmitField('Add Google Project')


class RenameGoogleBigQueryForm(FlaskForm):
    google_big_query_id = IntegerField()
    google_big_query_name = StringField('Tool name', validators=[DataRequired()])
    submit = SubmitField('Save Change')
