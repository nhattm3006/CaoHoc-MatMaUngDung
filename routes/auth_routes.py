from flask import Blueprint, render_template, request, redirect, url_for, make_response
from services.auth_service import authenticate
from utils.jwt_utils import generate_access_token, generate_refresh_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = authenticate(username, password)

        if user:
            # Generate Tokens
            access_token = generate_access_token(user["id"], user["username"], user["role"])
            refresh_token = generate_refresh_token(user["id"], user["username"], user["role"])

            # Create response and set cookies
            response = make_response(redirect("/"))
            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=3600  # 1 hour
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=7 * 24 * 3600  # 7 days
            )
            return response

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    response = make_response(redirect(url_for("auth.login")))
    response.set_cookie("access_token", "", expires=0)
    response.set_cookie("refresh_token", "", expires=0)
    return response