import datetime

import pandas as pd
from flask import Blueprint
from flask import render_template, request
from flask import session, redirect, url_for
from flask_caching import Cache
from sqlalchemy import func

from .. import db
from ..auth.utils_auth import login_required
from ..models import Payouts, Payouts_bank


rating = Blueprint('rating', __name__)



