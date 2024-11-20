# standard imports
from flask import Blueprint
from flask import session, render_template, redirect, g
# Internal services
from services.groups_service import get_groups, get_invites

base_bp = Blueprint('index', __name__)

@base_bp.route("/")
def route_index():
    username = session.get("username")
    if not username:
        return redirect("/login")
    g.groups = get_groups(username)
    g.invites = get_invites(username)
    return render_template("index.html")
