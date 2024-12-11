from .auth import auth_bp
from .groups import groups_bp
from .base import base_bp
from .projects import projects_bp
from .tasks import tasks_bp

blueprints = [auth_bp, groups_bp, base_bp, projects_bp, tasks_bp]
