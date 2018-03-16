from . import destinations
from .. import db
from flask import render_template, redirect, url_for, session, request, jsonify, flash
from flask_login import login_required, current_user
from requests_oauthlib import OAuth2Session
from ..models import User, GoogleProject, GoogleDataset, GoogleBigQuery
from .forms import AddGoogleProjectForm, RenameGoogleBigQueryForm
from ..helpers import get_google_credentials, token_saver
from ..decorators import requires_role
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
import os
import requests
from sqlalchemy.exc import IntegrityError

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
scope = ['https://www.googleapis.com/auth/userinfo.email',
         'https://www.googleapis.com/auth/bigquery',
         'https://www.googleapis.com/auth/logging.write']


@destinations.route('/')
@login_required
@requires_role('admin','destinations')
def destination():
    return redirect(url_for('base.portal'))


@destinations.route('/google/')
@login_required
@requires_role('admin','destinations')
def google():
    form = AddGoogleProjectForm()
    rename_tool_form = RenameGoogleBigQueryForm()
    google_big_queries= GoogleBigQuery.query.filter_by(user_id=current_user.id).outerjoin(GoogleProject).outerjoin(GoogleDataset).all()
    return render_template('google.html', form=form, rename_tool_form=rename_tool_form, google_big_queries=google_big_queries)


@destinations.route('/google/rename-tool/', methods=['POST'])
@login_required
@requires_role('admin','destinations')
def google_rename_tool():
    rename_tool_form = RenameGoogleBigQueryForm()
    if rename_tool_form.validate_on_submit():
        try:
            google_big_query = GoogleBigQuery.query.filter_by(
                user_id=current_user.id, id=rename_tool_form.google_big_query_id.data).first()
            google_big_query.name = rename_tool_form.google_big_query_name.data
            db.session.commit()
            return jsonify(status='reload', category='success', message='Tool Renamed')
        except Exception as e:
            db.session.rollback()
            return jsonify(status='error', message=str(e.orig))
    return jsonify(status='formErrors', formErrors=rename_tool_form.errors)


@destinations.route('/google/add-project/', methods=['POST'])
@login_required
@requires_role('admin','destinations')
def add_google_project():
    form = AddGoogleProjectForm()
    google_big_query =  GoogleBigQuery.query.filter_by(user_id=current_user.id, id=form.google_big_query_id.data).first_or_404()
    if form.validate_on_submit():
        token = google_big_query.google_credentials
        google_credentials = get_google_credentials(token)
        project_id = form.project_id.data.strip()
        try:
            bigquery_client = bigquery.Client(
                credentials=google_credentials, project=project_id)
            datasets = [
                dataset.dataset_id for dataset in bigquery_client.list_datasets()]
            google_project = GoogleProject(id=project_id,
                                           google_big_query_id=form.google_big_query_id.data)
            db.session.add(google_project)
            for dataset in datasets:
                google_dataset = GoogleDataset(
                    dataset_id=dataset, project_id=project_id)
                db.session.add(google_dataset)
            db.session.commit()
        except NotFound:
            db.session.rollback()
            return jsonify(status='error', message='Project ID: {} not found'.format(project_id))
        except Exception as e:
            db.session.rollback()
            message =str(e.orig) if hasattr(
                e, 'orig') else str(e.message) if hasattr(e, 'message') else str(e)
            if 'has not enabled BigQuery' in message:
                message = 'The project {} has not enabled BigQuery.'.format(project_id)
            elif 'Token has been expired or revoked' in message:
                message = 'Token for {} ({}) has been expired or revoked'.format(google_big_query.name, google_big_query.google_email)
                google_big_query.google_credentials=None
                db.session.commit()
                return jsonify(status='reload', category='error', message=message)
            return jsonify(status='error', message=message)
        return jsonify(status='reload', category='success', message='The project {} has been added'.format(project_id))
    return jsonify(status='formErrors', formErrors=form.errors)


@destinations.route('/google/remove-project/<projectid>/')
@login_required
@requires_role('admin','destinations')
def remove_google_project(projectid):
    # check if project exists and the user is owner
    google_big_query = GoogleBigQuery.query.filter_by(user_id=current_user.id).join(GoogleProject).filter_by(id=projectid).first_or_404()
    # remove the project
    try:
        google_project = GoogleProject.query.filter_by(id=projectid).first()
        db.session.delete(google_project)
        db.session.commit()
        flash('The project {} has been removed'.format(projectid), 'success')
    except Exception as e:
        db.session.rollback()
        flash(str(e.orig), 'danger')
    return redirect(url_for('destinations.google'))


@destinations.route('/google/reload-datasets/<projectid>/')
@login_required
@requires_role('admin','destinations')
def reload_google_datasets(projectid):
    # check if project exists and the user is owner
    google_big_query = GoogleBigQuery.query.filter_by(user_id=current_user.id).join(GoogleProject).filter_by(id=projectid).first_or_404()
    # find current datasets
    current_datasets = GoogleDataset.query.join(GoogleProject).filter_by(id=projectid).join(GoogleBigQuery).filter_by(
        user_id=current_user.id).all()
    # get their ids
    current_datasets_ids={current_dataset.dataset_id for current_dataset in current_datasets}
    # obtain lastest list of datasets ids from bigquery
    token = google_big_query.google_credentials
    google_credentials = get_google_credentials(token)
    try:
        bigquery_client = bigquery.Client(
            credentials=google_credentials, project=projectid)
        latest_datasets_ids = {dataset.dataset_id for dataset in bigquery_client.list_datasets()}
        # find diffs
        datasets_ids_to_add = latest_datasets_ids.difference(current_datasets_ids)
        datasets_ids_to_remove = current_datasets_ids.difference(latest_datasets_ids)
        for dataset in datasets_ids_to_add:
            google_dataset = GoogleDataset(
                dataset_id=dataset, project_id=projectid)
            db.session.add(google_dataset)
        db.session.commit()
        datasets_to_remove = GoogleDataset.query.filter(GoogleDataset.dataset_id.in_(datasets_ids_to_remove))
        for dataset in datasets_to_remove:
            db.session.delete(dataset)
        db.session.commit()
        flash('Reloaded', 'success')
    except Exception as e:
        db.session.rollback()
        message =str(e.orig) if hasattr(
            e, 'orig') else str(e.message) if hasattr(e, 'message') else str(e)
        if 'Token has been expired or revoked' in message:
            message = 'Token for {} ({}) has been expired or revoked'.format(google_big_query.name, google_big_query.google_email)
            google_big_query.google_credentials=None
            db.session.commit()
            flash(message, 'danger')
    return redirect(url_for('destinations.google'))



@destinations.route('/google/connect/')
@login_required
@requires_role('admin','destinations')
def connect_google():
    google = OAuth2Session(client_id=os.environ.get('GOOGLE_CLIENT_ID'),
                           scope=scope,
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
@requires_role('admin','destinations')
def oauth2callback():
    try:
        google = OAuth2Session(client_id=os.environ.get('GOOGLE_CLIENT_ID'),
                               redirect_uri=url_for(
                                   'destinations.oauth2callback', _external=True),
                               state=session['oauth_state'])
        token = google.fetch_token(token_url,
                                   client_secret=os.environ.get(
                                       'GOOGLE_CLIENT_SECRET'),
                                   authorization_response=request.url)

        google_session = OAuth2Session(os.environ.get('GOOGLE_CLIENT_ID'), token=token)
        r = google_session.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        google_big_query = GoogleBigQuery.query.filter_by(user_id=current_user.id, google_email=r['email']).first()
        if google_big_query:
            google_big_query.google_credentials = token
            db.session.commit()
        else:
            google_big_query = GoogleBigQuery(name='Google BigQuery',google_email= r['email'],google_credentials=token, user_id=current_user.id)
            db.session.add(google_big_query)
            db.session.commit()
    except IntegrityError as e:
        message = 'This Google account is already in our system' if 'google_email' in str(e.orig) else e.orig
        flash(str(message), 'danger')
    except Exception as e:
        message = request.args.get('error') if request.args.get('error') else e
        flash(str(message), 'danger')
    return redirect(url_for('destinations.google'))


@destinations.route('/google/disconnect/<google_big_query_id>/')
@login_required
@requires_role('admin','destinations')
def disconnect_google(google_big_query_id):
    try:
        google_big_query = GoogleBigQuery.query.filter_by(
            user_id=current_user.id, id=google_big_query_id).first()
        credentials = get_google_credentials(google_big_query.google_credentials)
        google_big_query.google_credentials = None
        db.session.commit()
        requests.post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token': credentials.token},
                      headers={'content-type': 'application/x-www-form-urlencoded'})
        flash('{} disconnected'.format(google_big_query.name), 'warning')
    except Exception as e:
        message = e.orig if hasattr(
            e, 'orig') else e.message if hasattr(e, 'message') else e
        db.session.rollback()
        flash(str(message), 'danger')
    return redirect(url_for('destinations.google'))


@destinations.route('/google/remove/<google_big_query_id>/')
@login_required
@requires_role('admin','destinations')
def remove_google(google_big_query_id):
    try:
        google_big_query = GoogleBigQuery.query.filter_by(
            user_id=current_user.id, id=google_big_query_id).first_or_404()
        google_email = google_big_query.google_email
        # revoke the token (if we still have it in our db)
        if google_big_query.google_credentials:
            credentials = get_google_credentials(google_big_query.google_credentials)
            requests.post('https://accounts.google.com/o/oauth2/revoke',
                                  params={'token': credentials.token},
                                  headers={'content-type': 'application/x-www-form-urlencoded'})
        # delete the tool from db
        db.session.delete(google_big_query)
        db.session.commit()
        flash('{} ({}) has been removed'.format(google_big_query.name,google_email), 'success')
    except Exception as e:
        message = e.orig if hasattr(
            e, 'orig') else e.message if hasattr(e, 'message') else e
        db.session.rollback()
        flash(str(message), 'danger')
    return redirect(url_for('destinations.google'))
