from quart import Blueprint, jsonify, render_template_string
from pathlib import Path

bp = Blueprint('auth', __name__)

async def _any_tmpl(filename: str):
    filepath = Path.cwd() / Path('static') / filename
    return await render_template_string(filepath.read_text())


async def _signup_tmpl():
    return await _any_tmpl('signup.html')


async def _login_tmpl():
    return await _any_tmpl('login.html')


@bp.route('/signup', methods=['GET', 'POST'])
async def signup_handler():
    return await _signup_tmpl()


@bp.route('/login', methods=['GET', 'POST'])
async def login_handler():
    # returns page with errors when request has errors
    # (this is all on formdata)
    # default page if username, password not provided
    # end result is a redirect to the dashboard, plus session.
    return await _login_tmpl()
