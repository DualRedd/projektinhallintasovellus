from flask import Blueprint
from flask import session, request, render_template, redirect
from services.auth_service import authenticate_user, create_user
from utils.input_validation import validate_create_user_form, validate_login_form
from config import MAX_INPUT_SIZES

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def route_login():
    username = session.get("username")
    if username:
        return redirect("/") # already logged in
    
    if request.method == "GET":
        return render_template("login.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES)
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        result = validate_login_form(username, password)
        if not result.valid:
            return render_template("login.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES, error_message=result.error)
        valid = authenticate_user(username, password)
        if not valid:
            return render_template("login.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES, error_message="Käyttäjänimi tai salasana on väärä!")
        session["username"] = username
        return redirect("/")

@auth_bp.route("/create-user", methods=["GET", "POST"])
def route_create_user():
    username = session.get("username")
    if username:
        return redirect("/") # already logged in
    
    if request.method == "GET":
        return render_template("create-user.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES)
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_check = request.form["password_check"]
        result = validate_create_user_form(username, password, password_check)
        if not result.valid:
            return render_template("create-user.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES, error_message=result.error)
        create_user(username, password)
        session["username"] = username
        return redirect("/")
    
@auth_bp.route("/logout")
def route_logout():
    session.pop("username")
    return redirect("/")