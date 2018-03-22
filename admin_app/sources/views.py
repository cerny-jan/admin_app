from . import sources
from .. import db
from flask import render_template, redirect, url_for, session, request, jsonify, flash
from flask_login import login_required, current_user
from requests_oauthlib import OAuth2Session
from ..models import User, GoogleProject, GoogleDataset, GoogleBigQuery
from .forms import AddCallRailForm
from ..decorators import requires_permission
import os
import requests


@sources.route('/')
@login_required
@requires_permission('admin','sources')
def source():
    return redirect(url_for('base.portal'))


@sources.route('/callrail/')
@login_required
@requires_permission('admin','sources')
def callrail():
    return render_template('callrail.html')
