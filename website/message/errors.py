from flask import Blueprint
from flask import render_template

errors = Blueprint('errors', __name__)


@errors.errorhandler(404)
def pagenotfound(error):
    return render_template('static_page/page404.html', title="Page not found"), 404
