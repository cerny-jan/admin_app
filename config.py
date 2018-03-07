import os


class Config(object):
    SECRET_KEY = os.environ.get('APP_SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    # DEBUG var doesn't work, FLASK_DEBUG env var needs to be set
    pass


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/flask_testdb'
