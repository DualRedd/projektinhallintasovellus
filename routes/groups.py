from flask import Blueprint
from flask import session, request, render_template, redirect
from services.groups_service import create_group

groups_bp = Blueprint('groups', __name__)

@groups_bp.route("/create-group")
def route_create_group():
    return render_template("create-group-form.html")

@groups_bp.route("/create-group/result", methods=["POST"])
def route_create_group_result():
    username = session.get("username")
    if not username:
        return redirect("/") # not logged in
    group_name = request.form["name"]
    group_desc = request.form["desc"]
    create_group(username, group_name, group_desc)
    return redirect("/")