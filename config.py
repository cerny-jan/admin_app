import os


class Config(object):
    SECRET_KEY = os.environ.get('APP_SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
