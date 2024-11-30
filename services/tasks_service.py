from sqlalchemy.sql import text
from datetime import datetime
from app import db

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
