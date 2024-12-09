# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, flash, g
from datetime import datetime
# Internal services
from services.groups_service import get_group_role, get_group_members
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
    if "group_id" in request.view_args and "project_id" in request.view_args:
        g.group_id = request.view_args["group_id"]
        g.project_id = request.view_args["project_id"]
        g.sidebar = 2
        g.role = get_group_role(g.group_id, g.user_id)
    if "task_id" in request.view_args:
        g.task_id = request.view_args["task_id"]

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>", methods=["GET"])
def route_base(group_id, project_id):
    return redirect(f"/group/{g.group_id}/project/{g.project_id}/tasks")

#------------#
# TASKS PAGE #
#------------#
@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/tasks", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_tasks(group_id, project_id):
    g.sidebar_right = 1
    g.group_members = get_group_members(g.group_id)
    g.can_edit_tasks = g.role.value >= role_enum.Collaborator.value
    g.current_page = 'tasks'
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
        print(result.valid)
        if result.valid:
            min_date = datetime.strptime(min_date_str, '%Y-%m-%d') if min_date_str != "" else None
            max_date = datetime.strptime(max_date_str, '%Y-%m-%d') if max_date_str != "" else None
            g.tasks = get_tasks(g.project_id, states, priorities, list(map(int,members)), member_query_type, min_date, max_date)
        else:
            print("ERROR!")
            flash(result.error, "bad-search")
            return redirect(f"/group/{g.group_id}/project/{g.project_id}/tasks")
    else:
        g.tasks = get_tasks(g.project_id)

    g.tasks.sort(key=lambda task: get_task_sorting_key(task, sorting))
    return render_template("project/tasks.html")

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/tasks/new", methods=["GET", "POST"])
@permissions(require_login=True, require_min_role=role_enum.Collaborator)
def route_tasks_new(group_id, project_id):
    if request.method == "GET":
        g.date = datetime.now().strftime('%Y-%m-%d')
        g.time = datetime.now().strftime('%H:%M')
        g.members = get_group_members(g.group_id)
        g.current_page = 'tasks'
        return render_template("project/new-task.html")
    # else POST-request
    task_name = request.form["name-stored"]
    task_desc = remove_line_breaks(request.form["desc-stored"])
    task_priority = request.form["priority-stored"]
    task_date = request.form["date-stored"]
    task_time = request.form["time-stored"]
    task_members = request.form.getlist("members-stored[]")
    result = input.validate_create_task_form(task_name, task_desc, task_priority, task_date, task_time, task_members)
    if result.valid:
        task_priority = task_priority_enum.get_by_value(int(task_priority))
        task_deadline = datetime.strptime(f"{task_date} {task_time}", '%Y-%m-%d %H:%M') if task_date != '' or task_time != '' else None
        task_id = create_task(g.user_id, g.project_id, task_name, task_desc, task_priority, task_deadline)
        for member in task_members:
            create_task_assignment(task_id, int(member))
        return redirect(f"/group/{g.group_id}/project/{g.project_id}/tasks")
    else:
        flash(result.error, "bad-form")
        return redirect(f"/group/{g.group_id}/project/{g.project_id}/tasks/new")

@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/task/<int:task_id>/edit-state", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_tasks_edit_state(group_id, project_id, task_id):
    if g.role == role_enum.Observer: # observers can only change state of tasks they are assigned to
        if (res := get_page_permission_response(require_task_membership=True)) is not None: return res
    state_str = request.form["state"]
    result = input.validate_task_state_form(state_str)
    if result.valid:
        update_task_state(task_id, task_state_enum.get_by_value(int(state_str)))
    return redirect(request.referrer or f"/group/{g.group_id}/project/{g.project_id}/tasks")

#------------#
# STATS PAGE #
#------------#
@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/stats", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_stats(group_id, project_id):
    g.current_page = 'stats'
    return render_template("project/stats.html")

#---------------#
# SETTINGS PAGE #
#---------------#
@projects_bp.route("/group/<int:group_id>/project/<int:project_id>/settings", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_settings(group_id, project_id):
    g.current_page = 'settings'
    return render_template("project/settings.html")