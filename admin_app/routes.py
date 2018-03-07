from admin_app import app
from flask import render_template, redirect, request, url_for, flash, jsonify
from admin_app.forms import LoginForm, AddUserForm, EditUserForm
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from admin_app.models import User
from admin_app import db
from sqlalchemy.exc import IntegrityError


@app.route('/portal')
@login_required
def portal():
    return render_template('blank.html')


@app.route('/users', methods=['GET'])
@login_required
def users():
    users = User.query.all()
    add_user_form = AddUserForm()
    edit_user_form = EditUserForm()
    return render_template('users.html', users=users, add_user_form=add_user_form, edit_user_form=edit_user_form)


@app.route('/edituser', methods=['POST'])
@login_required
def edituser():
    form = EditUserForm()
    if form.validate_on_submit():
        if request.form.get('submitButtonName') == 'removeuser':
            try:
                user = User.query.filter_by(id=form.userid.data).first()
                db.session.delete(user)
                db.session.commit()
                return jsonify(status='ok', message='User Removed')
            except Exception as e:
                db.session.rollback()
                return jsonify(status='error',message=str(e.orig))
        elif request.form.get('submitButtonName') == 'edituser':
            try:
                user = User.query.filter_by(id=form.userid.data).first()
                user.username = form.username.data
                user.email = form.email.data
                db.session.commit()
                return jsonify(status='ok', message='User edited')
            except IntegrityError as e:
                formErrors = {k:str(v) + ' already exists' for k,v in e.params.items() if k in ['username','email']}
                db.session.rollback()
                return jsonify(status='formErrors', formErrors=formErrors)
            except Exception as e:
                db.session.rollback()
                return jsonify(status='error', message=str(e.orig))
    return jsonify(data=form.errors)


@app.route('/adduser', methods=['POST'])
@login_required
def adduser():
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return jsonify(status='ok',  message='User Created')
    return jsonify(status='formErrors', formErrors=form.errors)



@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('portal'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('portal')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
