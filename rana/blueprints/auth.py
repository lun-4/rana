from sanic import Blueprint
from sanic.response import json

from rana.decorators import auth_route

bp = Blueprint('auth')

@bp.route('/signup', methods=['GET', 'POST'])
async def signup_handler(request):
    pass

@bp.route('/login', methods=['GET', 'POST'])
async def login_handler(request):
    # returns page with errors when request has errors
    # (this is all on formdata)
    # default page if username, password not provided
    # end result is a redirect to the dashboard, plus session.
    pass
