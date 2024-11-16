from app import db
from sqlalchemy.sql import text
from .auth_service import get_user
from enums.role import role

def get_groups(username : str):
    result = db.session.execute(text("SELECT G.id, G.name FROM group_roles GR \
                                    JOIN users U ON U.id = GR.user_id \
                                    JOIN groups G ON G.id = GR.group_id \
                                    WHERE U.username = :username \
                                    "), {"username":username})
    return result.fetchall()
    
def create_group(username : str, group_name : str, group_desc : str = "") -> int:
    group_id = db.session.execute(text("INSERT INTO groups (name, description) VALUES (:group_name, :group_desc) RETURNING id"), 
                                        {"group_name":group_name, "group_desc":group_desc}).fetchone()[0]
    user_id = get_user(username).id
    db.session.execute(text("INSERT INTO group_roles (group_id, user_id, is_creator, role) VALUES (:group_id, :user_id, TRUE, :role)"), 
                            {"group_id":group_id, "user_id":user_id, "role":role.Owner.value})
    db.session.commit()
    return group_id