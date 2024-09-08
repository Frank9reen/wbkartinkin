from functools import wraps

from flask import session, url_for, redirect


def login_required(f):  # не используется, можно будет в будущем удалить
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
