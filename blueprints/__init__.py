from sanic import Blueprint
from .heartbeats import bp as heartbeats

__all__ = ['heartbeats', 'group']

group = Blueprint.group(heartbeats, url_prefix='/api/v1')
