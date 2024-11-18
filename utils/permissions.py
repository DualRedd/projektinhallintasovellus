from flask import session, request
from enums.RoleEnum import RoleEnum
from services.groups_service import get_group_role

def check_group_permission(group_id : int, username : str, min_role : RoleEnum) -> bool:
    user_role = get_group_role(group_id, username)
    return user_role and user_role.value >= min_role.value

def check_csrf_token() -> bool:
    form_token = request.form.get("csrf_token")
    session_token = session.get("csrf_token")
    return form_token and session_token and form_token == session_token
