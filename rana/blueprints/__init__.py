from sanic import Blueprint
from .auth import bp as auth

from .heartbeats import bp as heartbeats
from .users import bp as users

__all__ = ['heartbeats', 'group']

api_group = Blueprint.group(users, heartbeats, url_prefix='/api/v1')
