from admin_app import create_app
import os
import click
from flask_cli import FlaskCLI

app = create_app(os.environ.get('FLASK_CONFIG','config.DevelopmentConfig'))

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


@app.cli.command()
def test():
    # python -m unittest discover -v
    # TODO COVERAGE
    # coverage run -m unittest discover
    # coverage report -m
    click.echo('Running tests')
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
