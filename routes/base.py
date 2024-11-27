# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, g
# Internal services
from services.groups_service import get_groups, get_invites
from utils.permissions import get_page_permission_response
from utils.permissions import permissions

base_bp = Blueprint('index', __name__)

@base_bp.route("/")
@permissions(require_login=True)
def route_index():
    g.groups = get_groups(g.username)
    g.invites = get_invites(g.username)
    return render_template("index.html")
