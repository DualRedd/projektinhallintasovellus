import re
from datetime import datetime
from flask import session, request, g
from services.auth_service import user_exists, authenticate_user
from services.groups_service import get_group_role
from utils.tools import parse_form_datetime
from enums.enums import role_enum, task_priority_enum, task_state_enum
from config import config

class ValidationResult:
    def __init__(self, valid : bool, error : str = ""):
        self.valid = valid
        self.error = error

def validate_create_user_form(username : str, password : str, password_check : str) -> ValidationResult:
    if not (res := validate_string_size(username, "username", "Username")).valid:
        return res
    if username[0].isspace() or username[-1].isspace():
        return ValidationResult(False, f"Username cannot start or end with a space!")
    if not check_string_chars(username, "a-zA-Z0-9_\-äöå "):
        return ValidationResult(False, f"Username can only contain characters a-zA-Z0-9_-äöå and spaces!")
    if user_exists(username):
        return ValidationResult(False, "Username has already been taken!")
    if not (res := validate_string_size(password, "password", "Password")).valid:
        return res
    if password != password_check:
        return ValidationResult(False, "Passwords do not match!")
    return ValidationResult(True)

def validate_login_form(username : str, password : str) -> ValidationResult:
    if not authenticate_user(username, password):
        return ValidationResult(False, "Username or password is incorrect!")
    return ValidationResult(True)

def validate_group_details_form(group_name : str, group_desc : str) -> ValidationResult:
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not (res := validate_string_size(group_name, "group_name", "Group name")).valid:
        return res
    if not (res := validate_string_size(group_desc, "group_description", "Group description")).valid:
        return res
    return ValidationResult(True)

def validate_project_details_form(project_name : str, project_desc : str) -> ValidationResult:
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not (res := validate_string_size(project_name, "project_name", "Project name")).valid:
        return res
    if not (res := validate_string_size(project_desc, "project_description", "Project description")).valid:
        return res
    return ValidationResult(True)

def validate_project_archive_form(state : str):
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if state not in ["false", "true"]:
        return ValidationResult(False)
    return ValidationResult(True)

def validate_remove_member_form(user):
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not user:
        return ValidationResult(False, "User not found!")
    role = get_group_role(g.group_id, user.id)
    if not role:
        return ValidationResult(False, "User is not a member nor invited!")
    if role == role_enum.Owner:
        return ValidationResult(False, "Owner cannot be kicked!")
    if role.value >= g.role.value:
        return ValidationResult(False, "Invalid permissions!")
    return ValidationResult(True)

def validate_alter_role_form(user, role_value_str):
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not user:
        return ValidationResult(False, "User not found!")
    role = get_group_role(g.group_id, user.id)
    if not role:
        return ValidationResult(False, "User is not a member nor invited!")
    if role == role_enum.Owner:
        return ValidationResult(False, "Owner's role cannot be changed!")
    if role.value >= g.role.value:
        return ValidationResult(False, "Invalid permissions!")
    try:
        role_value = int(role_value_str)
    except ValueError:
        return ValidationResult(False, "Invalid role!")
    new_role = role_enum.get_by_value(role_value)
    if not new_role or new_role == role_enum.Owner:
        return ValidationResult(False, "Invalid role!")
    if new_role.value >= g.role.value:
        return ValidationResult(False, "Invalid permissions!")
    return ValidationResult(True)

def validate_group_invite_form(group_id : int, invitee, role_value_str : int) -> ValidationResult:
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not invitee:
        return ValidationResult(False, "No such user found!")
    if get_group_role(group_id, invitee.id):
        return ValidationResult(False, "The user is already a member or invited!")
    # Check if role input is valid
    try:
        role_value = int(role_value_str)
    except ValueError:
        return ValidationResult(False, "Invalid role!")
    new_role = role_enum.get_by_value(role_value)
    if not new_role or new_role == role_enum.Owner:
        return ValidationResult(False, "Invalid role!")
    if new_role.value >= g.role.value:
        return ValidationResult(False, "Invalid permissions!")
    return ValidationResult(True)

def validate_create_project_form(project_name : str, project_desc : str):
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not (res := validate_string_size(project_name, "project_name", "Project name")).valid:
        return res
    if not (res := validate_string_size(project_name, "project_description", "Project description")).valid:
        return res
    return ValidationResult(True)

def validate_task_data_form(task_name : str, task_desc : str, task_priority_str : str, task_date : str, task_time : str, task_members : list[str]):
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if g.project_details.archived:
        return ValidationResult(False, "This project is archived!")
    if not (res := validate_string_size(task_name, "task_name", "Task name")).valid:
        return res
    if not (res := validate_string_size(task_desc, "task_description", "Task description")).valid:
        return res
    try:
        print(task_priority_str)
        priority_int = int(task_priority_str)
        if not task_priority_enum.get_by_value(priority_int):
            return ValidationResult(False, "Invalid task priority!")
    except ValueError:
        return ValidationResult(False, "Invalid task priority!")
    try:
        deadline = parse_form_datetime(task_date, task_time)
        if deadline and deadline.date() < datetime.now().date():
            return ValidationResult(False, "Deadline cannot be set to the past!")
    except ValueError:
        return ValidationResult(False, "Invalid deadline!")
    for member in task_members:
        try:
            id = int(member)
            if not get_group_role(g.group_id, id, is_invitee=False):
                return ValidationResult(False, "Invalid user assigned!")
        except ValueError:
            return ValidationResult(False, "Invalid user assigned!")
    return ValidationResult(True)

def validate_task_state_form(state_str : str):
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if g.project_details.archived:
        return ValidationResult(False, "This project is archived!")
    try:
        state_int = int(state_str)
        if not task_state_enum.get_by_value(state_int):
            return ValidationResult(False, "Invalid task state!")
    except ValueError:
        return ValidationResult(False, "Invalid task state!")
    return ValidationResult(True)

def validate_task_delete_form():
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if g.project_details.archived:
        return ValidationResult(False, "This project is archived!")
    return ValidationResult(True)

def validate_project_task_search_form(sorting : list[str], min_date_str : str, max_date_str : str, states : list[str],
                                      priorities : list[str], members : list[str], member_query_type : str):
    if len(sorting) != 4:
        return ValidationResult(False, "Invalid sort options!")
    for sort_str in sorting:
        if sort_str not in ["deadline", "priority", "state", "title"]:
            return ValidationResult(False, "Invalid sort options!")
    if (res := validate_common_search(min_date_str, max_date_str, states, priorities, members, member_query_type)) is not None:
        return res
    return ValidationResult(True)

def validate_group_task_search_form(sorting : list[str], min_date_str : str, max_date_str : str, states : list[str],
                                      priorities : list[str], members : list[str], member_query_type : str):
    if len(sorting) != 5:
        return ValidationResult(False, "Invalid sort options!")
    for sort_str in sorting:
        if sort_str not in ["deadline", "priority", "state", "project", "title"]:
            return ValidationResult(False, "Invalid sort options!")
    if (res := validate_common_search(min_date_str, max_date_str, states, priorities, members, member_query_type)) is not None:
        return res
    return ValidationResult(True)

def validate_common_search(min_date_str : str, max_date_str : str, states : list[str], priorities : list[str], members : list[str], member_query_type : str):
    try:
        if min_date_str != "": datetime.strptime(min_date_str, '%Y-%m-%d')
    except ValueError:
        return ValidationResult(False, "Invalid start date!")
    try:
        if max_date_str != "": datetime.strptime(max_date_str, '%Y-%m-%d')
    except ValueError:
        return ValidationResult(False, "Invalid end date!")
    for state_str in states:
        try:
            state = int(state_str)
            if task_state_enum.get_by_value(state) is None:
                return ValidationResult(False, "Invalid state provided!")
        except ValueError:
            return ValidationResult(False, "Invalid state provided!")
    for priority_str in priorities:
        try:
            priority = int(priority_str)
            if task_priority_enum.get_by_value(priority) is None:
                return ValidationResult(False, "Invalid priority provided!")
        except ValueError:
            return ValidationResult(False, "Invalid priority provided!")
    for member_str in members:
        try:
            int(member_str)
            # don't check each individual member, that would be a lot of queries in the worst case
        except ValueError:
            return ValidationResult(False, "Invalid state provided!")
    if member_query_type not in ["any", "all", "exact"]:
        return ValidationResult(False, "Invalid member filter type!")
    return ValidationResult(True)

def validate_empty_form():
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    return ValidationResult(True)

# Helper functions
def check_csrf_token() -> bool:
    form_token = request.form.get("csrf_token")
    session_token = session.get("csrf_token")
    return form_token and session_token and form_token == session_token

def check_string_chars(string : str, allowed : str) -> bool:
    return bool(re.match(f"^[{allowed}]*$", string))

def validate_string_size(string : str, string_type : str, error_string : str) -> ValidationResult:
    if len(string) < config["MIN_INPUT_SIZES"][string_type]:
        return ValidationResult(False, f"{error_string} cannot be shorter than {config['MIN_INPUT_SIZES'][string_type]} characters!")
    if len(string) > config["MAX_INPUT_SIZES"][string_type]:
        return ValidationResult(False, f"{error_string} cannot be longer than {config['MAX_INPUT_SIZES'][string_type]} characters!")
    return ValidationResult(True)
