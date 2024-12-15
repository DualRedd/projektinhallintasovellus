from sqlalchemy.sql import text
from datetime import datetime, time
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

def delete_task(task_id : int):
    db.session.execute(text("UPDATE tasks SET visible = FALSE WHERE id = :task_id"), {"task_id":task_id})
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

def get_tasks_project(group_id : int, project_id : int, states : list[str] = None, priorities : list[str] = None, members : list[int] = None,
              member_query_type : str = None, min_date : datetime = None, max_date : datetime = None,
              include_incomplete_before_min_date : bool = False, include_null_deadlines : bool = True):
    if min_date: min_date = datetime.combine(min_date.date(), time.min)
    if max_date: max_date = datetime.combine(max_date.date(), time.max)
    result = db.session.execute(text(f"SELECT T.id, T.title, T.description, \
                                                T.state, T.priority, T.deadline, \
                                                JSON_AGG ( \
                                                    JSON_BUILD_OBJECT( \
                                                        'id', U.id, \
                                                        'username', U.username, \
                                                        'is_member', (GR.user_id IS NOT NULL AND GR.is_invitee = FALSE) OR U.id IS NULL \
                                                    ) \
                                                ) AS members \
                                    FROM tasks T \
                                    LEFT JOIN task_assignments TA ON T.id = TA.task_id \
                                    LEFT JOIN users U ON TA.user_id = U.id AND U.visible = TRUE \
                                    LEFT JOIN group_roles GR ON GR.group_id = :group_id AND GR.user_id = U.id \
                                    WHERE T.project_id = :project_id \
                                        AND T.visible = TRUE \
                                        {'AND (T.deadline >= :min_date OR T.deadline IS NULL)' if min_date is not None and not include_incomplete_before_min_date else ''} \
                                        {'AND (T.deadline >= :min_date OR T.state != :completed)' if min_date is not None and include_incomplete_before_min_date else ''} \
                                        {'AND (T.deadline <= :max_date OR T.deadline IS NULL)' if max_date is not None else ''} \
                                        {'AND T.deadline IS NOT NULL' if not include_null_deadlines else ''} \
                                        {'AND T.state = ANY(:states)' if states is not None else ''} \
                                        {'AND T.priority = ANY(:priorities)' if priorities is not None else ''} \
                                    GROUP BY T.id \
                                    {'HAVING ARRAY_AGG(TA.user_id) && :members' if member_query_type == 'any' else ''} \
                                    {'HAVING ARRAY_AGG(TA.user_id) @> :members' if member_query_type == 'all' else ''} \
                                    {'HAVING ARRAY_AGG(TA.user_id) @> :members AND ARRAY_AGG(TA.user_id) <@ :members' if member_query_type == 'exact' else ''} \
                                    ORDER BY T.id"),
                                    {"group_id":group_id, "project_id":project_id, "min_date":min_date, "max_date":max_date,
                                     "states":states, "priorities":priorities, "members":members, "completed":str(task_state_enum.Completed.value)}).fetchall()
    result = query_res_to_dict(result)
    for task in result:
        task["state"] = task_state_enum.get_by_value(int(task["state"]))
        task["priority"] = task_priority_enum.get_by_value(int(task["priority"]))
    return result

def get_tasks_group(group_id : int, states : list[str] = None, priorities : list[str] = None, members : list[int] = None,
              member_query_type : str = None, min_date : datetime = None, max_date : datetime = None, projects : list[int] = None,
              include_archived : bool = True, include_incomplete_before_min_date : bool = False, include_null_deadlines : bool = True):
    if min_date: min_date = datetime.combine(min_date.date(), time.min)
    if max_date: max_date = datetime.combine(max_date.date(), time.max)
    result = db.session.execute(text(f"SELECT T.id, P.id AS project_id, T.title, P.name AS project_title, P.archived, \
                                                T.description, T.state, T.priority, T.deadline, \
                                                JSON_AGG ( \
                                                    JSON_BUILD_OBJECT( \
                                                        'id', U.id, \
                                                        'username', U.username, \
                                                        'is_member', (GR.user_id IS NOT NULL AND GR.is_invitee = FALSE) OR U.id IS NULL \
                                                    ) \
                                                ) AS members \
                                    FROM tasks T \
                                    LEFT JOIN projects P ON P.id = T.project_id \
                                    LEFT JOIN task_assignments TA ON T.id = TA.task_id \
                                    LEFT JOIN users U ON TA.user_id = U.id AND U.visible = TRUE \
                                    LEFT JOIN group_roles GR ON GR.group_id = :group_id AND GR.user_id = U.id \
                                    WHERE P.group_id = :group_id \
                                        AND T.visible = TRUE \
                                        {'AND (T.deadline >= :min_date OR T.deadline IS NULL)' if min_date is not None and not include_incomplete_before_min_date else ''} \
                                        {'AND (T.deadline >= :min_date OR T.state != :completed)' if min_date is not None and include_incomplete_before_min_date else ''} \
                                        {'AND (T.deadline <= :max_date OR T.deadline IS NULL)' if max_date is not None else ''} \
                                        {'AND T.deadline IS NOT NULL' if not include_null_deadlines else ''} \
                                        {'AND T.state = ANY(:states)' if states is not None else ''} \
                                        {'AND T.priority = ANY(:priorities)' if priorities is not None else ''} \
                                        {'AND P.id = ANY(:projects)' if projects is not None else ''} \
                                        {'AND P.archived = FALSE' if not include_archived else ''} \
                                    GROUP BY T.id, P.id \
                                    {'HAVING ARRAY_AGG(TA.user_id) && :members' if member_query_type == 'any' else ''} \
                                    {'HAVING ARRAY_AGG(TA.user_id) @> :members' if member_query_type == 'all' else ''} \
                                    {'HAVING ARRAY_AGG(TA.user_id) @> :members AND ARRAY_AGG(TA.user_id) <@ :members' if member_query_type == 'exact' else ''} \
                                    ORDER BY T.id"),
                                    {"group_id":group_id, "min_date":min_date, "max_date":max_date, "states":states,
                                     "priorities":priorities, "members":members, "projects":projects, "completed":str(task_state_enum.Completed.value)}).fetchall()
    result = query_res_to_dict(result)
    for task in result:
        task["state"] = task_state_enum.get_by_value(int(task["state"]))
        task["priority"] = task_priority_enum.get_by_value(int(task["priority"]))
    return result

def get_state_count_by_user_project(group_id : int, project_id : int):
    user_state_counts = db.session.execute(text("SELECT U.username, T.state, COUNT(T.id) AS count \
                                                FROM users U \
                                                JOIN group_roles GR ON GR.user_id = U.id AND GR.group_id = :group_id AND GR.is_invitee = FALSE  \
                                                LEFT JOIN task_assignments TA ON TA.user_id = U.id \
                                                LEFT JOIN tasks T ON T.id = TA.task_id AND T.project_id = :project_id AND T.visible = TRUE  \
                                                WHERE U.visible = TRUE \
                                                GROUP BY U.id, T.state \
                                                ORDER BY U.id, T.state \
                                                "), 
                                                {"group_id":group_id, "project_id":project_id}).fetchall()
    counts_by_user = {}
    for row in user_state_counts:
        if row.username not in counts_by_user:
            counts_by_user[row.username] = dict((state.value, 0) for state in task_state_enum)
        if row.state == None: continue
        counts_by_user[row.username][int(row.state)] = int(row.count)
    return counts_by_user
