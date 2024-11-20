from os import getenv
from flask import Flask
from flask import request, session, g
from flask_sqlalchemy import SQLAlchemy
from config import config

# app setup
app = Flask(__name__)   
app.secret_key = getenv("SECRET_KEY")

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# routes setup
from routes import blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint)

# global data for rendering pages
@app.context_processor
def inject_config_data():
    return config

# cache control
@app.after_request
def cache_control_headers(response):
    if not request.path.startswith('/static'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# basic request data
@app.before_request
def get_user_data():
    g.username = session.get("username")
    g.user_id = session.get("user_id")
