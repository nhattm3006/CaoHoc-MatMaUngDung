from flask import Blueprint, render_template, session
from utils.auth_decorators import login_required


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
@login_required
def home():

    username = session["username"]
    role = session.get("role")

    return render_template("home.html", username=username, role=role)