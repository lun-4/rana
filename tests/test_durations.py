import time
import datetime
import dateutil.parser

import pytest

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


async def do_heartbeats(test_cli_user, minutes=10, *, project='awoo'):
    """Send heartbeats."""
    start = datetime.datetime.now()
    end = datetime.datetime.now() + datetime.timedelta(minutes=minutes)

    for n in range(minutes):
        resp = await test_cli_user.post(
            '/api/v1/users/current/heartbeats', json={
                'entity': '/home/uwu/uwu.py',
                'type': 'file',
                'category': None,
                'time': time.time() + (n * 60),
                'project': project,
            })

        assert resp.status_code == 201

    return start, end


@pytest.mark.asyncio
async def test_durations(test_cli_user):
    """Test if given heartbeats generate a duration."""
    start, end = await do_heartbeats(test_cli_user)

    utcnow = datetime.datetime.utcnow()
    now = f'{utcnow.year}-{utcnow.month}-{utcnow.day}'
    resp = await test_cli_user.get(
        f'/api/v1/users/current/durations?date={now}')

    assert resp.status_code == 200
    rjson = await resp.json
    assert isinstance(rjson, dict)

    data = rjson['data']
    assert isinstance(data, list)

    duration = next(iter(data))
    assert isinstance(duration, dict)
    assert duration['project'] == 'awoo'

    dstart = dateutil.parser.parse(duration['start'])
    dend = dateutil.parser.parse(duration['end'])

    assert (dstart - start) < datetime.timedelta(seconds=30)
    assert (dend - end) < datetime.timedelta(seconds=30)


@pytest.mark.asyncio
async def test_summaries(test_cli_user):
    """Test summary generation"""
    start, end = await do_heartbeats(test_cli_user, 30, project='awoo')
    start2, end2 = await do_heartbeats(test_cli_user, 30, project='awoo2')

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
