from flask import Blueprint
from flask import session, request, render_template, redirect
from services.auth_service import authenticate_user, user_exists, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def route_login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        valid = authenticate_user(username, password)
        if not valid:
            return render_template("login.html", error_message="Käyttäjänimi tai salasana on väärä!")
        session["username"] = username
        return redirect("/")
    
@auth_bp.route("/logout")
def route_logout():
    session.pop("username")
    return redirect("/")

@auth_bp.route("/create-user", methods=["GET", "POST"])
def route_create_user():
    if request.method == "GET":
        return render_template("create-user.html")
    elif request.method == "POST":
        username = request.form["username"]
        if user_exists(username):
            return render_template("create-user.html", error_message="Käyttäjänimi on varattu!")
        password = request.form["password"]
        password_check = request.form["password_check"]
        if password != password_check:
            return render_template("create-user.html", error_message="Salasanat eivät täsmää!")
        create_user(username, password)
        session["username"] = username
        return redirect("/")