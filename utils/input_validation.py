from services.auth_service import user_exists
from config import MAX_INPUT_SIZES

class ValidationResult:
    def __init__(self, valid : bool, error : str = ""):
        self.valid = valid
        self.error = error

def validate_create_user_form(username : str, password : str, password_check : str) -> ValidationResult:
    if len(username) > MAX_INPUT_SIZES["username"]:
        return ValidationResult(False, "Liian pitkä käyttäjänimi!")
    if user_exists(username):
        return ValidationResult(False, "Käyttäjänimi on varattu!")
    if password != password_check:
        return ValidationResult(False, "Salasanat eivät täsmää!")
    if len(password) > MAX_INPUT_SIZES["password"]:
        return ValidationResult(False, "Liian pitkä salasana!")
    return ValidationResult(True)

def validate_login_form(username : str, password : str):
    if len(username) > MAX_INPUT_SIZES["username"] or len(password) > MAX_INPUT_SIZES["password"]:
        return ValidationResult(False, "Käyttäjänimi tai salasana on väärä!")
    return ValidationResult(True)

def validate_create_group_form(group_name : str, group_desc : str) -> ValidationResult:
    if len(group_name) > MAX_INPUT_SIZES["group_name"]:
        return ValidationResult(False, "Liian pitkä nimi!")
    if len(group_desc) > MAX_INPUT_SIZES["group_description"]:
        return ValidationResult(False, "Liian pitkä kuvaus!")
    return ValidationResult(True)
