from . import tools
from .. import db
from flask import render_template, redirect, url_for, session, request, jsonify
from flask_login import login_required, current_user
from requests_oauthlib import OAuth2Session
from ..models import User, GoogleProject, GoogleDataset
from .forms import AddGoogleProjectForm
from google.oauth2.credentials import Credentials
from google.api_core.exceptions import NotFound

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
refresh_url = token_url


@tools.route('/mapping')
@login_required
def mapping():
    return render_template('blank.html')


@tools.route('/logs')
@login_required
def logs():
    return render_template('blank.html')


@tools.route('/tool')
@login_required
def tool():
    return redirect(url_for('base.portal'))


@tools.route('/tool/callrail')
@login_required
def callrail():
    return render_template('callrail.html')


@tools.route('/tool/google')
@login_required
def google():
    form = AddGoogleProjectForm()
    projects = GoogleProject.query.filter_by(user_id=current_user.id).all()
    datasets = GoogleDataset.query.all()
    return render_template('google.html', form=form, projects = projects, datasets=datasets)


@tools.route('/tool/google/addproject', methods=['POST'])
@login_required
def add_google_project():
    form = AddGoogleProjectForm()
    if form.validate_on_submit():
        # google_project = GoogleProject(project_id=form.project_id.data,
        #             user_id=current_user)
        # db.session.add(google_project)
        # db.session.commit()

        def token_getter():
            return current_user.google_credentials

        token = token_getter()

        google_credentials = Credentials(
            token['access_token'],
            refresh_token=token['refresh_token'],
            token_uri=refresh_url,
            client_id='',
            client_secret='')

        try:
            from google.cloud import bigquery
            bigquery_client = bigquery.Client(credentials=google_credentials, project=form.project_id.data)
            print('------------------------------------')
            datasets = [dataset.dataset_id for dataset in bigquery_client.list_datasets()]
            print(datasets)
            print('------------------------------------')
            google_project = GoogleProject(id=form.project_id.data,
                            user_id=current_user.id)
            db.session.add(google_project)
            for dataset in datasets:
                google_dataset = GoogleDataset(dataset_id=dataset,project_id=form.project_id.data)
                db.session.add(google_dataset)
            db.session.commit()
        except NotFound:
            db.session.rollback()
            return jsonify(status='error', message='Project ID: {} not found'.format(form.project_id.data))
        except Exception as e:
            db.session.rollback()
            message = e.orig if hasattr(e, 'orig') else e.message if hasattr(e, 'message') else e
            return jsonify(status='error', message=str(message))
        return jsonify(status='ok', message='Google Project Added')
    return jsonify(status='formErrors', formErrors=form.errors)


@tools.route('/connect/google')
@login_required
def connect_google():
    google = OAuth2Session(client_id='',
                           scope='https://www.googleapis.com/auth/bigquery',
                           redirect_uri='http://127.0.0.1:5000/oauth2callback')
# When your application receives a refresh token, it is important to store that refresh token for future use. If your application loses the refresh token, it will have to re-prompt the user for consent before obtaining another refresh token. If you need to re-prompt the user for consent, include the approval_prompt parameter in the authorization code request, and set the value to  force.
    authorization_url, state = google.authorization_url(
        authorization_base_url,
        access_type='offline',
        # prompt='select_account',
        approval_prompt='force'
        )

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


@tools.route('/oauth2callback')
@login_required
def oauth2callback():
    google = OAuth2Session(client_id='',
                           redirect_uri='http://127.0.0.1:5000/oauth2callback',
                           state=session['oauth_state'])
    token = google.fetch_token(token_url,
                               client_secret='',
                               authorization_response=request.url)

    def token_saver(token):
        current_user.google_credentials =token
        db.session.commit()

    token_saver(token)

    google_credentials = Credentials(
        token['access_token'],
        refresh_token=token['refresh_token'],
        token_uri=refresh_url,
        client_id='',
        client_secret='')


    from google.cloud import bigquery
    bigquery_client = bigquery.Client(credentials=google_credentials, project='jan-cerny-152320')
    for dataset in bigquery_client.list_datasets():
        print(dataset.dataset_id)
    return redirect(url_for('tools.google'))
