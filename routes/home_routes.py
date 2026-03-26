from flask import Blueprint, render_template, g
from utils.auth_decorators import login_required


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
@login_required
def home():

    username = g.user["username"]
    role = g.user.get("role")

    return render_template("home.html", username=username, role=role)