from flask import Blueprint
from flask import session, request, render_template, redirect
from services.groups_service import create_group
from utils.input_validation import validate_create_group_form
from config import MAX_INPUT_SIZES

groups_bp = Blueprint('groups', __name__)

@groups_bp.route("/create-group", methods=["GET", "POST"])
def route_create_group():
    username = session.get("username")
    if not username:
        return redirect("/") # not logged in
    
    if request.method == "GET":
        return render_template("create-group-form.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES)
    elif request.method == "POST":
        group_name = request.form["name"]
        group_desc = request.form["desc"]
        result = validate_create_group_form(group_name, group_desc)
        if not result.valid:
            return render_template("create-group-form.html", MAX_INPUT_SIZES=MAX_INPUT_SIZES, error_message=result.error)
        create_group(username, group_name, group_desc)
        return redirect("/")