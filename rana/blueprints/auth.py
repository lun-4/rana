from quart import Blueprint, jsonify

bp = Blueprint('auth', __name__)


@bp.route('/signup', methods=['GET', 'POST'])
async def signup_handler():
    pass


@bp.route('/login', methods=['GET', 'POST'])
async def login_handler():
    # returns page with errors when request has errors
    # (this is all on formdata)
    # default page if username, password not provided
    # end result is a redirect to the dashboard, plus session.
    pass
