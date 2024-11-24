from sqlalchemy.sql import text
from app import db
from services.auth_service import get_user
from enums.RoleEnum import RoleEnum

def get_groups(username : str):
    result = db.session.execute(text("SELECT G.id, G.name FROM group_roles GR \
                                    JOIN users U ON U.id = GR.user_id AND U.visible = TRUE \
                                    JOIN groups G ON G.id = GR.group_id AND G.visible = TRUE \
                                    WHERE U.username = :username \
                                    "), {"username":username}).fetchall()
    return result

def get_invites(username : str):
    result = db.session.execute(text("SELECT G.id AS group_id, G.name AS group_name, GI.role FROM group_invites GI \
                                    JOIN users U ON U.id = GI.invitee_id AND U.visible = TRUE \
                                    JOIN groups G ON G.id = GI.group_id AND G.visible = TRUE \
                                    WHERE U.username = :username \
                                    "), {"username":username}).fetchall()
    return result

def get_group_details(group_id : int):
    result = db.session.execute(text("SELECT id, name, description FROM groups \
                                    WHERE id = :group_id AND visible = TRUE \
                                    "), {"group_id":group_id}).fetchone()
    return result

def get_group_members(group_id : int):
    result = db.session.execute(text("SELECT U.id, U.username, GR.role FROM group_roles GR \
                                    JOIN users U ON U.id = GR.user_id AND U.visible = TRUE \
                                    JOIN groups G ON G.id = GR.group_id AND G.visible = TRUE \
                                    WHERE GR.group_id = :group_id \
                                    "), {"group_id":group_id}).fetchall()
    return result

def get_group_invitees(group_id : int):
    result = db.session.execute(text("SELECT U.id, U.username, GI.role FROM group_invites GI \
                                    JOIN users U ON U.id = GI.invitee_id AND U.visible = TRUE \
                                    JOIN groups G ON G.id = GI.group_id AND G.visible = TRUE \
                                    WHERE GI.group_id = :group_id \
                                    "), {"group_id":group_id}).fetchall()
    return result

def get_group_role(group_id : int, username : str) -> RoleEnum | None:
    result = db.session.execute(text("SELECT GR.role FROM group_roles GR \
                                    JOIN users U ON U.id = GR.user_id AND U.visible = TRUE \
                                    JOIN groups G ON G.id = GR.group_id AND G.visible = TRUE \
                                    WHERE GR.group_id = :group_id AND U.username = :username \
                                    "), {"group_id":group_id, "username":username}).fetchone()
    return RoleEnum[result[0]] if result else None

def create_group(group_name : str, group_desc : str = "") -> int:
    group_id = db.session.execute(text("INSERT INTO groups (name, description) VALUES (:group_name, :group_desc) RETURNING id"),
                                        {"group_name":group_name, "group_desc":group_desc}).fetchone()[0]
    db.session.commit()
    return group_id

def update_group(group_id : int, group_name : str, group_desc : str = ""):
    db.session.execute(text("UPDATE groups SET name = :group_name, description = :group_desc WHERE id = :group_id"),
                            {"group_name":group_name, "group_desc":group_desc, "group_id":group_id})
    db.session.commit()

def delete_group(group_id : int):
    db.session.execute(text("UPDATE groups SET visible = FALSE WHERE id = :group_id"),
                            {"group_id":group_id})
    db.session.commit()

def create_group_member(group_id : int, user_id : int, role : RoleEnum):
    db.session.execute(text("INSERT INTO group_roles (group_id, user_id, role) VALUES (:group_id, :user_id, :role)"),
                            {"group_id":group_id, "user_id":user_id, "role":role.name})
    db.session.commit()

def delete_group_member(group_id : int, user_id : int):
    db.session.execute(text("DELETE FROM group_roles WHERE group_id = :group_id AND user_id = :user_id"),
                            {"group_id":group_id, "user_id":user_id})
    db.session.commit()

def get_group_invite(group_id : int, invitee_id : int):
    result = db.session.execute(text("SELECT group_id, invitee_id, role FROM group_invites WHERE group_id = :group_id AND invitee_id = :invitee_id"),
                                    {"group_id":group_id, "invitee_id":invitee_id}).fetchone()
    return result

def create_group_invite(group_id : int, invitee_id : int, role : RoleEnum):
    db.session.execute(text("INSERT INTO group_invites (group_id, invitee_id, role) VALUES (:group_id, :invitee_id, :role)"),
                            {"group_id":group_id, "invitee_id":invitee_id, "role":role.name})
    db.session.commit()

def delete_group_invite(group_id : int, invitee_id : int):
    db.session.execute(text("DELETE FROM group_invites WHERE group_id = :group_id AND invitee_id = :invitee_id"),
                            {"group_id":group_id, "invitee_id":invitee_id})
    db.session.commit()
