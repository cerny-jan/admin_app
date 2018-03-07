from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os


db = SQLAlchemy()
migrate = Migrate(db)
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'base.login'


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    from admin_app.base import base
    app.register_blueprint(base)

    return app
