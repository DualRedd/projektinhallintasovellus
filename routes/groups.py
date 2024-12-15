# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, flash, url_for, g
from datetime import datetime, timedelta
from calendar import monthrange
# Internal services
from services.groups_service import create_group, create_group_role
from services.groups_service import get_group_details, get_group_members, get_group_role
from services.groups_service import update_group, update_group_role
from services.groups_service import delete_group, delete_group_role
from services.projects_service import get_projects
from services.tasks_service import get_tasks_group
from services.auth_service import get_user
from utils.permissions import permissions
from utils.tools import remove_line_breaks, get_task_sorting_key
import utils.input_validation as input
# Enums
from enums.enums import role_enum

groups_bp = Blueprint('groups', __name__)

@groups_bp.before_request
def get_group_data():
    # global data for all group pages
    if "group_id" in request.view_args:
        g.group_id = request.view_args["group_id"]
        g.sidebar = True
        g.role = get_group_role(g.group_id, g.user_id, is_invitee=False)
        g.projects = get_projects(g.group_id)
        g.group_details = get_group_details(g.group_id)

@groups_bp.route("/group/<int:group_id>", methods=["GET"])
def route_base(group_id):
    return redirect(url_for("groups.route_dashboard", group_id=g.group_id))

#----------------#
# CREATION PAGES #
#----------------#
@groups_bp.route("/create-group", methods=["GET", "POST"])
@permissions(require_login=True)
def route_create():
    if request.method == "GET":
        return render_template("group/new-group.html")
    # else POST-request
    group_name = request.form["name-stored"]
    group_desc = remove_line_breaks(request.form["desc-stored"])
    result = input.validate_group_details_form(group_name, group_desc)
    if result.valid:
        g.group_id = create_group(group_name, group_desc)
        create_group_role(g.group_id, g.user_id, role_enum.Owner, is_invitee=False)
        return redirect(url_for("groups.route_dashboard", group_id=g.group_id))
    else:
        flash(result.error, "bad-form")
        return redirect(url_for("groups.route_create"))
        
@groups_bp.route("/join/<int:group_id>", methods=["GET"])
@permissions(require_login=True)
def route_join(group_id):
    invite_role = get_group_role(g.group_id, g.user_id, is_invitee=True)
    if invite_role:
        update_group_role(g.group_id, g.user_id, invite_role, False)
        return redirect(url_for("groups.route_dashboard", group_id=g.group_id))
    return redirect(url_for("base.route_index"))

#----------------#
# DASHBOARD PAGE #
#----------------#
@groups_bp.route("/group/<int:group_id>/dashboard", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_dashboard(group_id):
    g.current_page = 'dashboard'
    sorting = ['deadline', 'priority', 'state']
    filter = request.args.get('filter', 'non-completed')
    states = ['0', '1'] if filter == 'non-completed' else['0', '1', '2', '3']
    timeframe = request.args.get('time', 'week')
    max_date = datetime.today()
    if timeframe == 'week': max_date += timedelta(days=7)
    elif timeframe == 'month': max_date += timedelta(days=monthrange(max_date.year, max_date.month)[1])
    elif timeframe == 'anytime': max_date  = None
    g.tasks = get_tasks_group(group_id, states, members=[g.user_id], member_query_type='all', max_date=max_date)
    g.tasks.sort(key=lambda task: get_task_sorting_key(task, sorting))
    return render_template("group/dashboard.html")

#---------------#
# PROJECTS PAGE #
#---------------#
@groups_bp.route("/group/<int:group_id>/projects", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_projects(group_id):
    g.can_create_project = g.role.value >= role_enum.Manager.value
    g.active_projects = get_projects(g.group_id, archived=False)
    g.archived_projects = get_projects(g.group_id, archived=True)
    g.current_page = 'projects'
    return render_template("group/projects.html")

#------------#
# TASKS PAGE #
#------------#
@groups_bp.route("/group/<int:group_id>/tasks", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_tasks(group_id):
    g.current_page = 'tasks'
    g.sidebar_right = 1
    g.group_members = get_group_members(g.group_id)
    sorting = ["deadline", "priority", "state", "project", "title"]

    if request.args.get("search", "0") == "1":
        sorting = request.args.getlist("sort")
        min_date_str = request.args.get("date-min", "")
        max_date_str = request.args.get("date-max", "")
        states = request.args.getlist("state")
        priorities = request.args.getlist("priority")
        members = request.args.getlist("member")
        member_query_type = request.args.get('member-type')
        projects = request.args.getlist('project')
        result = input.validate_group_task_search_form(sorting, min_date_str, max_date_str, states, priorities, members, member_query_type, projects)
        if result.valid:
            min_date = datetime.strptime(min_date_str, '%Y-%m-%d') if min_date_str != "" else None
            max_date = datetime.strptime(max_date_str, '%Y-%m-%d') if max_date_str != "" else None
            if g.current_page == 'project/my-tasks' and member_query_type == 'exact': members.append(g.user_id)
            g.tasks = get_tasks_group(g.group_id, states, priorities, list(map(int,members)), member_query_type, min_date, max_date, list(map(int,projects)))
        else:
            flash(result.error, "bad-search")
            return redirect(url_for("groups.route_tasks", group_id=g.group_id))
    else:
        g.tasks = get_tasks_group(group_id, include_archived=False)
    g.tasks.sort(key=lambda task: get_task_sorting_key(task, sorting))
    return render_template("group/all-tasks.html")

#--------------#
# MEMBERS PAGE #
#--------------#
@groups_bp.route("/group/<int:group_id>/members", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_members(group_id):
    g.members = get_group_members(g.group_id)
    g.members.sort(key=lambda member: (member["is_invitee"], -member["role"].value))
    g.current_page = 'members'
    return render_template("group/members.html")

@groups_bp.route("/group/<int:group_id>/members/add", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Co_owner)
def route_members_add(group_id):
    username = request.form["username-stored"]
    role_value_str = request.form["role-stored"]
    invitee = get_user(username)
    result = input.validate_group_invite_form(g.group_id, invitee, role_value_str)
    if result.valid:
        create_group_role(g.group_id, invitee.id, role_enum.get_by_value(int(role_value_str)), True)
    else:
        flash(result.error, "bad-form")
    return redirect(url_for("groups.route_members", group_id=g.group_id))

@groups_bp.route("/group/<int:group_id>/members/remove", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Co_owner)
def route_members_remove(group_id):
    username = request.form["username"]
    user = get_user(username)
    result = input.validate_remove_member_form(user)
    if result.valid:
        delete_group_role(g.group_id, user.id)
    else:
        flash(result.error, "bad-form")
    return redirect(url_for("groups.route_members", group_id=g.group_id))

@groups_bp.route("/group/<int:group_id>/members/alter-role", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Co_owner)
def route_members_alter_role(group_id):
    username = request.form["username"]
    role_value_str = request.form.get("role", None)
    if role_value_str:
        user = get_user(username)
        result = input.validate_alter_role_form(user, role_value_str)
        if result.valid:
            update_group_role(g.group_id, user.id, role_enum.get_by_value(int(role_value_str)))
        else:
            flash(result.error, "bad-form")
    return redirect(url_for("groups.route_members", group_id=g.group_id))

#---------------#
# SETTINGS PAGE #
#---------------#
@groups_bp.route("/group/<int:group_id>/settings", methods=["GET"])
@permissions(require_login=True, require_min_role=role_enum.Observer)
def route_settings(group_id):
    g.group_details = get_group_details(g.group_id)
    g.current_page = 'settings'
    return render_template("group/settings.html")

@groups_bp.route("/group/<int:group_id>/settings/details", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Co_owner)
def route_settings_details(group_id):
    group_name = request.form["name-stored"]
    group_desc = remove_line_breaks(request.form["desc-stored"])
    result = input.validate_group_details_form(group_name, group_desc)
    if result.valid:
        update_group(g.group_id, group_name, group_desc)
    else:
        flash(result.error, "bad-form")
        session["edit-mode-stored"] = True # flag to open edit mode after redirect
    return redirect(url_for("groups.route_settings", group_id=g.group_id))

@groups_bp.route("/group/<int:group_id>/settings/delete-group", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Owner)
def route_settings_delete_group(group_id):
    result = input.validate_empty_form()
    if result.valid:
        delete_group(g.group_id)
        return redirect("/")
    else:
        flash(result.error, "bad-form2")
        return redirect(url_for("groups.route_settings", group_id=g.group_id))

@groups_bp.route("/group/<int:group_id>/settings/leave-group", methods=["POST"])
@permissions(require_login=True, require_min_role=role_enum.Observer, require_max_role=role_enum.Co_owner)
def route_settings_leave_group(group_id):
    result = input.validate_empty_form()
    if result.valid:
        delete_group_role(g.group_id, g.user_id)
        return redirect(url_for("base.route_index"))
    else:
        flash(result.error, "bad-form3")
        return redirect(url_for("groups.route_settings", group_id=g.group_id))
