from . import destinations
from .. import db
from flask import render_template, redirect, url_for, session, request, jsonify, flash
from flask_login import login_required, current_user
from requests_oauthlib import OAuth2Session
from ..models import User, GoogleProject, GoogleDataset
from .forms import AddGoogleProjectForm
from ..helpers import get_google_credentials, token_saver, token_getter
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
import os

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"


@destinations.route('/')
@login_required
def destination():
    return redirect(url_for('base.portal'))


@destinations.route('/google')
@login_required
def google():
    form = AddGoogleProjectForm()
    is_google_connected = True if current_user.google_credentials else False
    projects = GoogleProject.query.filter_by(user_id=current_user.id).all()
    datasets = GoogleDataset.query.join(
        GoogleProject).filter_by(user_id=current_user.id).all()
    return render_template('google.html', form=form, projects=projects, datasets=datasets, is_google_connected=is_google_connected)


@destinations.route('/google/addproject', methods=['POST'])
@login_required
def add_google_project():
    form = AddGoogleProjectForm()
    if form.validate_on_submit():
        token = token_getter()
        google_credentials = get_google_credentials(token)
        try:
            bigquery_client = bigquery.Client(
                credentials=google_credentials, project=form.project_id.data)
            datasets = [
                dataset.dataset_id for dataset in bigquery_client.list_datasets()]
            google_project = GoogleProject(id=form.project_id.data,
                                           user_id=current_user.id)
            db.session.add(google_project)
            for dataset in datasets:
                google_dataset = GoogleDataset(
                    dataset_id=dataset, project_id=form.project_id.data)
                db.session.add(google_dataset)
            db.session.commit()
        except NotFound:
            db.session.rollback()
            return jsonify(status='error', message='Project ID: {} not found'.format(form.project_id.data))
        except Exception as e:
            db.session.rollback()
            message = e.orig if hasattr(
                e, 'orig') else e.message if hasattr(e, 'message') else e
            return jsonify(status='error', message=str(message))
        return jsonify(status='ok', message='Google Project Added')
    return jsonify(status='formErrors', formErrors=form.errors)


@destinations.route('/google/reload-datasets/<projectid>')
@login_required
def reload_google(projectid):
    # check if project exists
    GoogleProject.query.filter_by(id=projectid).first_or_404()
    # find current datasets and remove them
    datasets = GoogleDataset.query.join(GoogleProject).filter_by(
        user_id=current_user.id, id=projectid).all()
    for dataset in datasets:
        db.session.delete(dataset)
    # obtain lastest list of datasets from bigquery
    token = token_getter()
    google_credentials = get_google_credentials(token)
    bigquery_client = bigquery.Client(
        credentials=google_credentials, project=projectid)
    datasets = [
        dataset.dataset_id for dataset in bigquery_client.list_datasets()]
    for dataset in datasets:
        google_dataset = GoogleDataset(
            dataset_id=dataset, project_id=projectid)
        db.session.add(google_dataset)
    db.session.commit()
    flash('Refreshed', 'success')
    return redirect(url_for('destinations.google'))


@destinations.route('/google/connect')
@login_required
def connect_google():
    google = OAuth2Session(client_id=os.environ.get('GOOGLE_CLIENT_ID'),
                           scope='https://www.googleapis.com/auth/bigquery',
                           redirect_uri=url_for('destinations.oauth2callback', _external=True))

    authorization_url, state = google.authorization_url(
        authorization_base_url,
        access_type='offline',
        # prompt='select_account',
        approval_prompt='force'
    )
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


@destinations.route('/google/oauth2callback')
@login_required
def oauth2callback():
    google = OAuth2Session(client_id=os.environ.get('GOOGLE_CLIENT_ID'),
                           redirect_uri=url_for(
                               'destinations.oauth2callback', _external=True),
                           state=session['oauth_state'])
    token = google.fetch_token(token_url,
                               client_secret=os.environ.get(
                                   'GOOGLE_CLIENT_SECRET'),
                               authorization_response=request.url)
    token_saver(token)
    return redirect(url_for('destinations.google'))
