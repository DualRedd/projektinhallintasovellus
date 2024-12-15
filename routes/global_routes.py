from flask import request, session, g
from datetime import datetime, time
from config import config
from app import app
from enums.enums import task_priority_enum, task_state_enum, role_enum

# global data for rendering pages
@app.context_processor
def inject_config_data():
    return config
@app.context_processor
def inject_stored_data():
    res = {}
    for key in session:
        if "-stored" in key:
            res[key] = session[key]
    return {"stored_data": res}

# basic request data
@app.before_request
def get_user_data():
    g.username = session.get("username")
    g.user_id = session.get("user_id")
    g.priorities = [priority for priority in task_priority_enum]
    g.states = [state for state in task_state_enum]
    g.role_enum = role_enum

# form data storing
@app.after_request
def form_response_storage(response):
    if (300 <= response.status_code < 400):
        # if this is a redirect, store form values
        for key in request.form:
            if "-stored" not in key: continue
            if key.endswith("[]"):
                session[key] = request.form.getlist(key)
            else:
                session[key] = request.form[key]
    else:
        # if this is not a redirect, remove stored form values
        to_remove = []
        for key in session:
            if "-stored" in key: to_remove.append(key)
        for key in to_remove:
            session.pop(key)
    return response

# cache control
@app.after_request
def cache_control_headers(response):
    if not request.path.startswith('/static'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# Template filters
@app.template_filter("user_in_task")
def is_user_in_task(members : list[dict], username : str):
    return any(member["username"] == username for member in members)

@app.template_filter('format_datetime')
def format_datetime(value, format='%d.%m.%Y %H:%M'):
    if value is None: return "None"
    if format == '%d.%m.%Y %H:%M' and value.time() == time.max.replace(microsecond=0):
        return value.strftime('%d.%m.%Y')
    return value.strftime(format)

@app.template_filter('user_ids')
def get_user_ids_from_dict(users):
    return [user["id"] for user in users]
