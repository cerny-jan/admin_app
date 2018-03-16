from functools import wraps
from flask_login import current_user
from flask import abort

def requires_role(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_role(*roles):
                     abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper
