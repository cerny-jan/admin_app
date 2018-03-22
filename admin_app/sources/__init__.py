from flask import Blueprint

sources = Blueprint('sources', __name__)

from . import views
