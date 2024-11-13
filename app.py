from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute(text("SELECT name FROM groups"))
    groups = result.fetchall()
    return render_template("index.html", count=len(groups), groups=groups)

@app.route("/create-group")
def create_group():
    return render_template("create-group-form.html")

@app.route("/create-group/result", methods=["POST"])
def create_group_result():
    db.session.execute(text("INSERT INTO groups (name) VALUES (:name)"), {"name":request.form["name"]})
    db.session.commit()
    return redirect("/")


