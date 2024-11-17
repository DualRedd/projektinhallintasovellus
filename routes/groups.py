# standard imports
from flask import Blueprint
from flask import session, request, render_template, redirect
# Internal services
from services.groups_service import create_group, get_group_details, get_group_invitees, get_group_members, get_group_role, create_group_invite
from services.auth_service import get_user
from utils.input_validation import validate_create_group_form, validate_group_invite_form
from utils.permissions import check_group_permission
# Enums and config
from enums.roleEnum import roleEnum
from config import MAX_INPUT_SIZES

groups_bp = Blueprint('groups', __name__)

@groups_bp.route("/create-group", methods=["GET", "POST"])
def route_create_group():
    username = session.get("username")
    if not username:
        return redirect("/") # not logged in
    
    if request.method == "GET":
        return render_template("create-group-form.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES)
    elif request.method == "POST":
        group_name = request.form["name"]
        group_desc = request.form["desc"]
        result = validate_create_group_form(group_name, group_desc)
        if not result.valid:
            return render_template("create-group-form.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES, error_message=result.error)
        group_id = create_group(username, group_name, group_desc)
        return redirect(f"/group/{group_id}")


@groups_bp.route("/group/<int:group_id>", methods=["GET", "POST"])
def route_group_page(group_id):
    username = session.get("username")
    if not username:
        return redirect("/") # not logged in
    is_member = get_group_role(group_id, username) != None
    if not is_member:
        return render_template("error.html", error_code='404', error_message="Sinulla ei ole oikeuksia tälle sivulle!")
    
    error_message = ""
    if request.method == "POST": # invite form posted
        if check_group_permission(group_id, username, roleEnum.Co_owner): # Co_owner is minimum required permission level
            invitee = get_user(request.form["username"])
            result = validate_group_invite_form(group_id, invitee)
            if result.valid:
                create_group_invite(group_id, invitee.id)
            else:
                error_message = result.error

    group_details = get_group_details(group_id)
    group_members = get_group_members(group_id)
    group_invitees = get_group_invitees(group_id)
    return render_template("group-view.html", group_details=group_details, group_members=group_members, group_invitees=group_invitees,
                                            MAX_INPUT_SIZES=MAX_INPUT_SIZES, error_message=error_message)
        

    


    
    

    
