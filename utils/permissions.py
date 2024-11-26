from functools import wraps
from flask import Response, request, redirect, render_template, g
from enums.RoleEnum import RoleEnum

def permissions(require_login : bool = False, require_min_role : RoleEnum = None,
                        require_max_role : RoleEnum = None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            res = get_page_permission_response(require_login, require_min_role, require_max_role)
            if res is not None:
                return res
            return f(*args, **kwargs)
        return wrapped
    return decorator

def get_page_permission_response(require_login : bool = False, require_min_role : RoleEnum = None,
                                 require_max_role : RoleEnum = None) -> Response | str | None:
    if require_login and not g.username:
        return redirect("/login")
    if require_min_role or require_max_role:
        if not g.role or (require_min_role and require_min_role.value > g.role.value) or (require_max_role and require_max_role.value < g.role.value):
            if request.method == "POST":
                return redirect(request.referrer or "/")
            g.sidebar = False
            g.error_message = "You do not have the right to view this page!"
            g.error_code = 404
            return render_template("error.html")
    return None
