from functools import wraps
from flask_login import current_user
from flask import abort

def requires_permission(*permissions):
    "there is a OR rule between permissions"
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_permission(*permissions):
                     abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper
