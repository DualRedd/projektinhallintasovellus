# standard imports
from flask import session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from secrets import token_hex
# Internal services
from app import db

def get_user(username : str):
    user = db.session.execute(text("SELECT id, username, password, visible FROM users WHERE username = :username"),
                                    {"username":username}).fetchone()
    return user

def user_exists(username : str) -> bool:
    return get_user(username) is not None

def authenticate_user(username : str, password : str) -> bool:
    user = get_user(username)
    if not user or user.visible is False:
        return False # username does not exist
    return check_password_hash(user.password, password)

def create_user(username : str, password : str):
    password_hash = generate_password_hash(password)
    db.session.execute(text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                       {"username":username, "password":password_hash})
    db.session.commit()

def login(username : str):
    session["username"] = username
    session["csrf_token"] = token_hex(16)
