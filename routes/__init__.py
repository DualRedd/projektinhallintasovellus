from .auth import auth_bp
from .groups import groups_bp
from .base import base_bp

blueprints = [auth_bp, groups_bp, base_bp]