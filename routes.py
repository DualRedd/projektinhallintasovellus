from app import app
from flask import session, request, render_template, redirect
from sqlalchemy.sql import text
from db import db

import auth, groups

@app.route("/")
def index():
    username = session.get("username")
    if not username:
        return render_template("index-no-account.html")
    mygroups = groups.get_groups(username)
    return render_template("index.html", groups=mygroups)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        valid = auth.authenticate_user(username, password)
        if not valid:
            return render_template("login.html", error_message="Käyttäjänimi tai salasana on väärä!")
        session["username"] = username
        return redirect("/")
    
@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/")

@app.route("/create-user", methods=["GET", "POST"])
def create_user():
    if request.method == "GET":
        return render_template("create-user.html")
    elif request.method == "POST":
        username = request.form["username"]
        if auth.user_exists(username):
            return render_template("create-user.html", error_message="Käyttäjänimi on varattu!")
        password = request.form["password"]
        password_check = request.form["password_check"]
        if password != password_check:
            return render_template("create-user.html", error_message="Salasanat eivät täsmää!")
        auth.create_user(username, password)
        session["username"] = username
        return redirect("/")


@app.route("/create-group")
def create_group():
    return render_template("create-group-form.html")

@app.route("/create-group/result", methods=["POST"])
def create_group_result():
    username = session.get("username")
    if not username:
        return redirect("/") # not logged in
    group_name = request.form["name"]
    groups.create_group(username, group_name)
    return redirect("/")
