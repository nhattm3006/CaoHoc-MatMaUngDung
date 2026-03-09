from flask import Blueprint, render_template, request, redirect, session, url_for
from services.auth_service import authenticate

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = authenticate(username, password)

        if user:

            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))