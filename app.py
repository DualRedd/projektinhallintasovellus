from os import getenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# app setup
app = Flask(__name__)   
app.secret_key = getenv("SECRET_KEY")

# Debug mode
debug = getenv("DEBUG")
if debug and debug == '1':
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

# Database setup
database_URI = getenv("DATABASE_URL")
if database_URI.startswith("postgres://"): # SQLAlchemy has removed support for the postgres name
    database_URI.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_URI
db = SQLAlchemy(app)

# routes setup
import routes.global_routes
from routes import blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint)
