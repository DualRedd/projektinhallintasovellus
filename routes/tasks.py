# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, flash, url_for, g
from datetime import datetime
# Internal services
from services.groups_service import get_group_role, get_group_members
from services.projects_service import get_projects, get_project_details
from services.tasks_service import create_task, set_task_assignments, update_task_state, update_task, delete_task
from utils.permissions import permissions, get_page_permission_response
from utils.tools import remove_line_breaks, parse_form_datetime
import utils.input_validation as input
# Enums
from enums.enums import role_enum, task_priority_enum, task_state_enum

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.before_request
def get_task_data():
    # global data for all task pages
    g.sidebar = 1
    if "group_id" in request.view_args:
        g.group_id = request.view_args["group_id"]
        g.role = get_group_role(g.group_id, g.user_id, is_invitee=False)
        if g.role: g.setting_access = g.role.value >= role_enum.Manager.value
        g.projects = get_projects(g.group_id)
    if "project_id" in request.view_args:
        g.project_id = request.view_args["project_id"]
        g.project_details = get_project_details(g.project_id)
    if "task_id" in request.view_args:
        g.task_id = request.view_args["task_id"]

@tasks_bp.route("/group/<int:group_id>/project/<int:project_id>/tasks/new", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Collaborator)
def route_new(group_id, project_id):
    task_name = request.form["title-stored"]
    task_desc = remove_line_breaks(request.form["desc-stored"])
    task_priority = request.form["priority-stored"]
    task_date = request.form["date-stored"]
    task_time = request.form["time-stored"]
    task_members = request.form.getlist("members-stored[]")
    result = input.validate_task_data_form(task_name, task_desc, task_priority, task_date, task_time, task_members)
    if result.valid:
        task_priority = task_priority_enum.get_by_value(int(task_priority))
        task_deadline = parse_form_datetime(task_date, task_time)
        task_id = create_task(g.project_id, task_name, task_desc, task_priority, task_deadline)
        set_task_assignments(task_id, list(map(int,task_members)))
    else:
        flash(result.error, "bad-form")
        session["bad-form-stored"] = -1 # flag to open correct form after redirect
    return redirect(request.referrer)

@tasks_bp.route("/group/<int:group_id>/project/<int:project_id>/task/<int:task_id>/edit", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Collaborator)
def route_edit(group_id, project_id, task_id):
    task_name = request.form["title-stored"]
    task_desc = remove_line_breaks(request.form["desc-stored"])
    task_priority = request.form["priority-stored"]
    task_date = request.form["date-stored"]
    task_time = request.form["time-stored"]
    task_members = request.form.getlist("members-stored[]")
    result = input.validate_task_data_form(task_name, task_desc, task_priority, task_date, task_time, task_members)
    if result.valid:
        task_priority = task_priority_enum.get_by_value(int(task_priority))
        task_deadline = parse_form_datetime(task_date, task_time)
        update_task(g.task_id, task_name, task_desc, task_priority, task_deadline)
        set_task_assignments(task_id, list(map(int,task_members)))
    else:
        flash(result.error, "bad-form")
        session["bad-form-stored"] = g.task_id # flag to open correct form after redirect
    return redirect(request.referrer or url_for("projects.route_my_tasks", group_id=g.group_id, project_id=g.project_id))

@tasks_bp.route("/group/<int:group_id>/project/<int:project_id>/task/<int:task_id>/edit-state", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_edit_state(group_id, project_id, task_id):
    if g.role == role_enum.Observer: # observers can only change state of tasks they are assigned to
        if (res := get_page_permission_response(require_task_membership=True)) is not None: return res
    state_str = request.form.get("state", None)
    if state_str is not None:
        result = input.validate_task_state_form(state_str)
        if result.valid:
            update_task_state(g.task_id, task_state_enum.get_by_value(int(state_str)))
    return redirect(request.referrer or url_for("projects.route_my_tasks", group_id=g.group_id, project_id=g.project_id))

@tasks_bp.route("/group/<int:group_id>/project/<int:project_id>/task/<int:task_id>/delete", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Collaborator)
def route_delete(group_id, project_id, task_id):
    result = input.validate_task_delete_form()
    if result.valid:
        delete_task(g.task_id)
    else:
        flash(result.error, "bad-form-2")
        session["bad-form-stored"] = g.task_id # flag to open correct form after redirect
    return redirect(request.referrer or url_for("projects.route_my_tasks", group_id=g.group_id, project_id=g.project_id))
