import time
import datetime
import dateutil.parser

import pytest

from rana.blueprints.heartbeats import process_hb, fetch_machine

@pytest.mark.asyncio
async def test_heartbeats(test_cli_user):
    """Test heartbeat creation for the given user."""
    resp = await test_cli_user.post('/api/v1/users/current/heartbeats', json={
        'entity': '/home/uwu/uwu.py',
        'type': 'file',
        'category': None,
        'time': time.time(),
        'project': 'awoo',
    })

    assert resp.status_code == 201
    rjson = await resp.json
    assert isinstance(rjson, dict)

    data = rjson['data']
    assert isinstance(data, dict)
    assert data['project'] == 'awoo'


async def do_heartbeats(test_cli_user, minutes=10, *, project='awoo', start=None):
    """Add heartbeats."""
    start = start or datetime.datetime.now()
    end = start + datetime.timedelta(minutes=minutes)

    app = test_cli_user.cli.app
    user_id = test_cli_user.user['id']

    mach_id = await fetch_machine(user_id, 'test_machine', app_=app)

    for n in range(minutes):
        hb_time = start + datetime.timedelta(minutes=n)

        heartbeat = await process_hb(user_id, mach_id, {
            'entity': '/home/uwu/uwu.py',
            'type': 'file',
            'category': None,
            'time': hb_time.timestamp(),
            'is_write': True,
            'project': project,
            'language': 'uwulang',

            'branch': None,
            'lines': 10,
            'lineno': None,
            'cursorpos': None,
        }, app_=app)

        assert heartbeat is not None

    return start, end


@pytest.mark.asyncio
async def test_durations(test_cli_user):
    """Test if given heartbeats generate a duration."""
    start, end = await do_heartbeats(test_cli_user)

    now = datetime.datetime.now()
    now_str = f'{now.year}-{now.month}-{now.day}'
    resp = await test_cli_user.get(
        f'/api/v1/users/current/durations?date={now_str}')

    assert resp.status_code == 200
    rjson = await resp.json
    assert isinstance(rjson, dict)

    data = rjson['data']
    assert isinstance(data, list)

    try:
        duration = next(iter(data))
    except StopIteration:
        raise Exception('data is empty')

    assert isinstance(duration, dict)
    assert duration['project'] == 'awoo'

    dstart = dateutil.parser.parse(duration['start'])
    dend = dateutil.parser.parse(duration['end'])

    assert (dstart - start) < datetime.timedelta(seconds=30)
    assert (dend - end) < datetime.timedelta(seconds=30)


@pytest.mark.asyncio
async def test_summaries(test_cli_user):
    """Test summary generation"""
    start, end = await do_heartbeats(test_cli_user, 10, project='awoo')
    start2, end2 = await do_heartbeats(test_cli_user, 9, project='awoo2', start=end + datetime.timedelta(minutes=15))

    now = datetime.datetime.now()
    now_str = f'{now.year}-{now.month}-{now.day}'

    resp = await test_cli_user.get(
        f'/api/v1/users/current/summaries?start={now_str}&end={now_str}')

    assert resp.status_code == 200
    rjson = await resp.json
    assert isinstance(rjson, dict)

    s_start = dateutil.parser.parse(rjson['start'])
    s_end = dateutil.parser.parse(rjson['end'])

    assert s_start.day == s_end.day == now.day
    assert s_start.month == s_end.month == now.month

    data = rjson['data']
    assert isinstance(data, list)

    try:
        data1 = next(iter(rjson['data']))
    except StopIteration:
        raise Exception('rjson.data is empty')

    assert isinstance(data1['grand_total']['total_seconds'], float)

    assert isinstance(data1['languages'], list)
    assert isinstance(data1['projects'], list)

    projects = data1['projects']
    assert isinstance(projects, list)

    # the first should always be awoo, the second should be always awoo2
    # due to the amount of time spent in them
    assert projects[0]['name'] == 'awoo'
    assert projects[1]['name'] == 'awoo2'
