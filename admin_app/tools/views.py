from . import tools
from .. import db
from flask import render_template, redirect, url_for, session, request, jsonify, flash
from flask_login import login_required, current_user
from requests_oauthlib import OAuth2Session
from ..models import User, GoogleProject, GoogleDataset
from ..helpers import get_google_credentials, token_saver, token_getter
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
import os

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"


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
