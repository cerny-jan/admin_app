from flask import Blueprint

destinations = Blueprint('destinations', __name__)

from . import views
