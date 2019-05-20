import uuid
import time
import urllib.parse
from pathlib import Path

from quart import (
    Blueprint, jsonify, render_template_string, session,
    current_app as app, request, redirect
)

from rana.auth import login, hash_password
from rana.errors import Unauthorized

bp = Blueprint('auth', __name__)


async def _any_tmpl(filename: str, **kwargs):
    filepath = Path.cwd() / Path('static') / filename

    return await render_template_string(
        filepath.read_text(), session=session, **kwargs)


async def _signup_tmpl(**kwargs):
    return await _any_tmpl('signup.html', **kwargs)


async def _login_tmpl(**kwargs):
    return await _any_tmpl('login.html', **kwargs)


async def _dashboard_tmpl():
    return await _any_tmpl('dashboard.html')


async def _extract_userpass(tmpl):
    """extract a username/password tuple out of the request.

    Does not return a tuple if something happened.
    """
    req_data = (await request.get_data()).decode()
    if not req_data:
        return await tmpl()

    data = urllib.parse.parse_qs(req_data)

    try:
        username, password = data['username'][0], data['password'][0]
    except (KeyError, IndexError):
        return await tmpl(error='username or password not provided')

    return username, password


@bp.route('/signup', methods=['GET', 'POST'])
async def signup_handler():
    """Handle a signup for a user."""
    res = await _extract_userpass(_signup_tmpl)
    if not isinstance(res, tuple):
        return res

    username, password = res

    existing = await app.db.fetchrow("""
    select id from users where username = ?
    """, (username,))

    if existing is not None:
        return await _signup_tmpl(error='username already exists')

    user_id = uuid.uuid4()
    api_key = uuid.uuid4()

    pwd_hash = await hash_password(password)

    await app.db.execute("""
    insert into users (id, username, password_hash, created_at)
    values (?, ?, ?, ?)
    """, (user_id, username, pwd_hash, time.time()))

    await app.db.execute("""
    insert into api_keys (user_id, key)
    values (?, ?)
    """, (user_id, api_key))

    return redirect('/login')


@bp.route('/login', methods=['GET', 'POST'])
async def login_handler():
    """Logins a single user. Reroutes them to /dashboard on success.
    """
    res = await _extract_userpass(_login_tmpl)
    if not isinstance(res, tuple):
        return res

    username, password = res
    user_id = await login(username, password)

    orig_username = await app.db.fetchval("""
    select username from users where id = ?
    """, (user_id,))

    api_key = await app.db.fetchval("""
    select key from api_keys where user_id = ?
    """, (user_id,))

    session['username'] = orig_username
    session['api_key'] = api_key

    return redirect('/dashboard')


@bp.route('/dashboard', methods=['GET', 'POST'])
async def dashboard_handler():
    return await _dashboard_tmpl()


@bp.route('/revoke_api_key', methods=['GET', 'POST'])
async def revoke_api_key():
    """Revoke the user's API key, generating a new one in the
    process."""
    old_api_key = session['api_key']
    if not old_api_key:
        raise Unauthorized('no api key provided')

    new_api_key = uuid.uuid4()

    await app.db.execute("""
    update api_keys set key = ? where key = ?
    """, (old_api_key, new_api_key))

    session['api_key'] = new_api_key
    return await _dashboard_tmpl()


@bp.route('/logout', methods=['GET'])
async def logout_handler():
    session['username'] = ''
    session['api_key'] = ''
    return await _any_tmpl('index.html')
