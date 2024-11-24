from flask import request, session, g
from config import config
from app import app

# global data for rendering pages
@app.context_processor
def inject_config_data():
    return config
@app.context_processor
def inject_stored_data():
    res = {}
    for key in session:
        if key.endswith('-stored'):
            res[key] = session[key]
    return {"stored_data": res}

# basic request data
@app.before_request
def get_user_data():
    g.username = session.get("username")
    g.user_id = session.get("user_id")

# form data storing
@app.after_request
def form_response_storage(response):
    if (300 <= response.status_code < 400):
        # if this is a redirect, store form values
        for key in request.form:
            if key.endswith("-stored"): session[key] = request.form[key]
    else:
        # if this is not a redirect, remove stored form values
        to_remove = []
        for key in session:
            if key.endswith("-stored"): to_remove.append(key)
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
