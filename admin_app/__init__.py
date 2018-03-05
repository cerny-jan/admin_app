from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import click
from flask_cli import FlaskCLI


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
csrf = CSRFProtect(app)
FlaskCLI(app)

from admin_app import routes, models


@app.cli.command()
def mycmd():
    click.echo("Test")


@app.cli.command()
def createsuperuser():
    try:
        username = click.prompt('username', type=str)
        email = click.prompt('email', type=str)
        user = models.User(username=username, email=email)
        password = click.prompt('password', type=str,
                                hide_input=True,  confirmation_prompt=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo('Superuser created')
    except Exception as e:
        db.session.rollback()
        click.echo(e)
