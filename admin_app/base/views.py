from . import base
from .. import db
from ..models import User
from .forms import LoginForm
from flask import render_template, url_for, redirect, jsonify, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from sqlalchemy.exc import IntegrityError


@base.route('/portal')
@login_required
def portal():
    return render_template('blank.html')


@base.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base.portal'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('base.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('base.portal')
        return redirect(next_page)
    return render_template('login.html', form=form)


@base.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base.login'))
