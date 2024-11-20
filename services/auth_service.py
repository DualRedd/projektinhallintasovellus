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

def create_user(username : str, password : str) -> int:
    password_hash = generate_password_hash(password)
    row_id = db.session.execute(text("INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id"),
                                    {"username":username, "password":password_hash}).fetchone()[0]
    db.session.commit()
    return row_id

def login(username : str, user_id : int):
    session["username"] = username
    session["user_id"] = user_id
    session["csrf_token"] = token_hex(16)
