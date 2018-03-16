from . import users
from .. import db
from ..models import User, Role
from .forms import AddUserForm, EditUserForm
from flask import render_template, url_for, redirect, jsonify, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from sqlalchemy.exc import IntegrityError
from ..decorators import requires_role



@users.route('/')
@login_required
@requires_role('admin')
def users_page():
    users = User.query.all()
    add_user_form = AddUserForm()
    edit_user_form = EditUserForm()
    return render_template('users.html', users=users, add_user_form=add_user_form, edit_user_form=edit_user_form)


@users.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')


@users.route('/remove-user/<int:userid>/')
@login_required
@requires_role('admin')
def remove_user(userid):
    try:
        user = User.query.filter_by(id=userid).first_or_404()
        db.session.delete(user)
        db.session.commit()
        flash('User Removed', 'success')
    except Exception as e:
        db.session.rollback()
        message = str(e.orig) if hasattr(
            e, 'orig') else str(e.message) if hasattr(e, 'message') else str(e)
        flash(message, 'danger')
    return redirect(url_for('users.users_page'))



@users.route('/edit-user/', methods=['POST'])
@login_required
@requires_role('admin')
def edit_user():
    form = EditUserForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(id=form.userid.data).first()
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            return jsonify(status='reload', category='success', message='User edited')
        except IntegrityError as e:
            formErrors = {k: str(v) + ' already exists' for k,
                          v in e.params.items() if k in ['username', 'email']}
            db.session.rollback()
            return jsonify(status='formErrors', formErrors=formErrors)
        except Exception as e:
            db.session.rollback()
            return jsonify(status='error', message=str(e.orig))
    return jsonify(data=form.errors)



@users.route('/add-user/', methods=['POST'])
@login_required
@requires_role('admin')
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return jsonify(status='reload', category='success', message='User Created')
    return jsonify(status='formErrors', formErrors=form.errors)
