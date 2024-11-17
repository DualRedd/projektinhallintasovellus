from enums.RoleEnum import RoleEnum
from services.groups_service import get_group_role 

def check_group_permission(group_id : int, username : str, min_role : RoleEnum):
    user_role = get_group_role(group_id, username)
    return user_role and user_role.value >= min_role.value