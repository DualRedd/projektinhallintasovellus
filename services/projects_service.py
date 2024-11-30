from sqlalchemy.sql import text
from app import db


def create_project(group_id : int, name : str, desc : str = "") -> int:
    project_id = db.session.execute(text("INSERT INTO projects (group_id, name, description) VALUES (:group_id, :name, :desc) RETURNING id"),
                                        {"group_id":group_id, "name":name, "desc":desc}).fetchone()[0]
    db.session.commit()
    return project_id

def get_projects(group_id : int, archived : bool = False):
    projects = db.session.execute(text("SELECT id, name, description FROM projects WHERE group_id = :group_id AND archived = :archived AND visible = TRUE"),
                                        {"group_id":group_id, "archived":archived}).fetchall()
    db.session.commit()
    return projects
