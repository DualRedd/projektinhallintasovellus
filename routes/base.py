# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, g
# Internal services
from services.groups_service import get_groups, get_invites
from utils.permissions import get_page_permission_response

base_bp = Blueprint('index', __name__)

@base_bp.route("/")
def route_index():
    if (res := get_page_permission_response(require_login=True)) is not None: return res
    g.groups = get_groups(g.username)
    g.invites = get_invites(g.username)
    return render_template("index.html")
