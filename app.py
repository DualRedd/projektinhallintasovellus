from os import getenv
from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy

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


@app.after_request
def cache_control_headers(response):
    if not request.path.startswith('/static'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response
