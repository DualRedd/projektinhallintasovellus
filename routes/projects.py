# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, flash, url_for, g
from datetime import datetime
# Internal services
from services.groups_service import get_group_role, get_group_members
from services.projects_service import create_project, get_project_details, get_projects
from services.tasks_service import create_task, create_task_assignment, get_tasks, update_task_state
from utils.permissions import permissions, get_page_permission_response
from utils.tools import remove_line_breaks, get_task_sorting_key
import utils.input_validation as input
# Enums
from enums.enums import role_enum, task_priority_enum, task_state_enum

projects_bp = Blueprint('projects', __name__)

@projects_bp.before_request
def get_project_data():
    # global data for all project pages
    g.sidebar = True
    if "group_id" in request.view_args:
        g.group_id = request.view_args["group_id"]
        g.role = get_group_role(g.group_id, g.user_id)
        g.projects = get_projects(g.group_id)
    if "project_id" in request.view_args:
        g.project_id = request.view_args["project_id"]
        g.project_details = get_project_details(g.project_id)
    if "task_id" in request.view_args:
        g.task_id = request.view_args["task_id"]

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>", methods=["GET"])
def route_base(group_id, project_id):
    return redirect(url_for("projects.route_my_tasks", group_id=g.group_id, project_id=g.project_id))

#----------------#
# CREATION PAGES #
#----------------#
@projects_bp.route("/group/<int:group_id>/projects/new", methods=["GET", "POST"])
@permissions(require_login=True, require_min_role=role_enum.Manager)
def route_new(group_id):
    if request.method == "GET":
        g.current_page = 'projects'
        return render_template("group/new-project.html")
    # else POST-request
    project_name = request.form["name-stored"]
    project_desc = remove_line_breaks(request.form["desc-stored"])
    result = input.validate_create_project_form(project_name, project_desc)
    if result.valid:
        g.project_id = create_project(g.group_id, project_name, project_desc)
        return redirect(url_for("projects.route_my_tasks", group_id=g.group_id, project_id=g.project_id))
    else:
        flash(result.error, "bad-form")
        return redirect(url_for("projects.route_new", group_id=g.group_id))

#-------------#
# TASKS PAGES #
#-------------#
@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/my-tasks", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_my_tasks(group_id, project_id):
    g.current_page = 'project/my-tasks'
    result = get_task_page()
    # filter personal tasks 
    g.tasks = [task for task in g.tasks if any(g.username == member["username"] for member in task["members"])]
    if not result:
        return redirect(url_for("projects.route_my_tasks", group_id=g.group_id, project_id=g.project_id))
    else:
        return render_template("project/my-tasks.html")

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/all-tasks", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_all_tasks(group_id, project_id):
    g.current_page = 'project/all-tasks'
    result = get_task_page()
    if not result:
        return redirect(url_for("projects.route_all_tasks", group_id=g.group_id, project_id=g.project_id))
    else:
        return render_template("project/all-tasks.html")

def get_task_page() -> bool:
    g.sidebar_right = 1
    g.group_members = get_group_members(g.group_id)
    g.can_edit_tasks = g.role.value >= role_enum.Collaborator.value
    sorting = ["deadline", "priority", "state", "title"]

    if request.args.get("search", "0") == "1":
        sorting = request.args.getlist("sort")
        min_date_str = request.args.get("date-min", "")
        max_date_str = request.args.get("date-max", "")
        states = request.args.getlist("state")
        priorities = request.args.getlist("priority")
        members = request.args.getlist("member")
        member_query_type = request.args.get('member-type')
        result = input.validate_project_task_search_form(sorting, min_date_str, max_date_str, states, priorities, members, member_query_type)
        if result.valid:
            min_date = datetime.strptime(min_date_str, '%Y-%m-%d') if min_date_str != "" else None
            max_date = datetime.strptime(max_date_str, '%Y-%m-%d') if max_date_str != "" else None
            if g.current_page == 'project/my-tasks' and member_query_type == 'exact': members.append(g.user_id)
            g.tasks = get_tasks(g.project_id, states, priorities, list(map(int,members)), member_query_type, min_date, max_date)
        else:
            flash(result.error, "bad-search")
            return False
    else:
        g.tasks = get_tasks(g.project_id)
    g.tasks.sort(key=lambda task: get_task_sorting_key(task, sorting))
    return True

#------------#
# STATS PAGE #
#------------#
@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/stats", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_stats(group_id, project_id):
    g.current_page = 'project/stats'
    return render_template("project/stats.html")

#---------------#
# SETTINGS PAGE #
#---------------#
@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/settings", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_settings(group_id, project_id):
    g.current_page = 'project/settings'
    return render_template("project/settings.html")
