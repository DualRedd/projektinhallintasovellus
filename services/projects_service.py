from sqlalchemy.sql import text
from app import db


def create_project(group_id : int, name : str, desc : str = "") -> int:
    project_id = db.session.execute(text("INSERT INTO projects (group_id, name, description) VALUES (:group_id, :name, :desc) RETURNING id"),
                                        {"group_id":group_id, "name":name, "desc":desc}).fetchone()[0]
    db.session.commit()
    return project_id

def update_project(project_id : int, project_name : str, project_desc : str = ""):
    db.session.execute(text("UPDATE projects SET name = :project_name, description = :project_desc WHERE id = :project_id"),
                            {"project_name":project_name, "project_desc":project_desc, "project_id":project_id})
    db.session.commit()

def update_project_archive_state(project_id : int, state : bool):
    db.session.execute(text("UPDATE projects SET archived = :state WHERE id = :project_id"),
                            {"state":state, "project_id":project_id})
    db.session.commit()

def delete_soft_project(project_id : int):
    db.session.execute(text("UPDATE projects SET visible = FALSE WHERE id = :project_id"),
                            {"project_id":project_id})
    db.session.commit()

def get_projects(group_id : int, archived : bool = None):
    projects = db.session.execute(text(f"SELECT id, name, description, archived FROM projects WHERE group_id = :group_id \
                                        {'AND archived = :archived' if archived is not None else ''} \
                                        AND visible = TRUE \
                                        ORDER BY archived, id"),
                                        {"group_id":group_id, "archived":archived}).fetchall()
    return projects

def get_project_details(project_id : int):
    details = db.session.execute(text("SELECT id, name, description, archived FROM projects WHERE id = :project_id AND visible = TRUE"),
                                        {"project_id":project_id}).fetchone()
    return details
