from . import tools

from flask import render_template, redirect, url_for
from flask_login import login_required


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
    return render_template('google.html')
