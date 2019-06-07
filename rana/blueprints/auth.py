import uuid
import time
import urllib.parse
from pathlib import Path

from quart import (
    Blueprint, jsonify, render_template, render_template_string,
    session, current_app as app, request, redirect
)

from rana.auth import login, hash_password
from rana.errors import Unauthorized, BadRequest

bp = Blueprint('auth', __name__)


# those functions exist to decrease repetition.
async def _signup_tmpl(**kwargs):
    return await render_template('signup.html', **kwargs)


async def _login_tmpl(**kwargs):
    return await render_template('login.html', **kwargs)


async def _dashboard_tmpl(**kwargs):
    return await render_template('dashboard.html', **kwargs)


async def _extract_userpass():
    """extract a username/password tuple out of the request.

    Does not return a tuple if something happened.
    """
    req_data = (await request.get_data()).decode()

    # If no request data is found, we don't return an error, and instead
    # just wish to render the template without an error.
    if not req_data:
        raise BadRequest('')

    data = urllib.parse.parse_qs(req_data)

    try:
        username, password = data['username'][0], data['password'][0]
    except (KeyError, IndexError):
        raise BadRequest('username or password not provided')

    try:
        signup_code = data['signup_code'][0]
    except (KeyError, IndexError):
        signup_code = ''

    return username, password, signup_code


@bp.route('/signup', methods=['GET', 'POST'])
async def signup_handler():
    """Handle a signup for a user."""
    signup_allowed = app.cfg['rana']['signups']
    signup_code = app.cfg['rana']['signup_code']

    # configparser will give us an empty string when the key isn't set
    # so we set it to a value that isn't possible to achieve on the request
    # args. None fills up that purpose.
    if not signup_code:
        signup_code = None

    try:
        res = await _extract_userpass()
    except BadRequest as err:
        return await _signup_tmpl(error=err.message)

    # unpack formdata into what we want
    username, password, signup_code = res

    # check signup state
    if not signup_allowed:
        if signup_code != app.cfg['rana']['signup_code']:
            raise Unauthorized(
                'Signups are disabled and the signup code is invalid.')

    existing = await app.db.fetchrow("""
    select id from users where username = $1
    """, username)

    if existing is not None:
        return await _signup_tmpl(error='username exists')

    user_id = uuid.uuid4()
    api_key = uuid.uuid4()

    pwd_hash = await hash_password(password)

    await app.db.execute("""
    insert into users (id, username, password_hash, created_at)
    values ($1, $2, $3, $4)
    """, user_id, username, pwd_hash, time.time())

    await app.db.execute("""
    insert into api_keys (user_id, key)
    values ($1, $2)
    """, user_id, str(api_key))

    return redirect('/login')


@bp.route('/login', methods=['GET', 'POST'])
async def login_handler():
    """Logins a single user. Reroutes them to /dashboard on success.
    """
    if session.get('user_id'):
        return redirect('/dashboard')

    try:
        res = await _extract_userpass()
    except BadRequest as err:
        return await _login_tmpl(error=err.message)

    username, password, _ = res
    user_id = await login(username, password)

    orig_username = await app.db.fetchval("""
    select username from users where id = $1
    """, user_id)

    api_key = await app.db.fetchval("""
    select key from api_keys where user_id = $1
    """, user_id)

    session['username'] = orig_username
    session['api_key'] = api_key

    return redirect('/dashboard')


@bp.route('/dashboard', methods=['GET', 'POST'])
async def dashboard_handler():
    key = session.get('api_key')
    if not key:
        return redirect('/login')

    user_id = await app.db.fetchval("""
    select user_id from api_keys where key = $1
    """, str(key))

    if user_id is None:
        return redirect('/login')

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
    update api_keys set key = $2 where key = $1
    """, str(old_api_key), str(new_api_key))

    session['api_key'] = new_api_key
    return redirect('/dashboard')


@bp.route('/logout', methods=['GET'])
async def logout_handler():
    session['username'] = ''
    session['api_key'] = ''
    return redirect('/')
