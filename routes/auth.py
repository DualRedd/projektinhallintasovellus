# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, flash, g
# Internal services
from services.auth_service import create_user, login
from services.groups_service import get_user
from utils.input_validation import validate_create_user_form, validate_login_form

auth_bp = Blueprint('auth', __name__)

@auth_bp.after_request
def remove_stored_forms(response):
    if not (300 <= response.status_code < 400):
        # if this is not a redirect, remove stored form values
        session.pop("form-username", None)
    return response

@auth_bp.route("/login", methods=["GET", "POST"])
def route_login():
    if g.username: return redirect("/") # check if already logged in
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        result = validate_login_form(username, password)
        if not result.valid:
            flash(result.error, "bad-form")
            session["form-username"] = username
            return redirect("/login")
        login(username, get_user(username).id)
        return redirect("/")

@auth_bp.route("/create-user", methods=["GET", "POST"])
def route_create_user():
    if g.username: return redirect("/") # check if already logged in
    if request.method == "GET":
        return render_template("create-user.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_check = request.form["password_check"]
        result = validate_create_user_form(username, password, password_check)
        if not result.valid:
            flash(result.error, "bad-form")
            session["form-username"] = username
            return redirect("/create-user")
        user_id = create_user(username, password)
        login(username, user_id)
        return redirect("/")

@auth_bp.route("/logout")
def route_logout():
    if "username" in session: session.pop("username")
    if "user_id" in session: session.pop("user_id")
    return redirect("/login")
