# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect
# Internal services
from services.groups_service import get_groups

base_bp = Blueprint('index', __name__)

@base_bp.route("/")
def route_index():
    username = session.get("username")
    if not username:
        return render_template("index-no-account.html")
    mygroups = get_groups(username)
    return render_template("index.html", groups=mygroups)
