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


@pytest.mark.asyncio
async def test_durations(test_cli_user):
    """Test if given"""
    # create 10 minutes duration manually
    start = datetime.datetime.now()

    for n in range(10):
        resp = await test_cli_user.post(
            '/api/v1/users/current/heartbeats', json={
                'entity': '/home/uwu/uwu.py',
                'type': 'file',
                'category': None,
                'time': time.time() + (n * 60),
                'project': 'awoo',
            })

        assert resp.status_code == 201

    end = datetime.datetime.now()

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

    # at least a 10min resolution
    assert (dstart - start) < datetime.timedelta(seconds=600)
    assert (dend - end) < datetime.timedelta(seconds=600)
