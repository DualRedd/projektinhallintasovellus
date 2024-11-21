# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, g
# Internal services
from services.groups_service import create_group, create_group_invite, create_group_member
from services.groups_service import get_group_details, get_group_invitees, get_group_members, get_group_invite
from services.groups_service import update_group
from services.groups_service import delete_group_invite
from services.auth_service import get_user
from utils.input_validation import validate_group_details_form, validate_group_invite_form
from utils.permissions import check_group_permission, get_page_permission_response
from utils.tools import remove_line_breaks
# Enums
from enums.RoleEnum import RoleEnum

groups_bp = Blueprint('groups', __name__)

@groups_bp.before_request
def get_group_id():
    if "group_id" in request.view_args:
        g.group_id = request.view_args["group_id"]
        g.sidebar = True


@groups_bp.route("/create-group", methods=["GET", "POST"])
def route_create_group():
    if (res := get_page_permission_response(require_login=True)) is not None: return res
    if request.method == "GET":
        return render_template("group/create-group-form.html")
    elif request.method == "POST":
        group_name = request.form["name"]
        group_desc = remove_line_breaks(request.form["desc"])
        result = validate_group_details_form(group_name, group_desc)
        if not result.valid:
            g.error_message = result.error
            return render_template("group/create-group-form.html")
        g.group_id = create_group(group_name, group_desc)
        create_group_member(g.group_id, g.user_id, RoleEnum.Owner)
        return redirect(f"/group/{g.group_id}/dashboard")

@groups_bp.route("/join/<int:group_id>")
def route_group_join(group_id):
    if (res := get_page_permission_response(require_login=True)) is not None: return res
    invite = get_group_invite(g.group_id, g.user_id)
    if invite:
        create_group_member(g.group_id, g.user_id, RoleEnum[invite.role])
        delete_group_invite(g.group_id, g.user_id)
        return redirect(f"/group/{g.group_id}/dashboard")
    return redirect("/")


@groups_bp.route("/group/<int:group_id>")
def route_group_page_base(group_id):
    return redirect(f"/group/{g.group_id}/dashboard")

@groups_bp.route("/group/<int:group_id>/dashboard", methods=["GET"])
def route_group_page_dashboard(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    g.group_details = get_group_details(g.group_id)
    g.current_page = 'dashboard'
    return render_template("group/group-dashboard.html")

@groups_bp.route("/group/<int:group_id>/projects", methods=["GET"])
def route_group_page_projects(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    g.current_page = 'projects'
    return render_template("error.html")

@groups_bp.route("/group/<int:group_id>/tasks", methods=["GET"])
def route_group_page_tasks(group_id):
    if res := get_page_permission_response(require_login=True, require_group_membership=True) is not None: return res
    g.current_page = 'tasks'
    return render_template("error.html")

@groups_bp.route("/group/<int:group_id>/members", methods=["GET", "POST"])
def route_group_page_members(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res

    # Co-owner is minimum required permission level for invites
    g.can_invite = check_group_permission(g.group_id, g.username, RoleEnum.Co_owner)
    if request.method == "POST" and g.can_invite: # invite form posted
        invitee = get_user(request.form["username"])
        role_value_str = request.form["role"]
        result = validate_group_invite_form(g.group_id, invitee, role_value_str)
        if result.valid:
            create_group_invite(g.group_id, invitee.id, RoleEnum(int(role_value_str)))
        else:
            g.error_message = result.error

    g.group_members = get_group_members(g.group_id)
    g.group_invitees = get_group_invitees(g.group_id)
    g.roles = [role for role in RoleEnum if role != RoleEnum.Owner]
    g.current_page = 'members'
    return render_template("group/group-members.html")

@groups_bp.route("/group/<int:group_id>/settings", methods=["GET", "POST"])
def route_group_page_settings(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res

    # Co-owner is minimum required permission level group settings
    settings_access = check_group_permission(g.group_id, g.username, RoleEnum.Co_owner)
    if request.method == "POST" and settings_access: # group data change form
        group_name = request.form["name"]
        group_desc = remove_line_breaks(request.form["desc"])
        result = validate_group_details_form(group_name, group_desc)
        if result.valid:
            update_group(g.group_id, group_name, group_desc)
        else:
            g.error_message = result.error

    g.group_details = get_group_details(g.group_id)
    g.current_page = 'settings'
    return render_template("group/group-settings.html")
