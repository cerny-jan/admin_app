from google.oauth2.credentials import Credentials
from . import db
from flask_login import current_user
from admin_app.models import GoogleBigQuery, Role
import os


def get_google_credentials(token):

    return Credentials(
        token['access_token'],
        refresh_token=token['refresh_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET')
    )


def token_saver(token, google_email):
    google_big_query = GoogleBigQuery.query.filter_by(
        user_id=current_user.id, google_email=None).first()
    if not google_big_query:
        google_big_query = GoogleBigQuery.query.filter_by(
            user_id=current_user.id, google_email=google_email).first()
    google_big_query.google_email = google_email
    google_big_query.google_credentials = token
    db.session.commit()


def find_role(name):
    role = Role.query.filter_by(name = name).first()
    return role
