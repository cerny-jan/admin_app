from admin_app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    google_big_queries = db.relationship(
        'GoogleBigQuery', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class GoogleBigQuery(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    google_email = db.Column(db.String(120), index=True, unique=True)
    google_credentials = db.Column(db.PickleType)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    google_projects = db.relationship(
        'GoogleProject', backref='user', lazy=True)


class GoogleProject(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
    google_big_query_id = db.Column(
        db.Integer, db.ForeignKey('google_big_query.id'))
    datasets = db.relationship(
        'GoogleDataset', backref='google_project', lazy=True)


class GoogleDataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.String(64), index=True)
    project_id = db.Column(db.String(64), db.ForeignKey('google_project.id'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
