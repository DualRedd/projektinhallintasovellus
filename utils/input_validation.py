from services.auth_service import user_exists, authenticate_user
from services.groups_service import get_group_role, check_invite_exists
from config import MAX_INPUT_SIZES

class ValidationResult:
    def __init__(self, valid : bool, error : str = ""):
        self.valid = valid
        self.error = error

def validate_create_user_form(username : str, password : str, password_check : str) -> ValidationResult:
    if len(username) > MAX_INPUT_SIZES["username"]:
        return ValidationResult(False, "Username is too long!")
    if user_exists(username):
        return ValidationResult(False, "Username has already been taken!")
    if password != password_check:
        return ValidationResult(False, "Passwords do not match!")
    if len(password) > MAX_INPUT_SIZES["password"]:
        return ValidationResult(False, "Password is too long!")
    return ValidationResult(True)

def validate_login_form(username : str, password : str):
    if len(username) > MAX_INPUT_SIZES["username"] or len(password) > MAX_INPUT_SIZES["password"]:
        return ValidationResult(False, "Username or password is incorrect!")
    if not authenticate_user(username, password):
        return ValidationResult(False, "Username or password is incorrect!")
    return ValidationResult(True)

def validate_create_group_form(group_name : str, group_desc : str) -> ValidationResult:
    if len(group_name) > MAX_INPUT_SIZES["group_name"]:
        return ValidationResult(False, "Group name is too long!")
    if len(group_desc) > MAX_INPUT_SIZES["group_description"]:
        return ValidationResult(False, "Group description is too long!")
    return ValidationResult(True)

def validate_group_invite_form(group_id : int, invitee):
    if not invitee:
        return ValidationResult(False, "No such user found!")
    if get_group_role(group_id, invitee.username):
        return ValidationResult(False, "The user is already a member of the group!")
    if check_invite_exists(group_id, invitee.id):
        return ValidationResult(False, "The user has already been invited!")
    return ValidationResult(True)