# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, flash, g
# Internal services
from services.groups_service import create_group, create_group_invite, create_group_member
from services.groups_service import get_group_details, get_group_invitees, get_group_members, get_group_invite, get_group_role
from services.groups_service import update_group
from services.groups_service import delete_group, delete_group_invite, delete_group_member
from services.auth_service import get_user
from utils.input_validation import validate_group_details_form, validate_group_invite_form, validate_empty_form
from utils.permissions import check_group_permission, get_page_permission_response
from utils.tools import remove_line_breaks
# Enums
from enums.RoleEnum import RoleEnum

groups_bp = Blueprint('groups', __name__)

@groups_bp.before_request
def get_group_id():
    # global data for all group pages
    if "group_id" in request.view_args:
        g.group_id = request.view_args["group_id"]
        g.sidebar = True

#------------#
# MAIN PAGES #
#------------#
@groups_bp.route("/create-group", methods=["GET", "POST"])
def route_create():
    if (res := get_page_permission_response(require_login=True)) is not None: return res
    if request.method == "GET":
        return render_template("group/new-group.html")
    # else POST-request
    group_name = request.form["name-stored"]
    group_desc = remove_line_breaks(request.form["desc-stored"])
    result = validate_group_details_form(group_name, group_desc)
    if result.valid:
        g.group_id = create_group(group_name, group_desc)
        create_group_member(g.group_id, g.user_id, RoleEnum.Owner)
        return redirect(f"/group/{g.group_id}/dashboard")
    else:
        flash(result.error, "bad-form")
        return redirect("/create-group")
        
@groups_bp.route("/join/<int:group_id>", methods=["GET"])
def route_join(group_id):
    if (res := get_page_permission_response(require_login=True)) is not None: return res
    invite = get_group_invite(g.group_id, g.user_id)
    if invite:
        create_group_member(g.group_id, g.user_id, RoleEnum[invite.role])
        delete_group_invite(g.group_id, g.user_id)
        return redirect(f"/group/{g.group_id}/dashboard")
    return redirect("/")

@groups_bp.route("/group/<int:group_id>", methods=["GET"])
def route_base(group_id):
    return redirect(f"/group/{g.group_id}/dashboard")

#----------------#
# DASHBOARD PAGE #
#----------------#
@groups_bp.route("/group/<int:group_id>/dashboard", methods=["GET"])
def route_dashboard(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    g.group_details = get_group_details(g.group_id)
    g.current_page = 'dashboard'
    return render_template("group/dashboard.html")

#---------------#
# PROJECTS PAGE #
#---------------#
@groups_bp.route("/group/<int:group_id>/projects", methods=["GET"])
def route_projects(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    g.current_page = 'projects'
    return render_template("group/projects.html")

@groups_bp.route("/group/<int:group_id>/projects/new", methods=["GET", "POST"])
def route_projects_new(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    if request.method == "GET":
        g.current_page = 'projects'
        return render_template("group/new-project.html")
    # else POST-request
    # TODO: process form

#------------#
# TASKS PAGE #
#------------#
@groups_bp.route("/group/<int:group_id>/tasks", methods=["GET"])
def route_tasks(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    print("here!")
    g.current_page = 'tasks'
    return render_template("error.html")

#--------------#
# MEMBERS PAGE #
#--------------#
@groups_bp.route("/group/<int:group_id>/members", methods=["GET"])
def route_members(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    # Co-owner is minimum required permission level for invites
    g.can_invite = check_group_permission(g.group_id, g.username, RoleEnum.Co_owner)
    g.group_members = get_group_members(g.group_id)
    g.group_invitees = get_group_invitees(g.group_id)
    g.roles = [role for role in RoleEnum if role != RoleEnum.Owner]
    g.current_page = 'members'
    return render_template("group/members.html")

@groups_bp.route("/group/<int:group_id>/members/add", methods=["POST"])
def route_members_add(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    permission = check_group_permission(g.group_id, g.username, RoleEnum.Co_owner)
    if permission:
        username = request.form["username-stored"]
        role_value_str = request.form["role-stored"]
        invitee = get_user(username)
        result = validate_group_invite_form(g.group_id, invitee, role_value_str)
        if result.valid:
            create_group_invite(g.group_id, invitee.id, RoleEnum(int(role_value_str)))
        else:
            flash(result.error, "bad-form")
    return redirect(f"/group/{g.group_id}/members")

#---------------#
# SETTINGS PAGE #
#---------------#
@groups_bp.route("/group/<int:group_id>/settings", methods=["GET"])
def route_settings(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    # Co-owner is minimum required permission level for access to group settings
    g.details_access = check_group_permission(g.group_id, g.username, RoleEnum.Co_owner)
    g.delete_access = check_group_permission(g.group_id, g.username, RoleEnum.Owner)
    g.group_details = get_group_details(g.group_id)
    g.current_page = 'settings'
    return render_template("group/settings.html")

@groups_bp.route("/group/<int:group_id>/settings/details", methods=["POST"])
def route_settings_details(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    # Atleast co-owner role required
    permission = check_group_permission(g.group_id, g.username, RoleEnum.Co_owner)
    if permission:
        group_name = request.form["name-stored"]
        group_desc = remove_line_breaks(request.form["desc-stored"])
        result = validate_group_details_form(group_name, group_desc)
        if result.valid:
            update_group(g.group_id, group_name, group_desc)
        else:
            flash(result.error, "bad-form")
            session["edit-mode-stored"] = True # flag to open edit mode after redirect
    return redirect(f"/group/{g.group_id}/settings")

@groups_bp.route("/group/<int:group_id>/settings/delete-group", methods=["POST"])
def route_settings_delete_group(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    # Only the owner can delete the group
    permission = check_group_permission(g.group_id, g.username, RoleEnum.Owner)
    if permission:
        result = validate_empty_form()
        if result.valid:
            delete_group(g.group_id)
            return redirect("/")
        else:
            flash(result.error, "bad-form2")
    return redirect(f"/group/{g.group_id}/settings")

@groups_bp.route("/group/<int:group_id>/settings/leave-group", methods=["POST"])
def route_settings_leave_group(group_id):
    if (res := get_page_permission_response(require_login=True, require_group_membership=True)) is not None: return res
    # Owner cannot leave own group
    permission = not check_group_permission(g.group_id, g.username, RoleEnum.Owner)
    if permission:
        result = validate_empty_form()
        if result.valid:
            delete_group_member(g.group_id, g.user_id)
            return redirect("/")
        else:
            flash(result.error, "bad-form3")
    return redirect(f"/group/{g.group_id}/settings")
