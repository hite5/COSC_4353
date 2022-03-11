from flask import current_app, url_for, render_template
from flask_login import UserMixin, current_user
from . import db
from functools import wraps


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    # type = db.Column(db.String(100))

# def login_required_test(role="ANY"):
#     def wrapper(fn):
#         @wraps(fn)
#         def decorated_view(*args, **kwargs):
#             if not current_user.is_authenticated:
#                return render_template('NoPermission.html')
#             type = current_user.type
#             if ( (type != role) and (role != "ANY")):
#                 return render_template('NoPermission.html')
#             return fn(*args, **kwargs)
#         return decorated_view
#     return wrapper