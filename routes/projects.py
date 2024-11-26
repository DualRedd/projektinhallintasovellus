# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, flash, g
# Internal services
from services.groups_service import get_group_role
from utils.permissions import permissions
from utils.tools import remove_line_breaks
# Enums
from enums.RoleEnum import RoleEnum

projects_bp = Blueprint('projects', __name__)

@projects_bp.before_request
def get_project_data():
    # global data for all project pages
    if "group_id" in request.view_args:
        g.group_id = request.view_args["group_id"]
        g.project_id = request.view_args["project_id"]
        g.sidebar = 2
        g.role = get_group_role(g.group_id, g.username)

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>", methods=["GET"])
def route_base(group_id, project_id):
    return redirect(f"/group/{g.group_id}/project/{g.project_id}/tasks")

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/tasks", methods=["GET"])
@permissions(require_login=True, require_min_role=RoleEnum.Observer)
def route_tasks(group_id, project_id):
    g.current_page = 'tasks'
    return render_template("project/tasks.html")

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/stats", methods=["GET"])
@permissions(require_login=True, require_min_role=RoleEnum.Observer)
def route_stats(group_id, project_id):
    g.current_page = 'stats'
    return render_template("project/stats.html")

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/settings", methods=["GET"])
@permissions(require_login=True, require_min_role=RoleEnum.Observer)
def route_settings(group_id, project_id):
    g.current_page = 'settings'
    return render_template("project/settings.html")