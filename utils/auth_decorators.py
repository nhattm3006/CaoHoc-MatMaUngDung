from flask import session, redirect
from functools import wraps


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "username" not in session:
            return redirect("/login")

        from models.user_model import User
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            session.clear()
            return redirect("/login")

        return func(*args, **kwargs)

    return wrapper



def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if session.get("role") != "admin":
            return redirect("/")

        return func(*args, **kwargs)

    return wrapper