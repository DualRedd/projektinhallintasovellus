from sqlalchemy.sql import text
from datetime import datetime
from app import db
from utils.tools import query_res_to_dict

def create_task(user_id : int, project_id : int, title : str, desc : str, priority : str, deadline : datetime) -> int:
    if deadline is not None: deadline = deadline.strftime('%Y-%m-%d %H:%M:%S')
    task_id = db.session.execute(text("INSERT INTO tasks (created_by_id, project_id, title, description, priority, deadline) \
                                    VALUES (:user_id, :project_id, :title, :desc, :priority, :deadline) RETURNING id"),
                                    {"user_id":user_id, "project_id":project_id, "project_name":project_id, "title":title, "desc":desc,
                                    "priority":priority, "deadline":deadline}).fetchone()[0]
    db.session.commit()
    return task_id

def create_task_assignment(task_id : int, user_id : int):
    task_id = db.session.execute(text("INSERT INTO task_assignments (task_id, user_id) VALUES (:task_id, :user_id) RETURNING id"),
                                    {"task_id":task_id, "user_id":user_id}).fetchone()[0]
    db.session.commit()

def get_task_members(task_id : int) -> list[dict]:
    result = db.session.execute(text("SELECT U.id, U.username FROM task_assignments TA \
                                     JOIN users U ON U.id = TA.user_id AND U.visible = TRUE \
                                     WHERE TA.task_id = :task_id"),
                                    {"task_id":task_id}).fetchall()
    return [{"id":int(row.id), "username":row.username} for row in result]

def get_tasks_dicts(project_id : int) -> list[dict]:
    result = db.session.execute(text("SELECT id, title, description, state, priority, deadline FROM tasks \
                                    WHERE project_id = :project_id AND visible = TRUE"),
                                    {"project_id":project_id}).fetchall()
    db.session.commit()
    result = query_res_to_dict(result)
    for task in result:
        task["deadline"] = task["deadline"].strftime('%d.%m.%Y %H:%M') if task["deadline"] else "Not Set"
        task["members"] = get_task_members(task["id"])
    return result
