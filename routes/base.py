# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, g
# Internal services
from services.groups_service import get_groups
from utils.permissions import permissions

base_bp = Blueprint('base', __name__)

@base_bp.route("/")
@permissions(require_login=True)
def route_index():
    g.groups = get_groups(g.user_id, is_invitee=False)
    g.invites = get_groups(g.user_id, is_invitee=True)
    return render_template("index.html")
