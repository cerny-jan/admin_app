from admin_app import create_app, db, models
from admin_app.helpers import find_permission
import os
import click
from flask_migrate import Migrate

app = create_app(os.environ.get('FLASK_CONFIG', 'config.DevelopmentConfig'))
migrate = Migrate(app, db)


@app.cli.command()
def mycmd():
    click.echo("Test")


@app.cli.command()
def createsuperuser():
    if models.Permission.query.first():
        try:
            username = click.prompt('username', type=str)
            email = click.prompt('email', type=str)
            user = models.User(username=username, email=email)
            password = click.prompt('password', type=str,
                                    hide_input=True, confirmation_prompt=True)
            user.set_password(password)
            user.permissions.append(find_permission('admin'))
            db.session.add(user)
            db.session.commit()
            click.echo('Superuser created')
        except Exception as e:
            db.session.rollback()
            click.echo(e)
    else:
        click.echo('run the command \'initpermissions\' first')


@app.cli.command()
def initpermissions():
        db.session.add(models.Permission(name='admin'))
        click.echo('admin added')
        db.session.add(models.Permission(name='destinations'))
        click.echo('destinations added')
        db.session.add(models.Permission(name='sources'))
        click.echo('sources added')
        db.session.commit()
        click.echo('Done')


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
