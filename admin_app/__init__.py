from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'base.login'


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.url_map.strict_slashes = False
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    from admin_app.base import base
    app.register_blueprint(base)
    from admin_app.tools import tools
    app.register_blueprint(tools)

    return app
