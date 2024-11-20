# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect, g
# Internal services
from services.groups_service import create_group, create_group_invite, create_group_member
from services.groups_service import get_group_details, get_group_invitees, get_group_members, get_group_role, get_group_invite
from services.groups_service import delete_group_invite
from services.auth_service import get_user
from utils.input_validation import validate_create_group_form, validate_group_invite_form
from utils.permissions import check_group_permission
# Enums
from enums.RoleEnum import RoleEnum

groups_bp = Blueprint('groups', __name__)

@groups_bp.route("/create-group", methods=["GET", "POST"])
def route_create_group():
    username = session.get("username")
    if not username:
        return redirect("/login") # not logged in

    if request.method == "GET":
        return render_template("create-group-form.html")
    elif request.method == "POST":
        group_name = request.form["name"]
        group_desc = request.form["desc"]
        result = validate_create_group_form(group_name, group_desc)
        if not result.valid:
            g.error_message = result.error
            return render_template("create-group-form.html")
        group_id = create_group(username, group_name, group_desc)
        return redirect(f"/group/{group_id}")

@groups_bp.route("/group/<int:group_id>", methods=["GET", "POST"])
def route_group_page(group_id):
    username = session.get("username")
    if not username:
        return redirect("/login") # not logged in
    is_member = get_group_role(group_id, username) is not None
    if not is_member:
        g.error_message = "You do not have the right to view this page!"
        g.error_code
        return render_template("error.html")

    # Co-owner is minimum required permission level for invites
    g.can_invite = check_group_permission(group_id, username, RoleEnum.Co_owner)
    if request.method == "POST" and g.can_invite: # invite form posted
        invitee = get_user(request.form["username"])
        role_value_str = request.form["role"]
        result = validate_group_invite_form(group_id, invitee, role_value_str)
        if result.valid:
            create_group_invite(group_id, invitee.id, RoleEnum(int(role_value_str)))
        else:
            g.error_message = result.error

    g.group_details = get_group_details(group_id)
    g.group_members = get_group_members(group_id)
    g.group_invitees = get_group_invitees(group_id)
    g.roles = [role for role in RoleEnum if role != RoleEnum.Owner]
    g.sidebar = True
    return render_template("group-view.html")

@groups_bp.route("/join/<int:group_id>")
def route_group_join(group_id):
    username = session.get("username")
    if not username:
        return redirect("/login") # not logged in

    user = get_user(username)
    invite = get_group_invite(group_id, user.id)
    if invite:
        create_group_member(group_id, user.id, RoleEnum[invite.role])
        delete_group_invite(group_id, user.id)
        return redirect(f"/group/{group_id}")
    return redirect("/")
