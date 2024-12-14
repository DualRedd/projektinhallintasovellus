from sqlalchemy.sql import text
from datetime import datetime
from app import db
from utils.tools import query_res_to_dict
from enums.enums import task_state_enum, task_priority_enum

def create_task(project_id : int, title : str, desc : str, priority : task_priority_enum, deadline : datetime) -> int:
    if deadline is not None: deadline = deadline.strftime('%Y-%m-%d %H:%M:%S')
    task_id = db.session.execute(text("INSERT INTO tasks (project_id, title, description, priority, deadline) \
                                    VALUES (:project_id, :title, :desc, :priority, :deadline) RETURNING id"),
                                    {"project_id":project_id, "title":title, "desc":desc,
                                    "priority":priority.value, "deadline":deadline}).fetchone()[0]
    db.session.commit()
    return task_id

def update_task(task_id : int, title : str, desc : str, priority : task_priority_enum, deadline : datetime):
    if deadline is not None: deadline = deadline.strftime('%Y-%m-%d %H:%M:%S')
    db.session.execute(text("UPDATE tasks SET title = :title, description = :desc, priority = :priority,  \
                            deadline = :deadline WHERE id = :task_id"),
                            {"task_id":task_id, "title":title, "desc":desc, "priority":priority.value, "deadline":deadline})
    db.session.commit()

def set_task_assignments(task_id : int, user_ids : list[int]):
    db.session.execute(text("DELETE FROM task_assignments WHERE task_id = :task_id"), {"task_id":task_id})
    for user_id in user_ids:
        db.session.execute(text("INSERT INTO task_assignments (task_id, user_id) VALUES (:task_id, :user_id)"),
                                {"task_id":task_id, "user_id":user_id})
    db.session.commit()

def exists_task_assignment(task_id : int, user_id : int) -> bool:
    result = db.session.execute(text("SELECT task_id, user_id FROM task_assignments WHERE task_id = :task_id AND user_id = :user_id"),
                                    {"task_id":task_id, "user_id":user_id}).fetchone()
    return result is not None

def update_task_state(task_id : int, state : task_state_enum):
    task_id = db.session.execute(text("UPDATE tasks SET state=:state WHERE id=:task_id;"),
                                    {"state":state.value, "task_id":task_id})
    db.session.commit()

def get_task_members(task_id : int) -> list[dict]:
    result = db.session.execute(text("SELECT U.id, U.username FROM task_assignments TA \
                                     JOIN users U ON U.id = TA.user_id AND U.visible = TRUE \
                                     WHERE TA.task_id = :task_id \
                                     ORDER BY U.id"),
                                    {"task_id":task_id}).fetchall()
    return [{"id":int(row.id), "username":row.username} for row in result]

def get_tasks(project_id : int, states : list[str] = None, priorities : list[str] = None, members : list[int] = None,
              member_query_type : str = None, min_date : datetime = None, max_date : datetime = None):
    result = db.session.execute(text(f"SELECT T.id, T.title, T.description, \
                                            T.state, T.priority, T.deadline, \
                                            JSON_AGG ( \
                                                JSON_BUILD_OBJECT( \
                                                    'id', U.id, \
                                                    'username', U.username \
                                                ) \
                                            ) AS members \
                                    FROM tasks T \
                                    LEFT JOIN task_assignments TA ON T.id = TA.task_id \
                                    LEFT JOIN users U ON TA.user_id = U.id AND U.visible = TRUE \
                                    WHERE T.project_id = :project_id \
                                        AND T.visible = TRUE \
                                        {'AND T.deadline >= :min_date' if min_date else ''} \
                                        {'AND T.deadline <= :max_date' if max_date else ''} \
                                        {'AND T.state = ANY(:states)' if states is not None else ''} \
                                        {'AND T.priority = ANY(:priorities)' if priorities is not None else ''} \
                                    GROUP BY T.id \
                                    {'HAVING ARRAY_AGG(TA.user_id) && :members' if member_query_type == 'any' else ''} \
                                    {'HAVING ARRAY_AGG(TA.user_id) @> :members' if member_query_type == 'all' else ''} \
                                    {'HAVING ARRAY_AGG(TA.user_id) @> :members AND ARRAY_AGG(TA.user_id) <@ :members' if member_query_type == 'exact' else ''} \
                                    ORDER BY T.id"),
                                    {"project_id":project_id, "min_date":min_date, "max_date":max_date,
                                     "states":states, "priorities":priorities, "members":members}).fetchall()
    result = query_res_to_dict(result)
    for task in result:
        task["state"] = task_state_enum.get_by_value(int(task["state"]))
        task["priority"] = task_priority_enum.get_by_value(int(task["priority"]))
    return result
