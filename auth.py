from db import db
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

def get_user(username : str):
    user = db.session.execute(text("SELECT id, password FROM users WHERE username = :username"), {"username":username}).fetchone()
    return user

def authenticate_user(username : str, password : str) -> bool:
    user = get_user(username)
    if not user:
        return False # username does not exist in database
    return check_password_hash(user.password, password)

def user_exists(username : str) -> bool:
    return get_user(username) != None

def get_hash(password : str):
    return generate_password_hash(password)

def add_user(username : str, password : str):
    password_hash = generate_password_hash(password)
    db.session.execute(text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                       {"username":username, "password":password_hash})
    db.session.commit()
