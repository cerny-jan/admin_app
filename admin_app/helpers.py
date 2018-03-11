from google.oauth2.credentials import Credentials
from . import db
from flask_login import current_user
import os


def get_google_credentials(token):

    return Credentials(
        token['access_token'],
        refresh_token=token['refresh_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET')
    )


def token_saver(token):
    current_user.google_credentials = token
    db.session.commit()


def token_getter():
    return current_user.google_credentials
