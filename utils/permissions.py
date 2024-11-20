from flask import Response, session, request, redirect, render_template, g
from enums.RoleEnum import RoleEnum
from services.groups_service import get_group_role

def check_group_permission(group_id : int, username : str, min_role : RoleEnum) -> bool:
    user_role = get_group_role(group_id, username)
    return user_role and user_role.value >= min_role.value

def check_csrf_token() -> bool:
    form_token = request.form.get("csrf_token")
    session_token = session.get("csrf_token")
    return form_token and session_token and form_token == session_token

def get_page_permission_response(require_login : bool = False, require_group_membership : bool = False) -> Response | str | None:
    if require_login and not g.username:
        return redirect("/login")
    if require_group_membership:
        if get_group_role(g.group_id, g.username) is None:
            g.error_message = "You do not have the right to view this page!"
            g.error_code = 404
            return render_template("error.html")
    return None
