from sanic import Blueprint
from .heartbeats import bp as heartbeats
from .users import bp as users

__all__ = ['heartbeats', 'group']

group = Blueprint.group(users, heartbeats, url_prefix='/api/v1')
